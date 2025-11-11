"""
Serviço de gerenciamento de cirurgias e mapa cirúrgico
"""
from datetime import datetime, time, timedelta
from models import db, Surgery, OperatingRoom, User
import pytz

class SurgeryService:
    """Serviço para gerenciar cirurgias"""
    
    def __init__(self):
        self.tz = pytz.timezone('America/Sao_Paulo')
    
    def _calculate_duration_minutes(self, start_time, end_time):
        """
        Calcula duração em minutos entre dois horários
        
        Args:
            start_time: Horário de início (time)
            end_time: Horário de término (time)
            
        Returns:
            int: Duração em minutos
        """
        start_dt = datetime.combine(datetime.today(), start_time)
        end_dt = datetime.combine(datetime.today(), end_time)
        return int((end_dt - start_dt).total_seconds() / 60)
    
    def _calculate_end_time(self, start_time, duration_minutes):
        """
        Calcula horário de término a partir do início e duração
        
        Args:
            start_time: Horário de início (time)
            duration_minutes: Duração em minutos
            
        Returns:
            time: Horário de término
        """
        start_dt = datetime.combine(datetime.today(), start_time)
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        return end_dt.time()
    
    def validate_room_conflict(self, operating_room_id, date, start_time, end_time, surgery_id=None):
        """
        Valida se há conflito de horário em uma sala
        
        Args:
            operating_room_id: ID da sala
            date: Data da cirurgia
            start_time: Horário de início
            end_time: Horário de término
            surgery_id: ID da cirurgia (para edição)
            
        Returns:
            tuple: (bool, str) - (is_valid, error_message)
        """
        # Buscar cirurgias na mesma sala e data
        query = Surgery.query.filter_by(
            operating_room_id=operating_room_id
        ).filter(
            Surgery.date == date
        )
        
        # Excluir a própria cirurgia se estiver editando
        if surgery_id:
            query = query.filter(Surgery.id != surgery_id)
        
        existing_surgeries = query.all()
        
        start_datetime = datetime.combine(date, start_time)
        end_datetime = datetime.combine(date, end_time)
        
        for surgery in existing_surgeries:
            existing_start = datetime.combine(surgery.date, surgery.start_time)
            existing_end = datetime.combine(surgery.date, surgery.end_time)
            
            # Verificar sobreposição
            if (start_datetime < existing_end and end_datetime > existing_start):
                return False, f"Conflito com cirurgia agendada às {surgery.start_time.strftime('%H:%M')} ({surgery.patient_name})"
        
        return True, ""
    
    def create_surgery(self, doctor_id, patient_name, procedure_name, operating_room_id, 
                      date, start_time, end_time=None, duration_minutes=None, notes=None, created_by=None):
        """
        Cria uma nova cirurgia
        
        Args:
            doctor_id: ID do médico
            patient_name: Nome do paciente
            procedure_name: Nome do procedimento
            operating_room_id: ID da sala
            date: Data
            start_time: Horário de início
            end_time: Horário de término (opcional se duration_minutes fornecido)
            duration_minutes: Duração em minutos (opcional se end_time fornecido)
            notes: Observações
            created_by: ID do usuário que criou
            
        Returns:
            Surgery: Cirurgia criada
        """
        # Calcular end_time se não fornecido
        if end_time is None:
            if duration_minutes is None:
                raise ValueError("Forneça end_time ou duration_minutes")
            end_time = self._calculate_end_time(start_time, duration_minutes)
        
        # Validar conflito
        is_valid, error_msg = self.validate_room_conflict(
            operating_room_id, date, start_time, end_time
        )
        
        if not is_valid:
            raise ValueError(error_msg)
        
        surgery = Surgery(
            doctor_id=doctor_id,
            patient_name=patient_name,
            procedure_name=procedure_name,
            operating_room_id=operating_room_id,
            date=date,
            start_time=start_time,
            end_time=end_time,
            notes=notes,
            status='agendada',
            created_by=created_by or doctor_id
        )
        
        db.session.add(surgery)
        db.session.commit()
        
        return surgery
    
    def update_surgery(self, surgery_id, **kwargs):
        """
        Atualiza uma cirurgia
        
        Args:
            surgery_id: ID da cirurgia
            **kwargs: Campos a atualizar
            
        Returns:
            Surgery: Cirurgia atualizada
        """
        surgery = Surgery.query.get(surgery_id)
        if not surgery:
            raise ValueError("Cirurgia não encontrada")
        
        # Normalizar payload: se duration_minutes for enviado, calcular end_time
        if 'duration_minutes' in kwargs and 'end_time' not in kwargs:
            start_time = kwargs.get('start_time', surgery.start_time)
            kwargs['end_time'] = self._calculate_end_time(start_time, kwargs.pop('duration_minutes'))
        
        # Se alterou sala, data ou horário, validar conflito
        if any(k in kwargs for k in ['operating_room_id', 'date', 'start_time', 'end_time']):
            operating_room_id = kwargs.get('operating_room_id', surgery.operating_room_id)
            date = kwargs.get('date', surgery.date)
            start_time = kwargs.get('start_time', surgery.start_time)
            end_time = kwargs.get('end_time', surgery.end_time)
            
            is_valid, error_msg = self.validate_room_conflict(
                operating_room_id, date, start_time, end_time, surgery_id
            )
            
            if not is_valid:
                raise ValueError(error_msg)
        
        # Atualizar campos
        for key, value in kwargs.items():
            if hasattr(surgery, key):
                setattr(surgery, key, value)
        
        db.session.commit()
        return surgery
    
    def delete_surgery(self, surgery_id):
        """Deleta uma cirurgia"""
        surgery = Surgery.query.get(surgery_id)
        if not surgery:
            raise ValueError("Cirurgia não encontrada")
        
        db.session.delete(surgery)
        db.session.commit()
        return True
    
    def get_weekly_map(self, week_start_date):
        """
        Retorna mapa cirúrgico de uma semana
        
        Args:
            week_start_date: Data de início da semana (segunda-feira)
            
        Returns:
            dict: Mapa cirúrgico organizado
        """
        week_end = week_start_date + timedelta(days=6)
        
        surgeries = Surgery.query.filter(
            Surgery.date >= week_start_date,
            Surgery.date <= week_end
        ).order_by(Surgery.date, Surgery.start_time).all()
        
        rooms = OperatingRoom.query.order_by(OperatingRoom.name).all()
        
        # Organizar por sala e data
        map_data = {}
        for room in rooms:
            map_data[room.id] = {
                'room': room,
                'surgeries': []
            }
        
        for surgery in surgeries:
            if surgery.operating_room_id in map_data:
                map_data[surgery.operating_room_id]['surgeries'].append(surgery)
        
        return {
            'week_start': week_start_date,
            'week_end': week_end,
            'rooms': map_data,
            'all_surgeries': surgeries
        }
    
    def get_doctor_surgeries(self, doctor_id, start_date=None, end_date=None):
        """Retorna cirurgias de um médico"""
        query = Surgery.query.filter_by(doctor_id=doctor_id)
        
        if start_date:
            query = query.filter(Surgery.date >= start_date)
        if end_date:
            query = query.filter(Surgery.date <= end_date)
        
        return query.order_by(Surgery.date, Surgery.start_time).all()
