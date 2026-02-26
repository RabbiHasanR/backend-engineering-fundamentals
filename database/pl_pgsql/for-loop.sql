-- sample for loop example

do $$
begin
	for counter in 1..5 loop
		raise notice 'counter: %', counter;
	end loop;
end $$;

-- using reverse

do $$
begin
	for counter in reverse 5..1 loop
		raise notice 'counter: %', counter;
	end loop;
end $$;


-- using step

do $$
begin
	for counter in 1..6 by 2 loop
		raise notice 'counter: %', counter;
	end loop;
end $$;


-- iterate result set using for loop

do $$
declare
	f record;
begin
	for f in select title, length
			from film
			order by length desc, title
			limit 10
	loop
	raise notice '%(% mins)', f.title, f.length;
	end loop;
end $$;


-- iterate over the result set using dynamic query and for loop


do $$
declare
	sort_type smallint = 1;
	rec_count int = 10;
	rec record;
	query text;
begin
	query = 'select title, release_year from film ';

	if sort_type = 1 then
		query = query || 'order by title';
	elsif sort_type = 2 then
		query = query || 'order by release_year';
	else
		raise 'invalid sort type %s', sort_type;
	end if;

	query = query || ' limit $1';

	for rec in execute query using rec_count
	loop
		raise notice '% - %', rec.release_year, rec.title;
	end loop;
end $$;