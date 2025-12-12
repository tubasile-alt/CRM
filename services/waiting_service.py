"""
Serviço de gerenciamento de espera de pacientes
"""
from datetime import datetime
from models import db, Appointment
import pytz

class WaitingService:
    """Serviço para gerenciar lista de espera"""
    
    def __init__(self):
        self.tz = pytz.timezone('America/Sao_Paulo')
    
    def check_in(self, appointment_id):
        """
        Realiza check-in de um paciente
        
        Args:
            appointment_id: ID do agendamento
            
        Returns:
            dict: Dados do check-in
        """
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            raise ValueError("Agendamento não encontrado")
        
        if appointment.checked_in_time:
            raise ValueError("Paciente já realizou check-in")
        
        now = datetime.now(self.tz)
        appointment.checked_in_time = now
        appointment.waiting = True
        
        db.session.commit()
        
        return {
            'id': appointment.id,
            'patient_name': appointment.patient.name,
            'checked_in_time': now.strftime('%H:%M'),
            'scheduled_time': appointment.start_time.strftime('%H:%M'),
            'waiting': True
        }
    
    def check_out(self, appointment_id):
        """
        Realiza check-out de um paciente (saiu da espera)
        
        Args:
            appointment_id: ID do agendamento
            
        Returns:
            dict: Dados do check-out
        """
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            raise ValueError("Agendamento não encontrado")
        
        appointment.waiting = False
        appointment.status = 'atendido'
        
        # Calcular tempo de espera e registrar
        wait_time = None
        if appointment.checked_in_time:
            delta = datetime.now(self.tz) - appointment.checked_in_time
            wait_time = int(delta.total_seconds() / 60)  # minutos
            appointment.total_waiting_minutes = wait_time
        
        db.session.commit()
        
        return {
            'id': appointment.id,
            'patient_name': appointment.patient.name,
            'wait_time_minutes': wait_time,
            'waiting': False
        }
    
    def get_waiting_list(self, doctor_id=None, date=None):
        """
        Retorna lista de pacientes em espera
        
        Args:
            doctor_id: ID do médico (opcional)
            date: Data específica (opcional, padrão: hoje)
            
        Returns:
            list: Lista de pacientes em espera
        """
        query = Appointment.query.filter_by(waiting=True)
        
        if doctor_id:
            query = query.filter_by(doctor_id=doctor_id)
        
        if date:
            query = query.filter(db.func.date(Appointment.start_time) == date)
        else:
            today = datetime.now(self.tz).date()
            query = query.filter(db.func.date(Appointment.start_time) == today)
        
        appointments = query.order_by(Appointment.checked_in_time).all()
        
        waiting_list = []
        for apt in appointments:
            wait_time = None
            checked_in_iso = None
            if apt.checked_in_time:
                # Converter para timezone-aware se for naive
                checkin_time = apt.checked_in_time
                if checkin_time.tzinfo is None:
                    checkin_time = self.tz.localize(checkin_time)
                
                current_time = datetime.now(self.tz)
                delta = current_time - checkin_time
                wait_time = int(delta.total_seconds() / 60)
                checked_in_iso = checkin_time.isoformat()
            
            waiting_list.append({
                'id': apt.id,
                'patient_id': apt.patient_id,
                'patient_name': apt.patient.name,
                'appointment_type': apt.appointment_type or 'Consulta',
                'scheduled_time': apt.start_time.strftime('%H:%M'),
                'checked_in_time': checked_in_iso,
                'wait_time_minutes': wait_time,
                'room': apt.room
            })
        
        return waiting_list
    
    def get_average_wait_time(self, doctor_id=None, days=30):
        """
        Calcula tempo médio de espera
        
        Args:
            doctor_id: ID do médico (opcional)
            days: Número de dias a considerar
            
        Returns:
            dict: Estatísticas de espera
        """
        from datetime import timedelta
        
        query = Appointment.query.filter(
            Appointment.total_waiting_minutes.isnot(None),
            Appointment.status == 'atendido'
        )
        
        if doctor_id:
            query = query.filter_by(doctor_id=doctor_id)
        
        # Últimos X dias
        cutoff_date = datetime.now(self.tz) - timedelta(days=days)
        query = query.filter(Appointment.created_at >= cutoff_date)
        
        appointments = query.all()
        
        if not appointments:
            return {
                'average': 0,
                'total': 0,
                'min': 0,
                'max': 0,
                'count': 0
            }
        
        times = [apt.total_waiting_minutes for apt in appointments]
        avg = sum(times) / len(times)
        
        return {
            'average': round(avg, 1),
            'total': sum(times),
            'min': min(times),
            'max': max(times),
            'count': len(times)
        }
    
    def get_wait_stats(self, doctor_id=None, date=None):
        """
        Retorna estatísticas de espera
        
        Args:
            doctor_id: ID do médico (opcional)
            date: Data específica (opcional)
            
        Returns:
            dict: Estatísticas de espera
        """
        waiting_list = self.get_waiting_list(doctor_id, date)
        
        if not waiting_list:
            return {
                'count': 0,
                'average_wait_minutes': 0,
                'max_wait_minutes': 0,
                'min_wait_minutes': 0
            }
        
        wait_times = [p['wait_time_minutes'] for p in waiting_list if p['wait_time_minutes'] is not None]
        
        return {
            'count': len(waiting_list),
            'average_wait_minutes': int(sum(wait_times) / len(wait_times)) if wait_times else 0,
            'max_wait_minutes': max(wait_times) if wait_times else 0,
            'min_wait_minutes': min(wait_times) if wait_times else 0
        }
    
    def assign_room(self, appointment_id, room_name):
        """
        Atribui sala a um paciente
        
        Args:
            appointment_id: ID do agendamento
            room_name: Nome da sala
            
        Returns:
            dict: Dados atualizados
        """
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            raise ValueError("Agendamento não encontrado")
        
        appointment.room = room_name
        db.session.commit()
        
        return {
            'id': appointment.id,
            'patient_name': appointment.patient.name,
            'room': room_name
        }
