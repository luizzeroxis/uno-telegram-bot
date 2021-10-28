import uno

from plural import plural

KIND_STRINGS_SHORT = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'R', 'S', '+2', '+4', 'W']
KIND_STRINGS_LONG = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'Reverse', 'Skip', 'Draw 2', 'Draw 4', 'Wild']

KIND_STRINGS = KIND_STRINGS_SHORT

COLOR_STRINGS_SHORT = ['', 'b', 'g', 'r', 'y']
COLOR_STRINGS_EMOJI = ['⬛', '🟦', '🟩', '🟥', '🟨']
COLOR_STRINGS_CIRCLE = ['⚫', '🔵', '🟢', '🔴', '🟡']
COLOR_STRINGS_HEART = ['🖤', '💙', '💚', '❤️', '💛']
COLOR_STRINGS_LONG = ['', 'Blue', 'Green', 'Red', 'Yellow']

COLOR_STRINGS = COLOR_STRINGS_SHORT

ACTION_CMD_STRINGS = {
	'd': uno.ACTION_DRAW,
	'p': uno.ACTION_PASS,
	'c': uno.ACTION_CALL_BLUFF,

	'draw': uno.ACTION_DRAW,
	'pass': uno.ACTION_PASS,
	'call bluff': uno.ACTION_CALL_BLUFF,
}

KIND_CMD_STRINGS = {
	'0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
	'5': 5, '6': 6, '7': 7, '8': 8, '9': 9,

	'r': uno.KIND_REVERSE,
	's': uno.KIND_SKIP,
	'+2': uno.KIND_DRAW_2,
	'+4': uno.KIND_DRAW_4,
	'w': uno.KIND_WILD,

	'reverse': uno.KIND_REVERSE,
	'skip': uno.KIND_SKIP,
	'draw 2': uno.KIND_DRAW_2,
	'draw 4': uno.KIND_DRAW_4,
	'wild': uno.KIND_WILD,
}

COLOR_CMD_STRINGS = {
	'b': uno.COLOR_BLUE,
	'g': uno.COLOR_GREEN,
	'r': uno.COLOR_RED,
	'y': uno.COLOR_YELLOW,

	'🟦': uno.COLOR_BLUE,
	'🟩': uno.COLOR_GREEN,
	'🟥': uno.COLOR_RED,
	'🟨': uno.COLOR_YELLOW,

	'🔵': uno.COLOR_BLUE,
	'🟢': uno.COLOR_GREEN,
	'🔴': uno.COLOR_RED,
	'🟡': uno.COLOR_YELLOW,

	'💚': uno.COLOR_BLUE,
	'💙': uno.COLOR_GREEN,
	'❤️': uno.COLOR_RED,
	'💛': uno.COLOR_YELLOW,

	'blue': uno.COLOR_BLUE,
	'green': uno.COLOR_GREEN,
	'red': uno.COLOR_RED,
	'yellow': uno.COLOR_YELLOW,
}

HIGHLIGHT_PLAYABLE = False

def card_string(card):
	return ''.join(x for x in [card_color_string(card.color), card_kind_string(card.kind)] if x)

def card_list_string(card_list):
	return ", ".join([card_string(card) for card in card_list])

def card_kind_string(card_kind):
	return KIND_STRINGS[card_kind]

def card_color_string(card_color):
	return COLOR_STRINGS[card_color]

def play_intent_string(play_intent):
	if play_intent.can_play and HIGHLIGHT_PLAYABLE:
		f_string = "<u>{}</u>"
	else:
		f_string = "{}"

	if play_intent.action == uno.ACTION_PLAY:
		return f_string.format(card_string(play_intent.card))
	elif play_intent.action == uno.ACTION_DRAW:
		return f_string.format("Draw")
	elif play_intent.action == uno.ACTION_PASS:
		return f_string.format("Pass")
	elif play_intent.action == uno.ACTION_CALL_BLUFF:
		return f_string.format("Call bluff")

def play_intent_list_string(play_intent_list):
	return ", ".join((play_intent_string(play_intent) for play_intent in play_intent_list))

def play_result_string(play_result, current_player_name, last_player_name=None):

	string = str(current_player_name) + ' '

	if play_result.action == uno.ACTION_PLAY:
		string += 'played '

		string += card_string(play_result.card)

		if play_result.new_color:
			string += ' with new color ' + card_color_string(play_result.new_color)
		
		string += '.'

		if play_result.uno:
			string += ' UNO!'

	elif play_result.action == uno.ACTION_DRAW:
		string += 'drew ' + str(play_result.num_draw) + ' ' + plural(play_result.num_draw, 'card', 'cards') + '.'
	elif play_result.action == uno.ACTION_PASS:
		string += 'passed.'

	elif play_result.action == uno.ACTION_CALL_BLUFF:
		string += 'called ' + str(last_player_name) + '\'s bluff... '

		if play_result.bluffed:
			string += 'and it was a bluff. ' + str(last_player_name) + ' received ' + str(play_result.num_draw) + ' ' + plural(play_result.num_draw, 'card', 'cards') + '.'
		else:
			string += 'and it was not a bluff. ' + str(current_player_name) + ' received ' + str(play_result.num_draw) + ' ' + plural(play_result.num_draw, 'card', 'cards') + '.'

	return string

def fail_reason_string(fail_reason):

	if fail_reason == 'not_current_player':
		return 'It is not your turn!'
	elif fail_reason == 'doesnt_have_card':
		return 'You do not have that card in your hand!'
	elif fail_reason == 'not_drawn_card':
		return 'You can only play the card you last drew!'
	elif fail_reason == 'card_doesnt_match':
		return 'This card does not match the current card!'
	elif fail_reason == 'not_draw_2_or_draw_4':
		return 'You can only play +2 or +4 or draw when the current card is +2!'
	elif fail_reason == 'cant_draw_2_on_draw_4':
		return 'You cannot play +2 on a +4!'
	elif fail_reason == 'draw_2_different_color':
		return 'You cannot play a +2 of a different color than the chosen +4 color!'
	elif fail_reason == 'cant_draw_4_on_draw_4':
		return 'You cannot play a +4 on a +4!'
	elif fail_reason == 'already_drew':
		return 'You already drew, play that card or pass!'
	elif fail_reason == 'cannot_pass':
		return 'You shall not pass!'
	elif fail_reason == 'hasnt_drawn':
		return 'You cannot pass without drawing!'
	elif fail_reason == 'bluff_disabled':
		return 'Calling bluffs has been disabled!'
	elif fail_reason == 'last_not_draw_4':
		return 'You cannot call a bluff if the previous player has not played a +4!'
	elif fail_reason == 'draw_played':
		return 'You cannot play non draw cards on draw cards!'
	else:
		return 'You failed in an unforeseen way! (' + str(fail_reason) + ')'

def parse_play(string):

	parser = Parser(string.lower())

	parser.clear_whitespace()
	action = parser.check_dict(ACTION_CMD_STRINGS)

	if action == None:
		color = parser.check_dict(COLOR_CMD_STRINGS)

		parser.clear_whitespace()
		kind = parser.check_dict(KIND_CMD_STRINGS)

		new_color = None

		if kind in [uno.KIND_DRAW_4, uno.KIND_WILD]:
			if color == None:
				parser.clear_whitespace()
				new_color = parser.check_dict(COLOR_CMD_STRINGS)

				if new_color == None:
					raise InputParsingError('You did not choose a new color!')
			else:
				new_color = color

			color = uno.NO_COLOR

		else:
			if kind == None or color == None:
				raise InputParsingError('You did not choose a card or action!')

		return uno.Play(uno.ACTION_PLAY, uno.Card(kind, color), new_color)

	else:
		return uno.Play(action, None, None)

class InputParsingError(Exception):
	pass

class Parser():

	def __init__(self, string):
		self.string = string
		self.pos = 0

	def ended(self):
		return self.pos >= len(self.string)

	def clear_whitespace(self):
		while not self.ended() and self.string[self.pos] == ' ':
			self.pos += 1

	def check_dict(self, dictionary, none=None):

		if not self.ended():
			for find_str, value in dictionary.items():
				if self.string[self.pos : self.pos + len(find_str)] == find_str:
					self.pos += len(find_str)
					return value

		return none