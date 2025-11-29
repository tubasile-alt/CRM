from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz

db = SQLAlchemy()

def get_brazil_time():
    tz = pytz.timezone('America/Sao_Paulo')
    return datetime.now(tz)

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    specialty = db.Column(db.String(50))  # 'dermatologista' ou 'cirurgiao_plastico'
    created_at = db.Column(db.DateTime, default=get_brazil_time)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_doctor(self):
        return self.role == 'medico'
    
    def is_secretary(self):
        return self.role == 'secretaria'

class Patient(db.Model):
    __tablename__ = 'patient'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    birth_date = db.Column(db.Date)
    cpf = db.Column(db.String(14))
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    mother_name = db.Column(db.String(100))
    indication_source = db.Column(db.String(100))
    occupation = db.Column(db.String(100))
    patient_type = db.Column(db.String(50), default='particular')
    attention_note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=get_brazil_time)
    
    appointments = db.relationship('Appointment', backref='patient', lazy=True, cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='patient', lazy=True, cascade='all, delete-orphan')
    tags = db.relationship('PatientTag', backref='patient', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class PatientDoctor(db.Model):
    __tablename__ = 'patient_doctor'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    patient_code = db.Column(db.Integer, nullable=False)  # Código crescente por médico
    created_at = db.Column(db.DateTime, default=get_brazil_time)
    
    __table_args__ = (
        db.UniqueConstraint('patient_id', 'doctor_id', name='unique_patient_doctor'),
        db.Index('idx_doctor_code', 'doctor_id', 'patient_code'),
    )
    
    patient = db.relationship('Patient', backref='doctor_codes')
    doctor = db.relationship('User', backref='patient_codes')

class Appointment(db.Model):
    __tablename__ = 'appointment'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='agendado')
    appointment_type = db.Column(db.String(20), default='Particular')
    notes = db.Column(db.Text)
    waiting = db.Column(db.Boolean, default=False)
    checked_in_time = db.Column(db.DateTime)
    room = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=get_brazil_time)
    
    doctor = db.relationship('User', backref='appointments')

class Note(db.Model):
    __tablename__ = 'note'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=True)  # Chave de agrupamento
    note_type = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50))  # 'patologia', 'cosmiatria', 'transplante_capilar'
    content = db.Column(db.Text)
    consultation_duration = db.Column(db.Integer)
    transplant_indication = db.Column(db.String(10), default='nao')  # 'sim' ou 'nao'
    surgical_planning = db.Column(db.Text)  # JSON com planejamento cirúrgico
    created_at = db.Column(db.DateTime, default=get_brazil_time)
    
    __table_args__ = (
        db.Index('idx_note_patient_appt_type', 'patient_id', 'appointment_id', 'note_type'),
    )
    
    doctor = db.relationship('User', backref='notes')
    appointment = db.relationship('Appointment', backref='consultation_notes')
    indications = db.relationship('Indication', backref='note', lazy=True, cascade='all, delete-orphan')
    cosmetic_plans = db.relationship('CosmeticProcedurePlan', backref='note', lazy=True, cascade='all, delete-orphan')
    hair_transplants = db.relationship('HairTransplant', backref='note', lazy=True, cascade='all, delete-orphan')

class Procedure(db.Model):
    __tablename__ = 'procedure'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=get_brazil_time)

class Indication(db.Model):
    __tablename__ = 'indication'
    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'), nullable=False)
    procedure_id = db.Column(db.Integer, db.ForeignKey('procedure.id'), nullable=False)
    indicated = db.Column(db.Boolean, default=False)
    performed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=get_brazil_time)
    
    procedure = db.relationship('Procedure', backref='indications')

class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(7), default='#6c757d')
    created_at = db.Column(db.DateTime, default=get_brazil_time)

class PatientTag(db.Model):
    __tablename__ = 'patient_tag'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=get_brazil_time)
    
    tag = db.relationship('Tag', backref='patient_tags')

class ChatMessage(db.Model):
    __tablename__ = 'chat_message'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=get_brazil_time)
    read = db.Column(db.Boolean, default=False)
    
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')
    reads = db.relationship('MessageRead', backref='message', cascade='all, delete-orphan')

class MessageRead(db.Model):
    __tablename__ = 'message_read'
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('chat_message.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    read_at = db.Column(db.DateTime, default=get_brazil_time)
    
    user = db.relationship('User')
    
    __table_args__ = (
        db.UniqueConstraint('message_id', 'user_id', name='_message_user_uc'),
        db.Index('idx_message_user', 'message_id', 'user_id')
    )

class OperatingRoom(db.Model):
    __tablename__ = 'operating_room'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    capacity = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=get_brazil_time)
    
    surgeries = db.relationship('Surgery', backref='room', lazy=True)

class Surgery(db.Model):
    __tablename__ = 'surgery'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time, nullable=False, index=True)
    end_time = db.Column(db.Time, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    patient_name = db.Column(db.String(100), nullable=False)
    procedure_id = db.Column(db.Integer, db.ForeignKey('procedure.id'))
    procedure_name = db.Column(db.String(200), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    operating_room_id = db.Column(db.Integer, db.ForeignKey('operating_room.id'), nullable=False, index=True)
    status = db.Column(db.String(20), default='agendada')
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=get_brazil_time)
    updated_at = db.Column(db.DateTime, default=get_brazil_time, onupdate=get_brazil_time)
    
    patient = db.relationship('Patient', backref='surgeries')
    procedure = db.relationship('Procedure', backref='surgeries')
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='doctor_surgeries')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_surgeries')
    updater = db.relationship('User', foreign_keys=[updated_by], backref='updated_surgeries')

class DoctorPreference(db.Model):
    __tablename__ = 'doctor_preference'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    color = db.Column(db.String(7), default='#0d6efd')
    layer_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=get_brazil_time)
    
    user = db.relationship('User', backref='preference', uselist=False)

# Modelos para Cosmiatria
class CosmeticProcedurePlan(db.Model):
    __tablename__ = 'cosmetic_procedure_plan'
    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'), nullable=False)
    procedure_name = db.Column(db.String(100), nullable=False)  # Botox, Sculptra, Morpheus, etc
    planned_value = db.Column(db.Numeric(10, 2))  # Valor planejado (precisão decimal para valores monetários)
    final_budget = db.Column(db.Numeric(10, 2))  # Orçamento final ajustado
    was_performed = db.Column(db.Boolean, default=False)  # Se foi realizado
    performed_date = db.Column(db.DateTime)  # Data de realização
    follow_up_months = db.Column(db.Integer)  # Intervalo de retorno em meses
    observations = db.Column(db.Text)  # Observações sobre o procedimento
    created_at = db.Column(db.DateTime, default=get_brazil_time)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# Modelos para Transplante Capilar
class HairTransplant(db.Model):
    __tablename__ = 'hair_transplant'
    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'), nullable=False)
    norwood_classification = db.Column(db.String(20))  # 1, 2, 3, 4, 5, 6
    previous_transplant = db.Column(db.String(10))  # 'sim' ou 'nao'
    transplant_location = db.Column(db.String(50))  # 'ICB' ou 'outro_servico'
    case_type = db.Column(db.String(50))  # 'primaria' ou 'secundaria'
    number_of_surgeries = db.Column(db.Integer, default=1)  # 1 ou 2 cirurgias planejadas
    body_hair_needed = db.Column(db.Boolean, default=False)
    eyebrow_transplant = db.Column(db.Boolean, default=False)
    beard_transplant = db.Column(db.Boolean, default=False)
    
    # Indicações cirúrgicas (múltipla seleção via checkboxes separados)
    frontal_transplant = db.Column(db.Boolean, default=False)
    crown_transplant = db.Column(db.Boolean, default=False)
    complete_transplant = db.Column(db.Boolean, default=False)
    complete_with_body_hair = db.Column(db.Boolean, default=False)
    
    # Planejamento cirúrgico (texto livre)
    surgical_planning = db.Column(db.Text)
    
    # Conduta (texto com padrão editável)
    clinical_conduct = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=get_brazil_time)
    
    images = db.relationship('TransplantImage', backref='transplant', lazy=True, cascade='all, delete-orphan')

class TransplantImage(db.Model):
    __tablename__ = 'transplant_image'
    id = db.Column(db.Integer, primary_key=True)
    hair_transplant_id = db.Column(db.Integer, db.ForeignKey('hair_transplant.id'), nullable=False)
    image_type = db.Column(db.String(50), nullable=False)  # 'consultation_photo', 'surgical_plan', 'simulation'
    file_path = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=get_brazil_time)

class TransplantSurgery(db.Model):
    __tablename__ = 'transplant_surgery'
    id = db.Column(db.Integer, primary_key=True)
    hair_transplant_id = db.Column(db.Integer, db.ForeignKey('hair_transplant.id'), nullable=False)
    surgery_date = db.Column(db.DateTime, nullable=False)
    surgical_planning = db.Column(db.Text)  # Planejamento cirúrgico detalhado
    complications = db.Column(db.Text)  # Intercorrências
    created_at = db.Column(db.DateTime, default=get_brazil_time)
    
    hair_transplant = db.relationship('HairTransplant', backref=db.backref('surgeries', cascade='all, delete-orphan'))

# Modelo para lembretes automáticos do CRM
class FollowUpReminder(db.Model):
    __tablename__ = 'follow_up_reminder'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    procedure_name = db.Column(db.String(100), nullable=False)
    scheduled_date = db.Column(db.Date, nullable=False, index=True)
    reminder_type = db.Column(db.String(50))  # 'cosmetic_follow_up', 'transplant_revision'
    status = db.Column(db.String(20), default='pending')  # 'pending', 'contacted', 'scheduled', 'completed'
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=get_brazil_time)
    
    patient = db.relationship('Patient', backref='reminders')

class Evolution(db.Model):
    __tablename__ = 'evolution'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    evolution_date = db.Column(db.DateTime, default=get_brazil_time, nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=get_brazil_time, index=True)
    
    patient = db.relationship('Patient', backref='evolutions')
    doctor = db.relationship('User', backref='evolutions')

class Payment(db.Model):
    __tablename__ = 'payment'
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False, index=True)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # 'dinheiro', 'cartao', 'pix'
    installments = db.Column(db.Integer, default=1)  # para cartão de crédito
    status = db.Column(db.String(20), default='pendente')  # 'pendente', 'pago', 'cancelado'
    procedures = db.Column(db.JSON)  # Array de procedimentos com valores
    consultation_type = db.Column(db.String(50))  # UNIMD, particular, retorno, implante, cortesia
    created_at = db.Column(db.DateTime, default=get_brazil_time, index=True)
    paid_at = db.Column(db.DateTime)
    
    appointment = db.relationship('Appointment', backref='payments')
    patient = db.relationship('Patient', backref='payments')
