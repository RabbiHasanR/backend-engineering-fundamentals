-- using record with the select into statement

do $$
declare
	rec record;
begin
	select id, username, email
	into rec
	from user_api_user
	where id = 'a29f220c-52e9-46b8-8e75-131634ad66db';

	raise notice '% % %', rec.id, rec.username, rec.email;
end $$;


-- using record variables in the for loop statement

do $$
declare
	rec record;
begin
	for rec in select *
			from user_api_user
	loop
		raise notice '% : (%) (%)', rec.id, rec.username, rec.email;
	end loop;
end $$;