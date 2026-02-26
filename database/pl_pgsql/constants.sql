-- constant example

do $$
declare
	vat constant numeric = 0.1;
	net_price numeric = 20.5;
begin
	raise notice 'The selling price is %', net_price * ( 1 + vat );
end $$;

-- similar to the default value of a variable, postgresql evaluated the value for the constant when the block is entered at run-time
-- not compile-time

do $$
declare
	started_at constant time := clock_timestamp();
begin
	perform pg_sleep(3);

	raise notice '3s later';
	raise notice 'Current time: %', clock_timestamp();

	perform pg_sleep(3);
	raise notice 'Started at: %', started_at;
end $$;