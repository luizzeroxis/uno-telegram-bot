begin;

alter table uno_rooms
	add column allow_highlight_playable_cards
		text not null default 'false';

commit;