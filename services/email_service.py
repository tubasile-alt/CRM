"""
Serviço de envio de emails
"""
from flask import current_app
from flask_mail import Message, Mail

class EmailService:
    """Serviço para envio de emails"""
    
    def __init__(self, mail: Mail):
        self.mail = mail
    
    def send_report(self, recipient, subject, body, attachment=None, filename=None):
        """
        Envia relatório por email
        
        Args:
            recipient: Email do destinatário
            subject: Assunto do email
            body: Corpo do email (texto ou HTML)
            attachment: Arquivo anexo (BytesIO)
            filename: Nome do arquivo anexo
            
        Returns:
            bool: True se enviado com sucesso
        """
        try:
            msg = Message(
                subject=subject,
                recipients=[recipient],
                body=body if not body.startswith('<') else None,
                html=body if body.startswith('<') else None
            )
            
            if attachment and filename:
                attachment.seek(0)
                msg.attach(filename, 'application/octet-stream', attachment.read())
            
            self.mail.send(msg)
            return True
            
        except Exception as e:
            current_app.logger.error(f"Erro ao enviar email: {str(e)}")
            return False
    
    def send_agenda_report(self, recipient, pdf_buffer=None, excel_buffer=None, date_range=None, doctor_name=""):
        """Envia relatório de agenda por email"""
        period = f"{date_range[0].strftime('%d/%m/%Y')} a {date_range[1].strftime('%d/%m/%Y')}" if date_range else ""
        
        subject = f"Agenda Médica - {doctor_name} - {period}"
        body = f"""
        <html>
        <body>
            <h2>Relatório de Agenda Médica</h2>
            <p><strong>Médico:</strong> {doctor_name}</p>
            <p><strong>Período:</strong> {period}</p>
            <p>Em anexo você encontra o(s) relatório(s) solicitado(s).</p>
            <br>
            <p>Atenciosamente,<br>Clínica Basile - Sistema CRM</p>
        </body>
        </html>
        """
        
        msg = Message(
            subject=subject,
            recipients=[recipient],
            html=body
        )
        
        if pdf_buffer:
            pdf_buffer.seek(0)
            msg.attach(f"agenda_{date_range[0].strftime('%Y%m%d')}.pdf", 
                      'application/pdf', pdf_buffer.read())
        
        if excel_buffer:
            excel_buffer.seek(0)
            msg.attach(f"agenda_{date_range[0].strftime('%Y%m%d')}.xlsx", 
                      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                      excel_buffer.read())
        
        try:
            self.mail.send(msg)
            return True
        except Exception as e:
            current_app.logger.error(f"Erro ao enviar email: {str(e)}")
            return False
    
    def send_surgical_map_report(self, recipient, pdf_buffer=None, excel_buffer=None, week_start=None):
        """Envia mapa cirúrgico por email"""
        from datetime import timedelta
        
        week_end = week_start + timedelta(days=6) if week_start else None
        period = f"{week_start.strftime('%d/%m/%Y')} a {week_end.strftime('%d/%m/%Y')}" if week_start else ""
        
        subject = f"Mapa Cirúrgico Semanal - {period}"
        body = f"""
        <html>
        <body>
            <h2>Mapa Cirúrgico Semanal</h2>
            <p><strong>Semana:</strong> {period}</p>
            <p>Em anexo você encontra o(s) mapa(s) cirúrgico(s) solicitado(s).</p>
            <br>
            <p>Atenciosamente,<br>Clínica Basile - Sistema CRM</p>
        </body>
        </html>
        """
        
        msg = Message(
            subject=subject,
            recipients=[recipient],
            html=body
        )
        
        if pdf_buffer:
            pdf_buffer.seek(0)
            msg.attach(f"mapa_cirurgico_{week_start.strftime('%Y%m%d')}.pdf",
                      'application/pdf', pdf_buffer.read())
        
        if excel_buffer:
            excel_buffer.seek(0)
            msg.attach(f"mapa_cirurgico_{week_start.strftime('%Y%m%d')}.xlsx",
                      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                      excel_buffer.read())
        
        try:
            self.mail.send(msg)
            return True
        except Exception as e:
            current_app.logger.error(f"Erro ao enviar email: {str(e)}")
            return False
