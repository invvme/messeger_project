from . import db
from flask_login import UserMixin
from datetime import datetime
from zoneinfo import ZoneInfo
from werkzeug.security import check_password_hash, generate_password_hash

chat_members = db.Table(
    'chat_members',
    db.Column('chat_id', db.Integer, db.ForeignKey('chat.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

def moscow_now():
    return datetime.now(ZoneInfo('Europe/Moscow')).replace(tzinfo=None)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    display_name = db.Column(db.String(50), default='')
    avatar = db.Column(db.String(200), default='default.jpg')

    messages = db.relationship('Message', back_populates='user')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_display_name(self):
        return self.display_name or self.username
    


class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_date = db.Column(db.DateTime, default=moscow_now)

    users = db.relationship(
        'User',
        secondary=chat_members,
        backref=db.backref('chats', lazy='dynamic')
    )
    messages = db.relationship(
        'Message',
        back_populates='chat',
        cascade='all, delete-orphan',
        order_by='Message.timestamp'
    )

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    image = db.Column(db.String, nullable=True)
    timestamp = db.Column(db.DateTime, default=moscow_now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)

    user = db.relationship('User', back_populates='messages')
    chat = db.relationship('Chat', back_populates='messages')
