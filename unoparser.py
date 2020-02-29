import uno

KIND_STRINGS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'Reverse', 'Skip', '+2', '+4', 'Wild']
COLOR_STRINGS = ['', 'Blue', 'Green', 'Red', 'Yellow']

ACTION_CMD_STRINGS = {
	'd': uno.ACTION_DRAW,
	'p': uno.ACTION_PASS,
}

KIND_CMD_STRINGS = {
	'0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
	'5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
	'r': uno.KIND_REVERSE,
	's': uno.KIND_SKIP,
	'+2': uno.KIND_DRAW_2,
	'+4': uno.KIND_DRAW_4,
	'w': uno.KIND_WILD,
}

COLOR_CMD_STRINGS = {
	'b': uno.COLOR_BLUE,
	'g': uno.COLOR_GREEN,
	'r': uno.COLOR_RED,
	'y': uno.COLOR_YELLOW,
}

def card_string(card):
	return ' '.join(x for x in [card_color_string(card.color), card_kind_string(card.kind)] if x)

def card_list_string(card_list):
	return ", ".join([card_string(card) for card in card_list])

def card_kind_string(card_kind):
	return KIND_STRINGS[card_kind]

def card_color_string(card_color):
	return COLOR_STRINGS[card_color]

def play_string(play):

	string = ''

	if play.action == uno.ACTION_PLAY:
		string += 'played '

		string += card_string(play.card)

		if play.new_color:
			string += ' with new color ' + card_color_string(play.new_color)
		else:
			string += '.'

	elif play.action == uno.ACTION_DRAW:
		string += 'drew cards.'
	elif play.action == uno.ACTION_PASS:
		string += 'passed.'

	return string

def parse_play(string):

	parser = Parser(string)

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