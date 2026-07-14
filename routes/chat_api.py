from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from models import ChatMessage, MessageRead, User, db
from services.clinic_time import format_brazil_datetime, get_brazil_time


chat_api_bp = Blueprint('chat_api', __name__)


@chat_api_bp.route('/api/chat/messages')
@login_required
def get_messages():
    with_user_id = request.args.get('with_user_id', type=int)
    if not with_user_id:
        return jsonify({'error': 'Parâmetro with_user_id é obrigatório'}), 400
    
    messages = ChatMessage.query.filter(
        db.or_(
            db.and_(ChatMessage.sender_id == current_user.id, ChatMessage.recipient_id == with_user_id),
            db.and_(ChatMessage.sender_id == with_user_id, ChatMessage.recipient_id == current_user.id)
        )
    ).order_by(ChatMessage.id.asc()).all()
    
    try:
        return jsonify([{
            'id': msg.id,
            'senderId': msg.sender_id,
            'recipientId': msg.recipient_id,
            'message': msg.message,
            'timestamp': format_brazil_datetime(msg.created_at).split(' ')[1] if msg.created_at else '',
            'read': msg.read if hasattr(msg, 'read') else False
        } for msg in messages])
    except Exception as e:
        print(f'[CHAT ERROR] Serialization failed: {e}')
        return jsonify({'error': 'Internal server error'}), 500


@chat_api_bp.route('/api/chat/send', methods=['POST'])
@login_required
def send_message():
    data = request.get_json(silent=True) or request.form
    if not hasattr(data, 'get'):
        return jsonify({'error': 'Dados inválidos'}), 400
    recipient_id = data.get('recipient_id')
    if not recipient_id:
        return jsonify({'error': 'recipient_id é obrigatório'}), 400

    try:
        recipient_id = int(recipient_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'Destinatário inválido'}), 400

    if recipient_id == current_user.id:
        return jsonify({'error': 'Não é possível enviar mensagem para si mesmo'}), 400
    
    recipient = db.session.get(User, recipient_id)
    if not recipient:
        return jsonify({'error': 'Destinatário não encontrado'}), 404
    
    message_text = str(data.get('message') or '').strip()
    if not message_text:
        return jsonify({'error': 'Mensagem vazia'}), 400
    if len(message_text) > 4000:
        return jsonify({'error': 'Mensagem excede o limite de 4000 caracteres'}), 400

    message_obj = ChatMessage(
        sender_id=current_user.id,
        recipient_id=recipient_id,
        message=message_text,
        created_at=get_brazil_time().replace(tzinfo=None)
    )
    db.session.add(message_obj)
    db.session.commit()
    return jsonify({'success': True, 'id': message_obj.id})


@chat_api_bp.route('/api/chat/mark_read', methods=['POST'])
@login_required
def mark_messages_read():
      data = request.get_json(silent=True) or request.form
      if not hasattr(data, 'get'):
          return jsonify({'success': False, 'error': 'Dados inválidos'}), 400
      from_user_id = data.get('from_user_id')
      if from_user_id:
          try:
              from_user_id = int(from_user_id)
          except (TypeError, ValueError):
              return jsonify({'success': False, 'error': 'Remetente inválido'}), 400
      
      query = db.session.query(ChatMessage.id).filter(ChatMessage.recipient_id == current_user.id)
      if from_user_id:
          query = query.filter(ChatMessage.sender_id == from_user_id)
      
      unread_message_ids = query.outerjoin(
          MessageRead,
          db.and_(MessageRead.message_id == ChatMessage.id, MessageRead.user_id == current_user.id)
      ).filter(MessageRead.id.is_(None)).all()
      
      if not unread_message_ids:
          return jsonify({'success': True, 'count': 0})
      
      read_records = [MessageRead(message_id=msg_id[0], user_id=current_user.id) for msg_id in unread_message_ids]
      try:
          db.session.bulk_save_objects(read_records)
          db.session.commit()
          return jsonify({'success': True, 'count': len(read_records)})
      except Exception as e:
          db.session.rollback()
          return jsonify({'success': False, 'error': str(e)}), 500


@chat_api_bp.route('/api/chat/latest_unread')
@login_required
def get_latest_unread():
      def _chat_display_name(user):
          if not user:
              return "Sistema"

          raw_name = (user.name or '').strip()
          username = (user.username or '').strip().lower()

          # Compatibilidade com base legada: usuário técnico/admin que representa o Dr. Arthur
          if username == 'admin' and (not raw_name or raw_name.lower() == 'admin'):
              return 'Dr. Arthur'

          return raw_name or user.email or user.username or "Sistema"

      subquery = db.session.query(MessageRead.message_id).filter(MessageRead.user_id == current_user.id)
      latest = ChatMessage.query.filter(
          ChatMessage.recipient_id == current_user.id,
          ~ChatMessage.id.in_(subquery)
      ).order_by(ChatMessage.created_at.desc()).first()
      
      if latest:
          return jsonify({
              'id': latest.id,
              'from_user_id': latest.sender_id,
              'from_name': _chat_display_name(latest.sender),
              'message': (latest.message[:80] + ('...' if len(latest.message) > 80 else '')) if latest.message else "",
              'created_at': latest.created_at.isoformat()
          })
      return jsonify({'id': None})


@chat_api_bp.route('/api/chat/unread_count')
@login_required
def get_unread_count():
      from_user_id = request.args.get('from_user_id', type=int)
      query = db.session.query(ChatMessage).filter(ChatMessage.recipient_id == current_user.id)
      if from_user_id:
          query = query.filter(ChatMessage.sender_id == from_user_id)
      
      count = query.outerjoin(
          MessageRead,
          db.and_(MessageRead.message_id == ChatMessage.id, MessageRead.user_id == current_user.id)
      ).filter(MessageRead.id.is_(None)).count()
      return jsonify({'count': count})


@chat_api_bp.route('/api/chat/contacts')
@login_required
def get_chat_contacts():
      def _chat_role_kind(user):
          role = (user.role or '').strip().lower()
          role_clinico = (user.role_clinico or '').strip().upper()

          if role == 'medico' or role_clinico in ('DERM', 'CP'):
              return 'medico'
          if role == 'secretaria' or role_clinico == 'SECRETARY':
              return 'secretaria'
          return None

      def _chat_display_name(user):
          raw_name = (user.name or '').strip()
          username = (user.username or '').strip().lower()

          # Compatibilidade com base legada: usuário técnico/admin que representa o Dr. Arthur
          if username == 'admin' and (not raw_name or raw_name.lower() == 'admin'):
              return 'Dr. Arthur'

          return raw_name or user.email or user.username or 'Usuário'

      users = User.query.filter(User.id != current_user.id).all()
      contacts = []
      for user in users:
          role_kind = _chat_role_kind(user)
          if role_kind is None:
              # Excluir perfis administrativos/técnicos do chat clínico
              continue

          unread_count = db.session.query(ChatMessage).filter(
              ChatMessage.recipient_id == current_user.id,
              ChatMessage.sender_id == user.id
          ).outerjoin(
              MessageRead,
              db.and_(MessageRead.message_id == ChatMessage.id, MessageRead.user_id == current_user.id)
          ).filter(MessageRead.id.is_(None)).count()
          
          contacts.append({
              'id': user.id,
              'name': _chat_display_name(user),
              'role': role_kind,
              'unread_count': unread_count
          })

      contacts.sort(key=lambda c: (0 if c['role'] == 'medico' else 1, c['name'].lower()))
      return jsonify(contacts)
