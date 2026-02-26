-- row type variable example

do $$
declare
	selected_user user_api_user%rowtype;
begin
	select * 
	into selected_user
	from user_api_user
	where id = 'a29f220c-52e9-46b8-8e75-131634ad66db';

	raise notice 'User name is % and User email is %',
	selected_user.username, selected_user.email;
end $$;