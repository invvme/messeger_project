from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from . import db
from .models import Chat, Message, User
from .find_map import get_map_image

import os
from werkzeug.utils import secure_filename
from flask import current_app

import requests
from io import BytesIO


main = Blueprint('main', __name__)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        if not text:
            return redirect(url_for('main.chat', chat_id=chat.id))

        if text.lower().startswith("покажи на карте "):
            address = text[len("покажи на карте "):].strip()

            if address:
                import uuid
                filename = f"{uuid.uuid4()}.png"
                image_path = get_map_image(address, filename)

                if not image_path:
                    message = Message()
                    message.text = "Не удалось получить карту."
                    message.user = current_user
                    message.chat = chat
                    db.session.add(message)
                    db.session.commit()
                    return redirect(url_for('main.chat', chat_id=chat.id))
                
                message = Message()
                message.text = f"Карта: {address}"
                message.image = image_path
                message.user = current_user
                message.chat = chat

                db.session.add(message)
                db.session.commit()

            return redirect(url_for('main.chat', chat_id=chat.id))
        
        else:
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


@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        new_name = request.form.get('display_name', '').strip()
        if new_name:
            current_user.display_name = new_name
            db.session.commit()
            return redirect(url_for('main.profile'))

        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename != '':
                if allowed_file(file.filename):
                    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'avatars')
                    filename = secure_filename(file.filename)

                    unique_name = f"{current_user.id}_{filename}"
                    file.save(os.path.join(upload_folder, unique_name))

                    current_user.avatar = unique_name
                    db.session.commit()
                    return redirect(url_for('main.profile'))

        return render_template('profile.html', title='Профиль', message='Некорректный файл')
    return render_template('profile.html', title='Профиль')
