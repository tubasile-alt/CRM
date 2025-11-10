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
    
    def validate_room_conflict(self, room_id, scheduled_date, scheduled_time, duration_minutes, surgery_id=None):
        """
        Valida se há conflito de horário em uma sala
        
        Args:
            room_id: ID da sala
            scheduled_date: Data da cirurgia
            scheduled_time: Horário de início
            duration_minutes: Duração em minutos
            surgery_id: ID da cirurgia (para edição)
            
        Returns:
            tuple: (bool, str) - (is_valid, error_message)
        """
        # Calcular horário de fim
        start_datetime = datetime.combine(scheduled_date, scheduled_time)
        end_datetime = start_datetime + timedelta(minutes=duration_minutes)
        
        # Buscar cirurgias na mesma sala e data
        query = Surgery.query.filter_by(
            room_id=room_id
        ).filter(
            Surgery.scheduled_date == scheduled_date
        )
        
        # Excluir a própria cirurgia se estiver editando
        if surgery_id:
            query = query.filter(Surgery.id != surgery_id)
        
        existing_surgeries = query.all()
        
        for surgery in existing_surgeries:
            existing_start = datetime.combine(surgery.scheduled_date, surgery.scheduled_time)
            existing_end = existing_start + timedelta(minutes=surgery.duration_minutes)
            
            # Verificar sobreposição
            if (start_datetime < existing_end and end_datetime > existing_start):
                return False, f"Conflito com cirurgia agendada às {surgery.scheduled_time.strftime('%H:%M')} ({surgery.patient_name})"
        
        return True, ""
    
    def create_surgery(self, doctor_id, patient_name, procedure_type, room_id, 
                      scheduled_date, scheduled_time, duration_minutes, notes=None):
        """
        Cria uma nova cirurgia
        
        Args:
            doctor_id: ID do médico
            patient_name: Nome do paciente
            procedure_type: Tipo de procedimento
            room_id: ID da sala
            scheduled_date: Data
            scheduled_time: Horário
            duration_minutes: Duração
            notes: Observações
            
        Returns:
            Surgery: Cirurgia criada
        """
        # Validar conflito
        is_valid, error_msg = self.validate_room_conflict(
            room_id, scheduled_date, scheduled_time, duration_minutes
        )
        
        if not is_valid:
            raise ValueError(error_msg)
        
        surgery = Surgery(
            doctor_id=doctor_id,
            patient_name=patient_name,
            procedure_type=procedure_type,
            room_id=room_id,
            scheduled_date=scheduled_date,
            scheduled_time=scheduled_time,
            duration_minutes=duration_minutes,
            notes=notes,
            status='agendada'
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
        
        # Se alterou sala, data ou horário, validar conflito
        if any(k in kwargs for k in ['room_id', 'scheduled_date', 'scheduled_time', 'duration_minutes']):
            room_id = kwargs.get('room_id', surgery.room_id)
            scheduled_date = kwargs.get('scheduled_date', surgery.scheduled_date)
            scheduled_time = kwargs.get('scheduled_time', surgery.scheduled_time)
            duration = kwargs.get('duration_minutes', surgery.duration_minutes)
            
            is_valid, error_msg = self.validate_room_conflict(
                room_id, scheduled_date, scheduled_time, duration, surgery_id
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
            Surgery.scheduled_date >= week_start_date,
            Surgery.scheduled_date <= week_end
        ).order_by(Surgery.scheduled_date, Surgery.scheduled_time).all()
        
        rooms = OperatingRoom.query.order_by(OperatingRoom.name).all()
        
        # Organizar por sala e data
        map_data = {}
        for room in rooms:
            map_data[room.id] = {
                'room': room,
                'surgeries': []
            }
        
        for surgery in surgeries:
            if surgery.room_id in map_data:
                map_data[surgery.room_id]['surgeries'].append(surgery)
        
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
            query = query.filter(Surgery.scheduled_date >= start_date)
        if end_date:
            query = query.filter(Surgery.scheduled_date <= end_date)
        
        return query.order_by(Surgery.scheduled_date, Surgery.scheduled_time).all()
