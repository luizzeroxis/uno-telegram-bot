begin;

alter table uno_users
	add column receive_status
		text not null default 'my_turn';

commit;