-- basic select into statement example
do $$
declare
	user_count int;
begin
	select count(*)
	into user_count
	from user_api_user;

	raise notice 'The number of users: %', user_count;
end $$;

-- using the select into with multiple variables

do $$
declare 
	u_username user_api_user.username%type;
	u_email user_api_user.email%type;
begin
	select username, email
	into u_username, u_email
	from user_api_user
	where id = 'a29f220c-52e9-46b8-8e75-131634ad66db';

	raise notice 'User username is % and email is %', u_username, u_email;
end $$;