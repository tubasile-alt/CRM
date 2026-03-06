"""
Gerador de orçamentos cosméticos em PDF
"""
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime

class BudgetExporter:
    """Exportador de orçamentos cosméticos para PDF"""
    
    def generate_budget(self, procedures, patient_name, doctor_name):
        """
        Gera orçamento em PDF
        
        Args:
            procedures: Lista de dicionários com {name, value}
            patient_name: Nome do paciente
            doctor_name: Nome do médico
            
        Returns:
            BytesIO buffer com o PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0d6efd'),
            spaceAfter=12,
            alignment=TA_CENTER
        )
        
        story.append(Paragraph('CLÍNICA BASILE', title_style))
        story.append(Paragraph('Orçamento de Procedimentos Estéticos', styles['Heading2']))
        story.append(Spacer(1, 0.3*inch))
        
        # Informações do paciente
        info_style = styles['Normal']
        story.append(Paragraph(f'<b>Paciente:</b> {patient_name}', info_style))
        story.append(Paragraph(f'<b>Médico:</b> {doctor_name}', info_style))
        story.append(Paragraph(f'<b>Data:</b> {datetime.now().strftime("%d/%m/%Y")}', info_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Tabela de procedimentos
        data = [['Procedimento', 'Valor (R$)']]
        total = 0
        
        for proc in procedures:
            value = float(proc['value']) if proc['value'] else 0
            total += value
            data.append([
                proc['name'],
                f'R$ {value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
            ])
        
        # Linha de total
        data.append(['', ''])
        data.append([
            Paragraph('<b>TOTAL ESTIMADO</b>', styles['Normal']),
            Paragraph(f'<b>R$ {total:,.2f}</b>'.replace(',', 'X').replace('.', ',').replace('X', '.'), styles['Normal'])
        ])
        
        # Estilo da tabela
        table = Table(data, colWidths=[4*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -3), colors.beige),
            ('GRID', (0, 0), (-1, -3), 1, colors.black),
            ('LINEABOVE', (0, -2), (-1, -2), 2, colors.black),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.5*inch))
        
        # Observações
        obs_style = ParagraphStyle(
            'Observation',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey
        )
        story.append(Paragraph(
            '<i>Observações:</i><br/>'
            '• Este orçamento tem validade de 30 dias.<br/>'
            '• Os valores podem sofrer alterações conforme avaliação médica.<br/>'
            '• O agendamento do procedimento está sujeito à disponibilidade.',
            obs_style
        ))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
