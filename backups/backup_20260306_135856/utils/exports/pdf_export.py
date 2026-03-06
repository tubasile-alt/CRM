"""
Exportação de relatórios para PDF usando ReportLab
"""
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
from io import BytesIO

class PDFExporter:
    """Exportador de relatórios PDF"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#0d6efd'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
    
    def export_agenda(self, appointments, date_range, doctor_name):
        """
        Exporta agenda para PDF
        
        Args:
            appointments: Lista de agendamentos
            date_range: Tupla (data_inicio, data_fim)
            doctor_name: Nome do médico
            
        Returns:
            BytesIO: PDF gerado
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        # Título
        title = f"Agenda Médica - {doctor_name}"
        elements.append(Paragraph(title, self.title_style))
        
        # Período
        period_text = f"Período: {date_range[0].strftime('%d/%m/%Y')} a {date_range[1].strftime('%d/%m/%Y')}"
        elements.append(Paragraph(period_text, self.styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Tabela de agendamentos
        data = [['Data/Hora', 'Paciente', 'Status', 'Sala', 'Observações']]
        
        for apt in appointments:
            data.append([
                apt.start_time.strftime('%d/%m %H:%M'),
                apt.patient.name,
                self._translate_status(apt.status),
                apt.room or '-',
                apt.notes[:50] + '...' if apt.notes and len(apt.notes) > 50 else (apt.notes or '-')
            ])
        
        table = Table(data, colWidths=[3*cm, 5*cm, 3*cm, 2.5*cm, 5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(table)
        
        # Rodapé
        elements.append(Spacer(1, 30))
        footer = f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        elements.append(Paragraph(footer, self.styles['Normal']))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def export_surgical_map(self, surgeries, week_start, rooms):
        """
        Exporta mapa cirúrgico semanal para PDF
        
        Args:
            surgeries: Lista de cirurgias
            week_start: Data de início da semana
            rooms: Lista de salas
            
        Returns:
            BytesIO: PDF gerado
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
        elements = []
        
        # Título
        week_end = week_start + timedelta(days=6)
        title = f"Mapa Cirúrgico Semanal"
        elements.append(Paragraph(title, self.title_style))
        
        period_text = f"Semana de {week_start.strftime('%d/%m/%Y')} a {week_end.strftime('%d/%m/%Y')}"
        elements.append(Paragraph(period_text, self.styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Tabela por sala
        for room in rooms:
            room_surgeries = [s for s in surgeries if s.room_id == room.id]
            
            if room_surgeries:
                elements.append(Paragraph(f"<b>{room.name}</b>", self.styles['Heading2']))
                elements.append(Spacer(1, 10))
                
                data = [['Data', 'Hora', 'Médico', 'Paciente', 'Procedimento', 'Duração']]
                
                for surgery in sorted(room_surgeries, key=lambda x: x.scheduled_date):
                    data.append([
                        surgery.scheduled_date.strftime('%d/%m/%Y'),
                        surgery.scheduled_time.strftime('%H:%M'),
                        surgery.doctor.name,
                        surgery.patient_name,
                        surgery.procedure_type,
                        f"{surgery.duration_minutes} min"
                    ])
                
                table = Table(data, colWidths=[3*cm, 2.5*cm, 5*cm, 5*cm, 5*cm, 2.5*cm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#198754')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                ]))
                
                elements.append(table)
                elements.append(Spacer(1, 20))
        
        # Rodapé
        footer = f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        elements.append(Paragraph(footer, self.styles['Normal']))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def _translate_status(self, status):
        """Traduz status de agendamento"""
        translations = {
            'agendado': 'Agendado',
            'confirmado': 'Confirmado',
            'atendido': 'Atendido',
            'faltou': 'Faltou',
            'cancelado': 'Cancelado'
        }
        return translations.get(status, status.capitalize())
