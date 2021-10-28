begin;

alter table uno_rooms
	add column show_bluffer_cards
		text not null default 'true';

update uno_rooms set show_bluffer_cards='false';

commit;