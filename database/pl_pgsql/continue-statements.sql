-- continue statement example

do $$
declare counter int = 0;
begin
	loop
		counter = counter + 1;
		exit when counter > 10;

		continue when mod(counter, 2) = 0;

		raise notice '%', counter;
	end loop;
end $$;