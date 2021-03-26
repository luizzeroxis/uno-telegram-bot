from collections import namedtuple
import random

NO_COLOR, COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_YELLOW = range(5)
COLORS = [COLOR_BLUE, COLOR_GREEN, COLOR_RED, COLOR_YELLOW]

KIND_REVERSE, KIND_SKIP, KIND_DRAW_2, KIND_DRAW_4, KIND_WILD = range(10, 15)

ACTION_PLAY, ACTION_DRAW, ACTION_PASS, ACTION_CALL_BLUFF = range(4)

class Game():

	def __init__(self):

		# config
		self.starting_num_player_cards = 7

		# init
		self.reset()

	def reset(self):

		self.num_players = 0
		self.winner = None
		self.current_card = None
		self.current_kind = None
		self.current_color = None
		self.current_player = 0
		self.direction = 1
		self.drawn_card = None
		self.draw_amount = 0
		self.can_call_bluff = False
		self.previous_bluffed = None
		self.draw_pile = []
		self.player_cards = []
		self.discard_pile = []
		self.draw_pile_has_emptied = False
		self.current_play_number = 0

	def begin(self, num_players):

		self.reset()

		self.num_players = num_players
		
		# Generate draw pile cards, with only allowed start cards
		self.draw_pile += list(generate_starting_cards())
		# Pick starting card
		self.set_current_card(self.pick_random_card())

		# Do special effects of starting card
		self.do_special_effects(self.current_card)

		# Generate rest of draw pile cards (cards not allowed to start with)
		self.draw_pile += list(generate_non_starting_cards())
		# Randomize cards
		self.shuffle_cards()

		# Pick player cards
		for player in range(num_players):
			self.player_cards.append(list(self.pick_cards(self.starting_num_player_cards)))
			self.sort_player_cards(player)

	def load(self):
		pass

	def save(self):
		pass

	def set_current_card(self, card):
		self.current_card = card
		self.current_kind = card.kind
		self.current_color = card.color
		self.discard_pile.append(card)

	def pick_card(self):
		if len(self.draw_pile) == 0:

			if len(self.discard_pile) <= 1:
				print("You ran out of cards. How's that even possible")
				pass

			self.draw_pile = self.discard_pile[:-1]
			self.discard_pile = self.discard_pile[-1:]

			self.shuffle_cards()

			self.draw_pile_has_emptied = True

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
		self.previous_player = self.current_player
		self.current_player = (self.current_player + self.direction) % self.num_players

	def do_special_effects(self, card, new_color=None):

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

	def play(self, player, play):

		if player != self.current_player:
			return PlayResult(fail_reason='not_current_player')

		self.draw_pile_has_emptied = False

		if play.action == ACTION_PLAY:
			return self.play_card(play.card, play.new_color)
		elif play.action == ACTION_DRAW:
			return self.play_draw()
		elif play.action == ACTION_PASS:
			return self.play_pass()
		elif play.action == ACTION_CALL_BLUFF:
			return self.play_call_bluff()

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
				return PlayResult(fail_reason='not_draw_or_bluff')

		# Check if card matches current card in kind or color
		if card.color != NO_COLOR and card.kind != self.current_kind and card.color != self.current_color:
			return PlayResult(fail_reason='card_doesnt_match')

		# Clear previous bluff
		self.can_call_bluff = False

		# Check bluff
		if card.kind == KIND_DRAW_4:

			self.can_call_bluff = True
			self.previous_bluffed = False

			# Check if any card could have been played
			for player_card in self.player_cards[self.current_player]:
				if player_card.color == self.current_color:
					self.previous_bluffed = True
					break

		# Make card the current card
		self.set_current_card(card)

		# Remove card from player's hand
		self.player_cards[self.current_player].remove(card)

		# If no cards in hand, player wins
		if len(self.player_cards[self.current_player]) == 0:
			self.winner = self.current_player

		# If one card in hand, say UNO
		uno = False
		if len(self.player_cards[self.current_player]) == 1:
			uno = True

		# Special card effects
		self.do_special_effects(card, new_color)

		self.drawn_card = None

		self.next_player()

		self.current_play_number += 1
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

		# Clear previous bluff
		self.can_call_bluff = False

		self.current_play_number += 1
		return PlayResult(success=True, action=ACTION_DRAW, num_draw=num_draw, draw_pile_has_emptied=self.draw_pile_has_emptied)

	def play_pass(self):

		# Can only pass if has drawn card
		if not self.drawn_card:
			return PlayResult(fail_reason='hasnt_drawn')

		self.drawn_card = None
		self.sort_player_cards(self.current_player)

		self.next_player()

		# Clear previous bluff
		self.can_call_bluff = False

		self.current_play_number += 1
		return PlayResult(success=True, action=ACTION_PASS)

	def play_call_bluff(self):

		if not self.can_call_bluff:
			return PlayResult(fail_reason='last_not_draw_4')

		# If bluffed, previous player has to draw stacked draw card amount
		if self.previous_bluffed:

			num_draw = self.draw_amount

			self.player_cards[self.previous_player] += list(self.pick_cards(num_draw))
			self.sort_player_cards(self.previous_player)

		# If not bluffed, current player has to draw stacked draw card amount plus 2
		else:

			num_draw = self.draw_amount + 2

			self.player_cards[self.current_player] += list(self.pick_cards(num_draw))
			self.sort_player_cards(self.current_player)

		# Clear +4 effect
		self.draw_amount = 0

		# Clear previous bluff
		self.can_call_bluff = False

		self.next_player()

		self.current_play_number += 1
		return PlayResult(success=True, action=ACTION_CALL_BLUFF, bluffed=self.previous_bluffed, num_draw=num_draw, draw_pile_has_emptied=self.draw_pile_has_emptied)

	def get_current_card(self):
		return self.current_card

	def get_current_player_cards(self):
		return self.player_cards[self.current_player]

	def get_num_players_cards(self):
		for player, cards in enumerate(self.player_cards):
			yield (player, len(cards))

	def get_next_player(self):
		return (self.current_player + self.direction) % self.num_players

Card = namedtuple('Card', ['kind', 'color'])
Play = namedtuple('Play', ['action', 'card', 'new_color'])
PlayResult = namedtuple('PlayResult',
	['success', 'action', 'card', 'new_color', 'num_draw', 'bluffed', 'uno', 'draw_pile_has_emptied', 'fail_reason'],
	defaults=
	(False, None, None, None, None, None, False, False, None))

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