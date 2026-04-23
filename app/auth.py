from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from . import db
from .models import User

auth = Blueprint('auth', __name__)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            return render_template('register.html',
                                   title='Регистрация',
                                   message='Заполните все обязательные поля')

        if db.session.query(User).filter(User.username == username).first():
            return render_template('register.html',
                                   title='Регистрация',
                                   message='Такой пользователь уже существует')

        user = User()
        user.username = username
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('main.index'))

    return render_template('register.html', title='Регистрация')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = db.session.query(User).filter(User.username == username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.index'))

        return render_template('login.html',
                               title='Авторизация',
                               message='Неправильный логин или пароль')

    return render_template('login.html', title='Авторизация')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
