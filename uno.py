from collections import namedtuple
import random

NO_COLOR = 0
COLOR_BLUE = 1
COLOR_GREEN = 2
COLOR_RED = 3
COLOR_YELLOW = 4

COLORS = [COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_YELLOW]

KIND_REVERSE = 10
KIND_SKIP = 11
KIND_DRAW_2 = 12
KIND_DRAW_4 = 13
KIND_WILD = 14

ACTION_PLAY = 'play'
ACTION_DRAW = 'draw'
ACTION_PASS = 'pass'
# ACTION_CALL_BLUFF = 'callbluff'

class Game():

	def __init__(self, num_players):
		self.num_players = num_players

		# config
		self.starting_num_player_cards = 7

		# init
		self.winner = None

		self.current_card = None
		self.current_kind = None
		self.current_color = None

		self.current_player = 0
		self.direction = 1
		self.drawn_card = None
		self.draw_amount = 0

		self.draw_pile = []
		
		self.draw_pile += list(generate_starting_cards())
		self.set_current_card(self.pick_random_card())

		self.do_special_effects(self.current_card)

		self.draw_pile += list(generate_non_starting_cards())
		self.shuffle_cards()

		self.player_cards = []

		for player in range(num_players):
			self.player_cards.append(list(self.pick_cards(self.starting_num_player_cards)))
			self.sort_player_cards(player)

	def set_current_card(self, card):
		self.current_card = card
		self.current_kind = card.kind
		self.current_color = card.color

	def pick_card(self):
		return self.draw_pile.pop()

	def pick_cards(self, number):
		for x in range(number):
			yield self.pick_card()

	def pick_random_card(self):
		return self.draw_pile.pop(random.randrange(len(self.draw_pile)))

	def shuffle_cards(self):
		random.shuffle(self.draw_pile)

	def sort_player_cards(self, player):
		self.player_cards[player].sort(key=lambda card: (card.color, card.kind, ))

	def next_player(self):
		self.current_player = (self.current_player + self.direction) % self.num_players

	def do_special_effects(self, card):

		# Special card effects
		if card.kind == KIND_REVERSE:
			self.direction = -self.direction

			# When it's only 2 players, reverse works like skip
			if self.num_players == 2:
				self.next_player()

		elif card.kind == KIND_SKIP:
			self.next_player()

		elif card.kind == KIND_DRAW_2:
			self.draw_amount += 2

		elif card.kind == KIND_DRAW_4:
			self.draw_amount += 4
			self.current_color = new_color

		elif card.kind == KIND_WILD:
			self.current_color = new_color

	def win(self):
		self.winner = self.current_player
		print(self.current_player + ' won')

	def uno(self):
		print(self.current_player + ' uwu')

	def play(self, player, play):

		if player != self.current_player:
			return PlayResult(fail_reason='not_current_player')

		if play.action == ACTION_PLAY:
			return self.play_card(play.card, play.new_color)
		elif play.action == ACTION_DRAW:
			return self.play_draw()
		elif play.action == ACTION_PASS:
			return self.play_pass()

	def play_card(self, card, new_color):

		# Check if player has the card
		if card not in self.player_cards[self.current_player]:
			return PlayResult(fail_reason='doesnt_have_card')

		# When player has drawn from the pile last time
		# Must be playing the drawn card, or pass
		if self.drawn_card:
			if card != self.drawn_card:
				return PlayResult(fail_reason='not_drawn_card')

		# When draw card has been played last
		if self.draw_amount != 0:

			# If +2, can add with +2 or +4
			if self.current_kind == KIND_DRAW_2:
				if card.kind != KIND_DRAW_2 and card.kind != KIND_DRAW_4:
					return PlayResult(fail_reason='not_draw_2_or_4_or_draw')

			# If +4, can't add anymore, must draw or call bluff
			if self.current_kind == KIND_DRAW_4:
				return PlayResult(fail_reason='not_draw_4_or_draw')

		# Check if card matches current card in kind or color
		if card.color != NO_COLOR and card.kind != self.current_kind and card.color != self.current_color:
			return PlayResult(fail_reason='card_doesnt_match')

		# Make card the current card
		self.set_current_card(card)

		# Remove card from player's hand
		self.player_cards[self.current_player].remove(card)

		# If no cards in hand, player wins
		if len(self.player_cards[self.current_player]) == 0:
			self.win()

		# If one card in hand, say UNO
		uno = False
		if len(self.player_cards[self.current_player]) == 1:
			uno = True

		# Sort cards (if drawn card happens)
		self.sort_player_cards(self.current_player)

		# Special card effects
		self.do_special_effects(card)

		self.drawn_card = None

		self.next_player()

		return PlayResult(success=True, action=ACTION_PLAY, card=card, new_color=new_color, uno=uno)

	def play_draw(self):

		# If player has drawn from the pile last time, can't do it again
		if self.drawn_card:
			return PlayResult(fail_reason='already_drew')

		# If draw card has been played last, pick up those cards
		if self.draw_amount != 0:

			num_draw = self.draw_amount

			self.player_cards[self.current_player] += list(self.pick_cards(self.draw_amount))
			self.sort_player_cards(self.current_player)

			self.draw_amount = 0

			self.next_player()

		# If not, pick only one card and continue playing
		else:

			num_draw = 1

			self.drawn_card = self.pick_card()
			self.player_cards[self.current_player].append(self.drawn_card)

		return PlayResult(success=True, action=ACTION_DRAW, num_draw=num_draw)

	def play_pass(self):

		# Can only pass if has drawn card
		if not self.drawn_card:
			return PlayResult(fail_reason='hasnt_drawn')

		self.drawn_card = None
		self.sort_player_cards(self.current_player)

		self.next_player()

		return PlayResult(success=True, action=ACTION_PASS)

	def get_current_card(self):
		return self.current_card

	def get_current_player_cards(self):
		return self.player_cards[self.current_player]

	def get_num_players_cards(self):
		for player, cards in enumerate(self.player_cards):
			yield (player, len(cards))

	def info(self):

		print('Players:')
		for player in range(self.num_players):
			print(str(player) + ': ' + str(len(self.player_cards[player])) + ' cards')

		print('Current card: ' + str(self.current_card))

		print('Your cards: ' + str(self.player_cards[self.current_player]))

Card = namedtuple('Card', ['kind', 'color'])
Play = namedtuple('Play', ['action', 'card', 'new_color'])
PlayResult = namedtuple('PlayResult',
	['success', 'action', 'card', 'new_color', 'num_draw', 'uno', 'fail_reason'],
	defaults=
	(False, None, None, None, None, False, None))

def make_cards(kinds, colors, amount=1):
	for kind in kinds:
		for color in colors:
			for x in range(amount):
				yield Card(kind, color)

def generate_starting_cards():
	yield from make_cards([0], COLORS)
	yield from make_cards([x for x in range(1, 9+1)], COLORS, amount=2)
	yield from make_cards([KIND_REVERSE, KIND_SKIP, KIND_DRAW_2], COLORS, amount=2)

def generate_non_starting_cards():
	yield from make_cards([KIND_WILD, KIND_DRAW_4], [NO_COLOR], amount=4)