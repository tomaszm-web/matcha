from flask import (
	request,
	session)
from datetime import datetime
from .models import Account, Notification, Chat
from flask_socketio import emit
from app import db, socketio

users_in_chat = {}
account = Account(db)
chat = Chat(db)
notification = Notification(db)


@socketio.on('connect', namespace='/private_chat')
def connect_user_to_chat():
	if 'user' in session:
		users_in_chat[str(session['user'])] = request.sid

@socketio.on('private_chat event', namespace='/private_chat')
def send_message(data):
	if 'sender_id' in data and 'recipient_id' in data and 'body' in data:
		data['timestamp'] = datetime.now().strftime('%c')
		chat.send_message(data['sender_id'], data['recipient_id'], data['body'])
		emit('private_chat response', data, room=users_in_chat[data['sender_id']])
		if data['recipient_id'] in users_in_chat:
			emit('private_chat response', data, room=users_in_chat[data['recipient_id']])
		else:
			notification.send(data['recipient_id'], 'message', account.get_user_info(data['sender_id']))


@socketio.on('disconnect', namespace='/private_chat')
def disconnect_user_from_chat():
	if 'user' in session:
		users_in_chat.pop(session['user'], None)


@socketio.on('connect')
def connect_user():
	if 'user' in session:
		last_login_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		sql = "UPDATE `users` SET online = 1, last_login = %s WHERE id = %s"
		db.query(sql, (last_login_date, session['user']))


@socketio.on('disconnect')
def disconnect_user():
	if 'user' in session:
		sql = "UPDATE `users` SET online=0 WHERE id=%s"
		db.query(sql, [session['user']])
		session.pop("user", None)
