-- if then example
do $$
declare
	selected_user user_api_user%rowtype;
	input_user_id user_api_user.id%type = 'a29f220c-52e9-46b8-8e75-131634ad66dc';
begin
	select * from user_api_user
	into selected_user
	where id = input_user_id;

	if not found then
		raise notice 'The user % could not be found', input_user_id;
	end if;
end $$;


-- if then else statement example

do $$
declare
	selected_user user_api_user%rowtype;
	input_user_id user_api_user.id%type = 'a29f220c-52e9-46b8-8e75-131634ad66db';
begin
	select * from user_api_user
	into selected_user 
	where id = input_user_id;

	if not found then
		raise notice 'The user % could not be found', input_user_id;
	else
		raise notice 'The user email is %', selected_user.email;
	end if;
end $$;


-- if then elsif statement example

do $$
declare
	u_user user_api_user%rowtype;
	len_description varchar(100);
begin
	select * from user_api_user
	into u_user
	where id = 'a29f220c-52e9-46b8-8e75-131634ad66db';

	if not found then
		raise notice 'User not found';
	else
		if u_user.length >0 and u_user.length <=50 then
			len_description := 'Short';
		elsif u_user.length > 50 and u_user.length < 120 then
			len_description := 'Medium';
		elsif u_user.length > 120 then
			len_description := 'Long';
		else
			len_description := 'N/A';
		end if;

		raise notice 'The % user is %', u_user.email, len_description;
	end if;
end $$;
