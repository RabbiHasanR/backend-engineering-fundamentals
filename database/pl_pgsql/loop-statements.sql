-- basic loop example

do $$
declare
	counter int = 0;
begin
	loop
		counter = counter + 1;
		raise notice '%', counter;

		if counter = 5 then
			exit;
		end if;
	end loop;
end $$;

-- single exit statement example

do $$
declare 
	counter int = 0;
begin
	loop
		counter = counter + 2;
		raise notice '%', counter;
	
		exit when counter = 6;
	end loop;
end $$;


-- using loop with label

do $$
declare
	counter int := 0;
begin
	<<my_loop>>
	loop
		counter = counter + 1;
		raise notice '%', counter;
		exit my_loop when counter = 5;
	end loop;
end $$;


-- nested loop example

do $$
declare
	row_var int := 0;
	col_var int := 0;
begin
	<<outer_loop>>
	loop
		row_var = row_var + 1;
		<<inner_loop>>
		loop
			col_var = col_var + 1;
			raise notice '(%, %)', row_var, col_var;

			exit inner_loop when col_var = 3;
		end loop;

		col_var = 0;

		exit outer_loop when row_var = 3;
	end loop;
end $$;
	