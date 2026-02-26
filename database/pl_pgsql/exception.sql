-- handling no data found exception example

do $$
declare
	rec record;
	v_film_id int = 2000;
begin
	select film_id, title
	into strict rec
	from film
	where film_id = v_film_id;

	exception
		when no_data_found then
			raise exception 'film % not found', v_film_id;
end $$;



-- handling too many rows exception example

do $$
declare
	rec record;
begin
	select film_id, title
	into strict rec
	from film
	where title like 'A%';

	exception
		when too_many_rows then
			raise exception 'Search query returns too many rows';
end $$;


-- handling multiple exceptions

do $$
declare
	rec record;
	v_length int = 90;
begin
	select film_id, title
	into strict rec
	from film
	where length = v_length;

	exception
		when sqlstate 'P0002' then
			raise exception 'film with length % not found', v_length;
		when sqlstate 'P0003' then
			raise exception 'The with length % is not found', v_length;
end $$;