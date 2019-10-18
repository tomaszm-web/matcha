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
	"""Add key = chat_id"""
	if 'user' in session:
		users_in_chat[str(session['user'])] = request.sid
		print(users_in_chat)


@socketio.on('send_message event', namespace='/private_chat')
def send_message(data):
	try:
		data['timestamp'] = datetime.now().strftime('%c')
		sender = account.get_user_info(data['sender_id'], extended=False)
		recipient = account.get_user_info(data['recipient_id'], extended=False)

		chat.send_message(sender['id'], recipient['id'], data['text'])
		emit('private_chat response', data, room=users_in_chat[sender['id']])

		if recipient['id'] in users_in_chat:
			emit('send_message response', data, room=users_in_chat[recipient['id']])
		else:
			notification.send(recipient, 'message', sender)
	except KeyError as e:
		print(e)

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
