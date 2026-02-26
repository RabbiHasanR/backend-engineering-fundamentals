-- function example. returns the number of film whose length between the len_from and len_to
-- To replace the existing function, use the 'or replace' option.

create function get_film_count(len_from int, len_to int)
returns int
language plpgsql
as
$$
declare
	film_count integer;
begin
	select count(*)
	into film_count
	from film
	where length between len_from and len_to;

	return film_count;
end $$;


select get_film_count(40,90);

-- execute function using named notation

select get_film_count(
	len_from => 40,
	len_to => 90
)

-- using older syntax
select get_film_count(
	len_from := 40,
	len_to := 90
)


-- using mixed notation
select get_film_count(40, len_to => 90);

-- can not used named argument befor positional arguments
select get_film_count(len_from => 40, 90);

-- function parameter modes: in, out, inout
-- the in mode example. in is default mode

create or replace function find_film_by_id(p_film_id int)
returns varchar
language plpgsql
as $$
declare
	film_title film.title%type;
begin
	select title
	into film_title
	from film
	where film_id = p_film_id;

	if not found then
		raise 'Film with id % not found', p_film_id;
	end if;

	return film_title;
end $$;

select * from find_film_by_id(1);

-- the out mode example


create or replace function get_film_stat(
	out min_len int,
	out max_len int,
	out avg_len numeric)

language plpgsql
as $$
begin
	select min(length),
		   max(length),
		   avg(length)::numeric(5,1)
	into min_len, max_len, avg_len
	from film;
end $$;

select get_film_stat();

--output seperate as columns
select * from get_film_stat();


-- the inout mode
create or replace function swap(
	inout x int,
	inout y int
)
language plpgsql
as $$
begin
	select x,y into y,x;
end $$;

select * from swap(10,20);


-- function overloading
-- specific customer rental duration
create or replace function get_rental_duration(
	p_customer_id int
)
returns int
language plpgsql
as $$
declare
	rental_duration int;
begin
	select
		sum(extract(day from return_date - rental_date))
	into rental_duration
	from rental
	where customer_id = p_customer_id;

	return rental_duration;

end $$;
		
select get_rental_duration(232);


-- specific customer rental duration from a specific date up to now

create or replace function get_rental_duration(
	p_customer_id int,
	p_from_date date
)
returns int
language plpgsql
as $$
declare
	rental_duration int;
begin
	select sum(extract(day from return_date + '12:00:00' - rental_date))
	into rental_duration
	from rental
	where customer_id = p_customer_id and
		  rental_date >= p_from_date;


	return rental_duration;
end $$;

select get_rental_duration(232, '2005-07-01');

-- function return table
create or replace function get_film(
	p_pattern varchar
)
returns table (
	film_title varchar,
	film_release_year int
)
language plpgsql
as $$
begin
	return query
		select 
			title,	
			release_year::int
		from
			film
		where
			title ilike p_pattern;
end $$;

select get_film('Al%');

select * from get_film('Al%');

-- process each row

create or replace function get_film_two(
	p_pattern varchar,
	p_year int
)
returns table (
	film_title varchar,
	film_release_year int
)
language plpgsql
as $$
declare
	var_r record;
begin
	for var_r in (
			select title, release_year
			from film
			where title ilike p_pattern and
				release_year = p_year
			) loop film_title := upper(var_r.title);
			film_release_year := var_r.release_year;

			return next;
	end loop;
end $$;


select * from get_film_two('%er', 2006);


-- return on or more rows
drop function if exists find_film_by_id(p_id int);

create or replace function find_film_by_id(
	p_id int
)
returns setof film
as $$
begin
	-- return query select * from film where film_id = p_id;
	return query select * from film;
end;
$$
language plpgsql;

select find_film_by_id(100);

-- retrieve the title of the film with id 100
select (find_film_by_id(100)).title;

--retrieve the data from all columns of the returned row
select * from find_film_by_id(100);
