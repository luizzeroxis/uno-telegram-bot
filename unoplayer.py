import uno
import unoparser
from unoparser import InputParsingError

from plural import plural

game = None

def main():

	num_players = ask_input("Number of players: ", parse_pos_int)

	global game
	game = uno.Game()
	game.begin(num_players)

	status(game)

	while True:
		play = ask_input(str(game.current_player) + "> ", parse_play)

		play_result = game.play(game.current_player, play)

		if play_result.success:
			print(unoparser.play_result_string(play_result))
			status(game)
		else:
			print(unoparser.fail_reason_string(play_result.fail_reason))

def status(game):

	text = ''

	for for_player_number in range(game.num_players):

		num_cards = len(game.player_cards[for_player_number])
		text += str(for_player_number) + ': ' + str(num_cards) + ' ' + plural(num_cards, 'card', 'cards')

		if game.winner == None and game.current_player == for_player_number:
			text += ' <- Current player'
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

def parse_pos_int(string):
	try:
		return int(string)
	except ValueError as e:
		raise InputParsingError('That is not a positive integer number!')

def ask_input(text, return_fun=lambda x: x):

	while True:
		result = input(text)
		try:
			return return_fun(result)
		except InputParsingError as e:
			print(e)

def parse_play(message):

	global game

	if message == 'give +4':
		game.player_cards[game.current_player] += [uno.Card(uno.KIND_DRAW_4, uno.NO_COLOR)]
		raise InputParsingError('CHEAT: GIVE +4')
	if message == 'clear cards':
		game.player_cards[game.current_player] = []
		raise InputParsingError('CHEAT: CLEAR CARDS')

	return unoparser.parse_play(message)

if __name__ == "__main__":
	main()