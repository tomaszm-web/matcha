from datetime import datetime
from collections import defaultdict

from flask import session, request
from flask_socketio import emit

from app import socketio
from .models import Account, Chat, Notification

chats = defaultdict(dict)
connected = {}


@socketio.on('connect', namespace='/private_chat')
def connect_user_to_chat():
	user_id = session['user']
	recipient_id = int(request.args['recipient_id'])
	chat = Chat(user_id, recipient_id)

	chats[chat.id][user_id] = request.sid
	messages = chat.get_messages()
	emit('connect response', {'messages': messages}, room=chats[chat.id][user_id])


@socketio.on('send_message event', namespace='/private_chat')
def send_message(data):
	try:
		data['timestamp'] = datetime.now().strftime(Chat.timestamp_format)
		user_id = session['user']
		sender = Account(user_id, extended=False)
		recipient = Account(data['recipient_id'], extended=False)
		chat = Chat(sender.id, recipient.id)

		emit('message received', data, room=chats[chat.id][sender.id])
		chat.send_message(data['text'])
		if recipient.id in chats[chat.id]:
			emit('message received', data, room=chats[chat.id][recipient.id])
		else:
			Notification.send(sender, recipient, 'message')
	except KeyError as e:
		print(e)


@socketio.on('disconnect_from_chat', namespace='/private_chat')
def disconnect_from_chat(data):
	chats[data['chat_id']].pop(data['user_id'])


@socketio.on('connect')
def connect_user():
	if 'user' in session and session['user'] not in connected:
		user = Account(session['user'], extended=False)
		if not user.online:
			user.online = 1
		connected[user.id] = request.sid


@socketio.on('notification send')
def notification_send(data):
	if 'user' in session and session['user'] in connected:
		emit('notification received', data, room=connected[session['user']])


@socketio.on('disconnect')
def disconnect_user():
	if 'user' in session and session['user'] in connected:
		user = Account(session['user'], extended=False)
		if user.online:
			user.online = 0
		connected.pop(user.id)


@socketio.on_error()
def error_handler(e):
	pass


@socketio.on_error('/private_chat')
def error_handler(e):
	pass
