# Database dealing code (shared between interfaces)

import logging
import os
import pickle

import psycopg2
from psycopg2 import sql

# All possible settings and its possible values (first one is the default)
all_settings = {
	'style': ('short', 'emoji', 'circle', 'heart', 'long',),
	'show_play_number': ('false', 'true',),
}

# All possible room configs and its possible values (first one is the default)
all_configs = {
	# TODO
	'draw_4_on_draw_4': ('false', 'true',),
	'draw_2_on_draw_4': ('false', 'true',),
	'disable_call_bluff': ('false', 'true',),
	'allow_play_non_drawn_cards': ('false', 'true',),
	'allow_pass_without_draw': ('false', 'true',),
	'draw_pass_behavior': ('single_draw', 'multiple_draws', 'multiple_draws_disable_pass'),

	# 'number_starting_cards': 7,
}

conn, cur = None, None

def main():

	# Environment vars
	DATABASE_URL = os.environ.get('DATABASE_URL')

	# Enable logging
	logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
	logger = logging.getLogger(__name__)

	# Database setup
	global conn, cur
	conn = psycopg2.connect(DATABASE_URL)
	cur = conn.cursor()

## Database functions

def get_user_settings(user_id):

	all_settings_list = list(all_settings)

	cur.execute(
		sql.SQL("select {fields} from uno_users where user_id=%s limit 1;")
			.format(
				fields=sql.SQL(',').join(sql.Identifier(n) for n in all_settings_list)
			),
		(user_id,)
	)

	result = cur.fetchone()

	if not result:
		return {k: v[0] for k, v in all_settings.items()} # default values for all settings
	else:
		settings = dict(zip(all_settings_list, result))

		return settings

def get_room_configs(room_id):

	all_configs_list = list(all_configs)

	cur.execute(
		sql.SQL("select {fields} from uno_rooms where id=%s limit 1;")
			.format(
				fields=sql.SQL(',').join(sql.Identifier(n) for n in all_configs_list)
			),
		(room_id,)
	)

	result = cur.fetchone()

	if not result:  # this is never supposed to happen!
		# return {k: v[0] for k, v in all_configs.items()} # default values for all configs
		return None
	else:
		configs = dict(zip(all_configs_list, result))

		return configs

def get_current_room(user_id):
	cur.execute("select room_id from uno_joins where user_id=%s limit 1;", (user_id,))
	result = cur.fetchone()

	if result:
		return result[0]

	return None

def select_users_info_in_room(room_id):
	cur.execute("select player_number, user_id from uno_joins where room_id=%s order by player_number, user_id;", (room_id,))
	return [(row[0], row[1],) for row in cur]

def select_users_ids_in_room(room_id):
	cur.execute("select user_id from uno_joins where room_id=%s order by user_id;", (room_id,))
	return [row[0] for row in cur]

def select_player_number(room_id, user_id):
	cur.execute("select player_number from uno_joins where room_id=%s and user_id=%s limit 1;", (room_id, user_id))
	return cur.fetchone()[0]

def select_user_id_from_player_number(room_id, player_number):
	cur.execute("select user_id from uno_joins where room_id=%s and player_number=%s limit 1;", (room_id, player_number))
	return cur.fetchone()[0]

def select_game(room_id):
	cur.execute("select game_pickle from uno_rooms where id=%s limit 1;", (room_id,))
	result = cur.fetchone()[0]

	if result:
		return pickle.loads(result)
	else:
		return None

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

def update_user_settings(user_id, setting, value):

	cur.execute(
		sql.SQL("insert into uno_users (user_id, {settings}) values (%s, %s) "
			"on conflict (user_id) do update set {settings} = excluded.{settings};")
			.format(
				settings=sql.Identifier(setting)
			),
		(user_id, value,)
	)
	# conn.commit()

def update_room_config(room_id, config, value):

	cur.execute(
		sql.SQL("update uno_rooms set {configs}=%s where id=%s;")
			.format(
				configs=sql.Identifier(config)
			),
		(value, room_id,)
	)
	# conn.commit()

def delete_user_from_room(user_id):
	cur.execute("delete from uno_joins where user_id=%s;", (user_id,))
	# conn.commit()

def delete_room(room_id):
	cur.execute("delete from uno_rooms where id=%s;", (room_id,))
	# conn.commit()

def commit():
	conn.commit()

main()