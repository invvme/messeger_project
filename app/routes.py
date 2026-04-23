from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from . import db
from .models import Chat, Message, User

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
@login_required
def index():
    param = {}
    param['title'] = 'Главная страница'
    param['users'] = db.session.query(User).filter(User.id != current_user.id).all()
    param['chats'] = current_user.chats.order_by(Chat.created_date.desc()).all()
    return render_template('index.html', **param)

@main.route('/start_chat/<int:user_id>', methods=['POST'])
@login_required
def start_chat(user_id):
    other_user = db.session.get(User, user_id)
    if not other_user:
        abort(404)

    for chat in current_user.chats:
        if current_user in chat.users and other_user in chat.users and len(chat.users) == 2:
            return redirect(url_for('main.chat', chat_id=chat.id))

    chat = Chat()
    chat.users.append(current_user)
    chat.users.append(other_user)
    db.session.add(chat)
    db.session.commit()
    return redirect(url_for('main.chat', chat_id=chat.id))

@main.route('/chat/<int:chat_id>', methods=['GET', 'POST'])
@login_required
def chat(chat_id):
    chat = db.session.get(Chat, chat_id)
    if not chat:
        abort(404)

    if current_user not in chat.users:
        abort(403)

    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        if text:
            message = Message()
            message.text = text
            message.user = current_user
            message.chat = chat
            db.session.add(message)
            db.session.commit()
        return redirect(url_for('main.chat', chat_id=chat.id))

    param = {}
    param['title'] = 'Чат'
    param['chat'] = chat
    param['chats'] = current_user.chats.order_by(Chat.created_date.desc()).all()
    return render_template('chat.html', **param)
