-- variable example
-- 1. declare variables

do $$
declare
	counter int = 1;
	first_name varchar(50) = 'Jhon';
	last_name varchar(50) = 'Doe';
	payment numeric(11,2) = 20.5;
begin
	raise notice '% % % has been paid % USD',
	counter,
	first_name,
	last_name,
	payment;
end $$;


-- 2. Assign values to the variables

do $$
declare
	first_name varchar(50);
begin
	first_name = split_part('Jhon Doe', ' ', 1);
	raise notice 'The first name is %', first_name;
end $$;

-- variable initialization timing
-- postgresql evaluated the initial value of a variable and assigns it when the block is entered.

do $$
declare
	created_at time = clock_timestamp();
begin
	raise notice '%', created_at;
	perform pg_sleep(3);
	raise notice '%', created_at;
end $$;


-- copying data types
do $$
declare
	user_name user_api_user.username%type;
	first_name user_name%type;
begin
	select username from user_api_user into user_name
	where id = 'a29f220c-52e9-46b8-8e75-131634ad66db';
	first_name = user_name;
	raise notice 'User username is: %', user_name;
	raise notice 'User first name is: %', first_name;
end $$;


-- variables in blocks and subblocks

do $$
<<outer_block>>
declare
	counter int := 0;
begin
	counter := counter + 1;
	raise notice 'The current value of the counter is %', counter;

	declare
		counter int = 0;
	begin
		counter = counter + 20;
		raise notice 'Counter in the subblock is %', counter;
		raise notice 'Counter in the outer block is %', outer_block.counter;
	end;

	raise notice 'Counter is the outer block is %', counter;
end outer_block $$;