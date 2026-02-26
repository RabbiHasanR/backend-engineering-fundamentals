-- simple case statement

do $$
declare
	rate payment_api_ratemodel.bdt_rate%type;
	price_segment varchar(50);
begin
	select bdt_rate into rate
	from payment_api_ratemodel
	where id = 1;

	if found then
		case rate
			when 120 then
				price_segment = 'Mass';
			when 299 then
				price_segment = 'Mainstream';
			when 499 then
				price_segment = 'High End';
			else
				price_segment = 'Unspecified';
			end case;

		raise notice '%', price_segment;
	else
		raise notice 'rate not found';
	end if;
end $$;


-- searched case statement
do $$
declare
	total_rate numeric;
	service_level varchar(25);
begin
	select sum(bdt_rate) into total_rate
	from payment_api_ratemodel
	where id = 1;

	if found then
		case
			when total_rate > 200 then
				service_level = 'Platinum';
			when total_rate > 100 then
				service_level = 'Gold';
			else
				service_level = 'Silver';
		end case;
		raise notice 'Service Level: %', service_level;
	else
		raise notice 'Rate not found';
	end if;
end $$;
