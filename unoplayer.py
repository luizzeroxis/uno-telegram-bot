import uno
import unoparser
from unoparser import InputParsingError

from plural import plural

game = None

def main():

	begin()
	play_until_end()

def begin():

	num_players = ask_input("Number of players: ", parse_pos_int)

	global game
	game = uno.Game()
	game.begin(num_players)

	status()

def play():

	playing_player = game.current_player

	play = ask_input(str(game.current_player) + "> ", parse_play, once=True)
	if not play:
		return False

	play_result = game.play(game.current_player, play)

	if play_result.success:
		print("#" + str(game.current_play_number) + ": " + str(playing_player) + " " + unoparser.play_result_string(play_result))
		status()
		return True
	else:
		print(unoparser.fail_reason_string(play_result.fail_reason))
		return False

def play_until_success():

	while not play():
		pass

def play_until_end():

	while game.winner == None:
		play()

	print(game.winner + ' won.')

def status():

	text = ''

	if game.direction == 1:
		player_numbers = range(game.num_players)
	else:
		player_numbers = range(game.num_players-1, -1, -1)

	for for_player_number in player_numbers:

		num_cards = len(game.player_cards[for_player_number])
		text += str(for_player_number) + ': ' + str(num_cards) + ' ' + plural(num_cards, 'card', 'cards')

		if game.winner == None:
			if game.current_player == for_player_number:
				text += ' <- Current'
			elif game.get_next_player() == for_player_number:
				text += ' <- Next'
		elif game.winner == for_player_number:
			text += ' <- Winner'

		text += '\n'

	text += 'Current card: ' + unoparser.card_string(game.get_current_card()) + '\n'
	if game.current_color != game.get_current_card().color:
		text += 'Chosen color: ' + unoparser.card_color_string(game.current_color) + '\n'

	player_number = game.current_player

	text += 'Your cards: '
	
	if len(game.player_cards[player_number]) != 0:
		text += unoparser.card_list_string(game.player_cards[player_number])
	else:
		text += 'None!'

	text += '\n'

	print(text)

	return text

def ask_input(text, return_fun=lambda x: x, once=False):

	while True:
		result = input(text)
		try:
			return return_fun(result)
		except InputParsingError as e:
			print(e)

		if once:
			break

def parse_pos_int(string):
	try:
		return int(string)
	except ValueError as e:
		raise InputParsingError('That is not a positive integer number!')

def parse_play(message):

	global game

	if message == 'give +4':
		game.player_cards[game.current_player] += [uno.Card(uno.KIND_DRAW_4, uno.NO_COLOR)]
		raise InputParsingError('CHEAT: GIVE +4')
	if message == 'clear cards':
		game.player_cards[game.current_player] = []
		raise InputParsingError('CHEAT: CLEAR CARDS')
	if message == 'give r':
		game.player_cards[game.current_player] += [uno.Card(uno.KIND_REVERSE, color) for color in uno.COLORS]
		raise InputParsingError('CHEAT: GIVE R')

	return unoparser.parse_play(message)

if __name__ == "__main__":
	main()