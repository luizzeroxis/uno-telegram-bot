import os
import logging
import psycopg2
import pickle
import uno, unoparser

from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.error import TelegramError, Unauthorized, BadRequest,  TimedOut, ChatMigrated, NetworkError

conn, cur = None, None

def main():
	
	# Environment vars
	TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
	TELEGRAM_BOT_WEBHOOK = os.environ.get('TELEGRAM_BOT_WEBHOOK')
	DATABASE_URL = os.environ.get('DATABASE_URL')
	PORT = os.environ.get('PORT')

	# Enable logging
	logging.basicConfig(level=logging.INFO)
	logger = logging.getLogger(__name__)

	## Database setup
	global conn, cur
	conn = psycopg2.connect(DATABASE_URL)
	cur = conn.cursor()

	## Bot setup
	# Set up the Updater
	updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
	dp = updater.dispatcher

	# Command handlers
	dp.add_handler(CommandHandler('start', handler_start))
	dp.add_handler(CommandHandler('help', handler_help))

	dp.add_handler(CommandHandler('status', handler_status))
	dp.add_handler(CommandHandler('new', handler_new))
	dp.add_handler(CommandHandler('join', handler_join))
	dp.add_handler(CommandHandler('leave', handler_leave))
	dp.add_handler(CommandHandler('begin', handler_begin))
	dp.add_handler(CommandHandler('end', handler_end))

	dp.add_handler(CommandHandler('chat', handler_chat))

	# Message handlers
	dp.add_handler(MessageHandler(Filters.text & Filters.private, handler_text_message))

	dp.add_error_handler(handler_error)

	# Start the webhook
	updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TELEGRAM_BOT_TOKEN, clean=True, allowed_updates=["message"])
	updater.bot.set_webhook(TELEGRAM_BOT_WEBHOOK + TELEGRAM_BOT_TOKEN)
	updater.idle()

## Bot handlers

def handler_start(update, context):
	update.message.reply_text("Hello there")

def handler_help(update, context):
	update.message.reply_text(
		"*ZeroXis bot - made by @luizeldorado*\n"
		"/help - Shows this\n"
		"/status - Show what's going on\n"
		"/new - Create new room\n"
		"/join - Join a room\n"
		"/leave - Leave a room\n"
		"/begin - Begin game\n"
		"/end - End game\n"
		"/chat - Send a message to all in room\n"
		"When in game, send a message to make a play.\n"
		"d - Draw card(s)\n"
		"p - Pass\n"
		"<color><kind> - Play card of said color and kind.\n"
		"<color> can be b, g, r, y, or nothing in kinds that have no color.\n"
		"<kind> can be 0 to 9, r, s, +2, +4, or w\n"
		"+4 and w have no color, but you have to specify a color after it.\n"
		"Examples: g6, rr, +4y\n"
		, parse_mode=ParseMode.MARKDOWN)
	pass

def handler_status(update, context):

	text = ''
	user_id = update.message.from_user.id
	room_id = get_current_room(user_id)

	if room_id:
		users = select_users_in_room(room_id)

		text += 'You are currently in room number ' + str(room_id) + ', which has ' + str(len(users)) + ' user(s).\n'

		for user in users:
			text += '- ' + str(user) + '\n'

		game = select_game(room_id)
		player_number = select_player_number(room_id, user_id)

		if game:
			text += gameinfo(game, player_number)

	else:
		text += 'You are currently not joined in any room.\n'

	update.message.reply_text(text)

def handler_new(update, context):
	
	text = ''
	user_id = update.message.from_user.id
	current_room_id = get_current_room(user_id)

	if current_room_id == None:
		room_id = insert_room()
		insert_user_to_room(room_id, user_id)
		db_commit()

		text += 'Created and joined room ' + str(room_id) + '.\n'
	
	else:
		text = 'You are already in room ' + str(current_room_id) + '! You must /leave that room first.\n'

	update.message.reply_text(text)

def handler_join(update, context):
	
	if not update.message:
		print(update)

	text, text_to_all = '', ''
	user_id = update.message.from_user.id
	room_id = None

	if len(context.args) > 0:
		room_id = string_to_positive_integer(context.args[0])

		if room_id != None:

			current_room_id = get_current_room(user_id)
			room_exists = check_room_exists(room_id)

			if current_room_id:
				text += 'You are already in room ' + str(current_room_id) + '! You must /leave that room first.\n'

			if not room_exists:
				text += 'This room does not exist!\n'

			if not current_room_id and room_exists:
				insert_user_to_room(room_id, user_id)
				db_commit()

				text += 'Joined room ' + str(room_id) + '.\n'
				text_to_all += str(user_id) + ' joined the room.\n'
			
		else:
			text += 'This can\'t possibly be a room! Come on!\n'

	else:
		text += 'You have not said the room you want to join! Try /join <room number>\n'

	update.message.reply_text(text)
	send_message_to_room(context, room_id, text_to_all)

def handler_leave(update, context):
	
	text, text_to_all = '', ''
	user_id = update.message.from_user.id
	room_id = get_current_room(user_id)

	if room_id:
		delete_user_from_room(user_id)

		text += 'You have left room number '+str(room_id)+'.\n'

		if check_room_empty(room_id):
			delete_room(room_id)

			text += 'The room was empty with your departure, so it has been deleted.\n'
		else:
			text_to_all += str(user_id) + ' left the room.\n'

		db_commit()
		
	else:
		text += 'You are not in any room right now!\n'

	update.message.reply_text(text)
	send_message_to_room(context, room_id, text_to_all)

player_numbers = {}

def handler_begin(update, context):

	user_id = update.message.from_user.id
	room_id = get_current_room(user_id)

	if room_id:
		users = select_users_in_room(room_id)

		game = uno.Game(len(users))
		update_game(room_id, game)

		global player_numbers
		player_numbers = {}

		for i, user in enumerate(users):
			update_player_number(room_id, user, i)
			# player_numbers[users[i]] = i

		db_commit()

		send_message_to_room(context, room_id, 'Game has begun')
		send_message_to_room(context, room_id, lambda user_id: gameinfo(game, select_player_number(room_id, user_id)))

	else:
		update.message.reply_text("You cannot begin the game if you are not in a room! Try /new or /join <room number>")

def handler_end(update, context):
	
	user_id = update.message.from_user.id
	room_id = get_current_room(user_id)

	if room_id:

		update_game(room_id, None)
		db_commit()

		send_message_to_room(context, room_id, 'Game has ended')

	else:
		update.message.reply_text("You cannot end the game if you are not in a room! Try /new or /join <room number>")

def handler_chat(update, context):

	text, text_to_all = '', ''
	user_id = update.message.from_user.id
	room_id = get_current_room(user_id)

	message = ' '.join(context.args)

	if room_id:
		text_to_all += str(user_id) + ': ' + message
	else:
		text += 'You cannot send chat messages if you are not in a room!\n'
		update.message.reply_text(text)

	send_message_to_room(context, room_id, text_to_all, not_me=user_id)

def handler_text_message(update, context):
	
	user_id = update.message.from_user.id
	room_id = get_current_room(user_id)

	if room_id:

		message = update.message.text

		game = select_game(room_id)
		player_number = select_player_number(room_id, user_id)
		# player_number = player_numbers[user_id]

		try:
			play = unoparser.parse_play(message)
			if game.play(player_number, play):

				update_game(room_id, game)
				db_commit()

				send_message_to_room(context, room_id, str(user_id) + ' ' + unoparser.play_string(play))

				# send message to player that is current
				# context.bot.send_message(chat_id= , text='')
				# update.message.reply_text(gameinfo(game, player_number))

			else:
				update.message.reply_text('That is an invalid play.')

		except unoparser.InputParsingError as e:
			update.message.reply_text('You are dumb! ' + str(e))

	else:
		update.message.reply_text('You cannot play if you are not in a room! Try /new or /join <room number>')

def handler_error(update, context):
	try:
		raise context.error
	except Unauthorized:
		# remove update.message.chat_id from conversation list
		logging.exception('Uncaught')
	except BadRequest:
		# handle malformed requests - read more below!
		logging.exception('Uncaught')
	except TimedOut:
		# handle slow connection problems
		logging.exception('Uncaught')
	except NetworkError:
		# handle other connection problems
		logging.exception('Uncaught')
	except ChatMigrated as e:
		# the chat_id of a group has changed, use e.new_chat_id instead
		logging.exception('Uncaught')
	except TelegramError:
		# handle all other telegram related errors
		logging.exception('Uncaught')

## Helper functions

def string_to_positive_integer(string):
	try:
		number = int(string)
	except ValueError:
		return None

	if number >= 0:
		return number

def send_message_to_room(context, room_id, text, not_me=None):
	if text and room_id:
		for user_id in select_users_in_room(room_id):
			if user_id != not_me:
				if callable(text):
					context.bot.send_message(chat_id=user_id, text=text(user_id))
				else:
					context.bot.send_message(chat_id=user_id, text=text)

def gameinfo(game, player_number):
	text = ''

	text += 'Current player: (' + str(game.current_player) + ')\n'
	text += 'Current card: ' + unoparser.card_string(game.get_current_card()) + '\n'
	if game.current_color != game.get_current_card().color:
		text += 'Chosen color: ' + unoparser.card_color_string(game.current_color) + '\n'

	text += 'Your cards: ' + unoparser.card_list_string(game.player_cards[player_number]) + '\n'

	return text

## Database functions

def get_current_room(user_id):
	cur.execute("select room_id from uno_joins where user_id=%s limit 1;", (user_id,))
	result = cur.fetchone()

	if result:
		return result[0]

	return None

def select_users_in_room(room_id):
	cur.execute("select user_id from uno_joins where room_id=%s order by user_id;", (room_id,))

	return [row[0] for row in cur]

def select_game(room_id):
	cur.execute("select game_pickle from uno_rooms where id=%s limit 1;", (room_id,))
	result = cur.fetchone()[0]

	return pickle.loads(result)

def select_player_number(room_id, user_id):
	cur.execute("select player_number from uno_joins where room_id=%s and user_id=%s limit 1;", (room_id, user_id))
	return cur.fetchone()[0]

def check_room_empty(room_id):
	cur.execute("select room_id from uno_joins where room_id=%s limit 1;", (room_id,))
	result = cur.fetchone()

	if result:
		return False

	return True

def check_room_exists(room_id):
	cur.execute("select id from uno_rooms where id=%s limit 1;", (room_id,))
	result = cur.fetchone()

	if result:
		return True

	return False

def insert_room():
	cur.execute("insert into uno_rooms default values returning id;")
	room_id = cur.fetchone()[0]
	# conn.commit()

	return room_id

def insert_user_to_room(room_id, user_id):
	cur.execute("insert into uno_joins (room_id, user_id) values (%s, %s);", (room_id, user_id,))
	# conn.commit()

def update_game(room_id, game):
	cur.execute("update uno_rooms set game_pickle=%s where id=%s;", (pickle.dumps(game), room_id,))
	# conn.commit()

def update_player_number(room_id, user_id, player_number):
	cur.execute("update uno_joins set player_number=%s where room_id=%s and user_id=%s;", (player_number, room_id, user_id,))
	# conn.commit()

def delete_user_from_room(user_id):
	cur.execute("delete from uno_joins where user_id=%s;", (user_id,))
	# conn.commit()

def delete_room(room_id):
	cur.execute("delete from uno_rooms where id=%s;", (room_id,))
	# conn.commit()

def db_commit():
	conn.commit()

if __name__ == "__main__":
	main()