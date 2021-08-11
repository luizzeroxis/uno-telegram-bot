alter table uno_rooms
	add column draw_4_on_draw_4
		text not null default 'false',
	add column draw_2_on_draw_4
		text not null default 'false',
	add column disable_call_bluff
		text not null default 'false',
	add column allow_play_non_drawn_cards
		text not null default 'false',
	add column infinite_draws
		text not null default 'false',
	add column allow_pass_without_draw
		text not null default 'false';