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

		self.draw_4_on_draw_4 = False
		self.draw_2_on_draw_4 = 'false'
		self.disable_call_bluff = False
		self.allow_play_non_drawn_cards = False
		self.allow_pass_without_draw = False
		self.draw_pass_behavior = 'single_draw'

		# init
		self.reset()

	def reset(self):

		self.num_players = 0
		self.winner = None
		self.current_card = None
		self.current_kind = None
		self.current_color = None
		self.current_player = 0
		self.previous_player = None
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

		for intent in self.get_play_intents(self.current_player):
			if intent.action == play.action and intent.card == play.card:
				
				if intent.can_play:
					if play.action == ACTION_PLAY:
						return self.play_card(play.card, play.new_color)
					elif play.action == ACTION_DRAW:
						return self.play_draw()
					elif play.action == ACTION_PASS:
						return self.play_pass()
					elif play.action == ACTION_CALL_BLUFF:
						return self.play_call_bluff()

				else:
					return PlayResult(fail_reason=intent.fail_reason)

		if play.card not in self.player_cards[self.current_player]:
			return PlayResult(fail_reason='doesnt_have_card')


	def play_card(self, card, new_color):

		# Clear previous bluff
		self.can_call_bluff = False

		# Check bluff
		if card.kind == KIND_DRAW_4:

			self.can_call_bluff = True
			self.previous_bluffed = False

			# Check if any cards that aren't +4s could have been played,
			# if there are then it is a bluff.
			for intent in self.get_play_intents_cards(self.current_player):
				if intent.can_play:
					if intent.card.kind != KIND_DRAW_4:
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

		self.sort_player_cards(self.current_player)

		# Special card effects
		self.do_special_effects(card, new_color)

		self.drawn_card = None

		self.next_player()

		self.current_play_number += 1
		return PlayResult(success=True, action=ACTION_PLAY, card=card, new_color=new_color, uno=uno)

	def play_draw(self):

		# If draw card has been played last, pick up those cards
		if self.draw_amount != 0:

			num_draw = self.draw_amount

			self.player_cards[self.current_player] += list(self.pick_cards(self.draw_amount))

			self.draw_amount = 0

			self.sort_player_cards(self.current_player)
			self.next_player()

		# If not, pick only one card and continue playing
		else:

			num_draw = 1

			self.sort_player_cards(self.current_player)

			self.drawn_card = self.pick_card()
			self.player_cards[self.current_player].append(self.drawn_card)

		# Clear previous bluff
		self.can_call_bluff = False

		self.current_play_number += 1
		return PlayResult(success=True, action=ACTION_DRAW, num_draw=num_draw, draw_pile_has_emptied=self.draw_pile_has_emptied)

	def play_pass(self):

		self.drawn_card = None

		self.sort_player_cards(self.current_player)
		self.next_player()

		# Clear previous bluff
		self.can_call_bluff = False

		self.current_play_number += 1
		return PlayResult(success=True, action=ACTION_PASS)

	def play_call_bluff(self):

		# If bluffed, previous player has to draw stacked draw card amount
		if self.previous_bluffed:

			num_draw = self.draw_amount

			self.player_cards[self.previous_player] += list(self.pick_cards(num_draw))
			self.sort_player_cards(self.previous_player)

		# If not bluffed, current player has to draw stacked draw card amount plus 2
		else:

			num_draw = self.draw_amount + 2

			self.player_cards[self.current_player] += list(self.pick_cards(num_draw))

		# Clear +4 effect
		self.draw_amount = 0

		# Clear previous bluff
		self.can_call_bluff = False

		self.sort_player_cards(self.current_player)
		self.next_player()

		self.current_play_number += 1
		return PlayResult(success=True, action=ACTION_CALL_BLUFF, bluffed=self.previous_bluffed, num_draw=num_draw, draw_pile_has_emptied=self.draw_pile_has_emptied)

	def get_play_intents(self, player):

		# ACTION_PLAY
		yield from self.get_play_intents_cards(player)

		# ACTION_DRAW
		yield self.get_play_intent_draw(player)

		# ACTION_PASS
		yield self.get_play_intent_pass(player)

		# ACTION_CALL_BLUFF
		yield self.get_play_intent_call_bluff(player)

	def get_play_intents_cards(self, player):

		for card in self.player_cards[player]:
			yield self.get_play_intent_card(card, player)

	def get_play_intent_card(self, card, player):

		if player != self.current_player:
			return PlayIntent(ACTION_PLAY, card, can_play=False, fail_reason='not_current_player')

		# Config for only allowing last drawn card to be played
		if not self.allow_play_non_drawn_cards:
			if self.drawn_card:
				if card != self.drawn_card:
					return PlayIntent(ACTION_PLAY, card, can_play=False, fail_reason='not_drawn_card')

		# Check if draws are required
		if self.draw_amount == 0:
			# When no draw card has been played last

			# If card has color
			if card.color != NO_COLOR:
				# If card doesn't match current kind or color
				if not (card.kind == self.current_kind or card.color == self.current_color):
					return PlayIntent(ACTION_PLAY, card, can_play=False, fail_reason='card_doesnt_match')

		else:
			# When draw card has been played last
			
			if self.current_kind == KIND_DRAW_2:
				if card.kind != KIND_DRAW_2 and card.kind != KIND_DRAW_4:
					return PlayIntent(ACTION_PLAY, card, can_play=False, fail_reason='not_draw_2_or_draw_4')

			elif self.current_kind == KIND_DRAW_4:
				if card.kind == KIND_DRAW_2:
					if self.draw_2_on_draw_4 == 'false':
						return PlayIntent(ACTION_PLAY, card, can_play=False, fail_reason='cant_draw_2_on_draw_4')
					
					if self.draw_2_on_draw_4 == 'true':
						# Only allow if +2 is the chosen +4 color
						if card.color != self.current_color:
							return PlayIntent(ACTION_PLAY, card, can_play=False, fail_reason='draw_2_different_color')

					if self.draw_2_on_draw_4 == 'true_any_color':
						pass

				elif card.kind == KIND_DRAW_4:
					if not self.draw_4_on_draw_4:
						return PlayIntent(ACTION_PLAY, card, can_play=False, fail_reason='cant_draw_4_on_draw_4')

				else:
					return PlayIntent(ACTION_PLAY, card, can_play=False, fail_reason='not_draw_2_or_draw_4')

		return PlayIntent(ACTION_PLAY, card)

	def get_play_intent_draw(self, player):

		if player != self.current_player:
			return PlayIntent(ACTION_DRAW, can_play=False, fail_reason='not_current_player')

		# Config for allowing only one draw
		if self.draw_pass_behavior == 'single_draw':
			if self.drawn_card:
				return PlayIntent(ACTION_DRAW, can_play=False, fail_reason='already_drew')

		return PlayIntent(ACTION_DRAW)

	def get_play_intent_pass(self, player):

		if player != self.current_player:
			return PlayIntent(ACTION_PASS, can_play=False, fail_reason='not_current_player')

		# Config for disallowing passing
		if self.draw_pass_behavior == 'multiple_draws_disable_pass':
			return PlayIntent(ACTION_PASS, can_play=False, fail_reason='cannot_pass')

		# Config for disallowing passing if has not drawn
		if not self.allow_pass_without_draw:
			if not self.drawn_card:
				return PlayIntent(ACTION_PASS, can_play=False, fail_reason='hasnt_drawn')

		return PlayIntent(ACTION_PASS)

	def get_play_intent_call_bluff(self, player):

		if player != self.current_player:
			return PlayIntent(ACTION_CALL_BLUFF, can_play=False, fail_reason='not_current_player')

		if self.disable_call_bluff:
			return PlayIntent(ACTION_CALL_BLUFF, can_play=False, fail_reason='bluff_disabled')

		if not self.can_call_bluff:
			return PlayIntent(ACTION_CALL_BLUFF, can_play=False, fail_reason='last_not_draw_4')

		return PlayIntent(ACTION_CALL_BLUFF)

	def get_next_player(self):
		return (self.current_player + self.direction) % self.num_players


Card = namedtuple('Card', ['kind', 'color'])
Play = namedtuple('Play', ['action', 'card', 'new_color'])
PlayResult = namedtuple('PlayResult',
	['success', 'action', 'card', 'new_color', 'num_draw', 'bluffed', 'uno', 'draw_pile_has_emptied', 'fail_reason'],
	defaults=(False, None, None, None, None, None, False, False, None,))
PlayIntent = namedtuple('PlayIntent', ['action', 'card', 'can_play', 'fail_reason'],
	defaults=(None, None, True, None,))

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