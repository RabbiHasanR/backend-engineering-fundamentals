-- dollar quoted string constant systax

select 'String constant' as message0;

select 'I''m a string constant' as message1;

select $$I'm a string constant$$ as message2;

select $$I'm a string constant$$ as message3;


select $message$I'm a string constant$message$ s;


-- with out use dollar quoted
do
'declare
	film_count integer;
begin
	select count(*) into film_count
	from user_api_user;
	raise notice ''The number of films: %'', film_count;
end;'
;


-- using dollar quoted
do
$$
declare
	user_count integer;
begin
	select count(*) into user_count
	from user_api_user;
	raise notice 'The number of users: %', user_count;
end;
$$;



-- using dollar-quoted string constants in functions
-- function syntex
-- create function function_name(param_list)
-- 	returns datatype

-- language lang_name
-- as
-- 	'function_body'



-- without using dollar quoted
create function find_user_by_id(
	u_id UUID
) returns user_api_user
language sql
as 
	'select * from user_api_user
	where id = u_id';


select find_user_by_id('a29f220c-52e9-46b8-8e75-131634ad66db');



-- using dollar quoted string constants

create function find_all_users() returns user_api_user
language sql
as
$$
	select * from user_api_user;
$$;

select find_all_users();


-- usng dollar quoted string constants in stored procedures
-- create procedure proc_name(param_list)
-- language lang_name
-- as $$
-- 	-- stored procedure body
-- $$