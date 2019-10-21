from flask import (
	request,
	session, jsonify)
from datetime import datetime
from .models import Account, Chat
from flask_socketio import emit
from app import db, socketio
from collections import defaultdict

chats = defaultdict(dict)
connected = set()


# @socketio.on('connect', namespace='/private_chat')
# def connect_user_to_chat():
# 	user_id = session['user']
# 	recipient_id = int(request.args['recipient_id'])
# 	chat = Chat(user_id, recipient_id)
#
# 	chats[chat.id][user_id] = request.sid
# 	messages = chat.get_messages()
# 	emit('connect response', {'messages': messages}, room=chats[chat.id][user_id])
# 	print(chats)
#
#
# @socketio.on('send_message event', namespace='/private_chat')
# def send_message(data):
# 	try:
# 		chat_id = int(data['chat_id'])
# 		data['timestamp'] = datetime.now().strftime(Chat.timestamp_format)
# 		sender = Account(data['sender_id'], extended=False)
# 		emit('send_message response', data, room=chats[chat_id][sender['id']])
#
# 		recipient = Account(data['recipient_id'], extended=False)
# 		Chat.send_message(chat_id, sender['id'], recipient['id'], data['text'])
#
# 		if recipient['id'] in chats[chat_id]:
# 			emit('send_message response', data, room=chats[chat_id][recipient['id']])
# 		else:
# 			notification.send(recipient, 'message', sender)
# 	except KeyError as e:
# 		print(e)
#
#
# @socketio.on('disconnect_from_chat', namespace='/private_chat')
# def disconnect_from_chat(data):
# 	chats[data['chat_id']].pop(data['user_id'])
#
#
# @socketio.on('connect')
# def connect_user():
# 	if 'user' in session and session['user'] not in connected:
# 		last_login_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
# 		sql = "UPDATE `users` SET online = 1, last_login = %s WHERE id = %s"
# 		db.query(sql, (last_login_date, session['user']))
# 		connected.add(session['user'])


# @socketio.on('disconnect')
# def disconnect_user():
# 	if 'user' in session and session['user'] in connected:
# 		sql = "UPDATE `users` SET online = 0 WHERE id = %s"
# 		db.query(sql, [session['user']])
# 		session.pop("user", None)
# 		connected.remove(session['user'])
#
#
# @socketio.on('my event')
# def evvvent():
# 	print("Disconnected!")
#
#
# @socketio.on_error()
# def error_handler(e):
# 	pass
#
#
# @socketio.on_error('/private_chat')
# def error_handler(e):
# 	pass
