-- to get the latest reults from mysql into 
-- the materialized or cached view, we need to refresh it 

refresh materialized view msql_results;

-- insert missing results
insert into public.results
select 
	a.*
from 
	msql_results a 
where
	a."timestamp" > (select
						b."timestamp"
					from
						results b
					order by
						b."timestamp" desc
					limit
						1);

--##################################################
--18-146471-122005	1550058728756
-- latest timestamp
select 
	to_timestamp(1550058728.756);


--18-123094-124719	1468582484160
-- first timestamp
select 
	to_timestamp(1468582484.160);
