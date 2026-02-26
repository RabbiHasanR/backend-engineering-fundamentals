-- exit statement to terminate unconditional loop
do $$
declare
	i int = 0;
	j int = 0;
begin
	<<outer_loop>>
	loop
		i = i + 1;
		exit when i > 3;
		j = 0;
		<<inner_loop>>
		loop
			j = j + 1;
			exit when j > 3;
			raise notice '(i,j): (%,%)', i, j;
		end loop inner_loop;
	end loop outer_loop;
end $$;

-- following example places the label of the outer loop in the second exit statement:

do $$
declare
	i int = 0;
	j int = 0;
begin
	<<outer_loop>>
	loop
		i = i + 1;
		exit when i > 3;

		j = 0;
		<<inner_loop>>

		loop
			j = j + 1;
			exit outer_loop when j > 3;
			raise notice '(i,j): (%,%)', i, j;
		end loop inner_loop;
	end loop outer_loop;
end $$;


-- using exit statement to exit a block

do $$
begin
	<<simple_block>>
	begin
		exit simple_block;
			-- for demo purpose
		raise notice '%', 'unreachable!';
	end;
	raise notice '%', 'End of block';
end $$;
	