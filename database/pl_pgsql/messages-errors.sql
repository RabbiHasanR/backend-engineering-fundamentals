-- errors and messages

do $$
begin
	raise info 'information message %', now();
	raise log 'log message %', now();
	raise debug 'debug message %', now();
	raise warning 'warning message %', now();
	raise notice 'notice message %', now();
end $$;

-- raise errors

do $$
declare
	email varchar(255) := '[[email protected]](../cdn-cgi/1/email-protection.html)';
begin
	raise exception 'duplicate email: %', email
		  using hint = 'check the email again';
end $$;


do $$
begin
	raise sqlstate '77777';
end $$;


do $$
begin
	raise invalid_regular_expression;
end $$;


-- assert statement example
-- if assert condition false then raise errors, else not

do $$
declare
	user_count integer;
begin
	select count(*)
	into user_count
	from user_api_user;
	raise notice '%', user_count;
	assert user_count > 0, 'User not found, check the user table';
end $$;