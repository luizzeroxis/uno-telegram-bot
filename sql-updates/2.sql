begin;

alter table uno_rooms
	add column draw_pass_behavior
		text not null default 'single_draw';

update uno_rooms set draw_pass_behavior='single_draw' where infinite_draws='false';
update uno_rooms set draw_pass_behavior='multiple_draws' where infinite_draws='true';

alter table uno_rooms
	drop column infinite_draws;

commit;