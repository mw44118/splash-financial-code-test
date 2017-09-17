drop view if exists highest_monthly_deposits cascade;

create view highest_monthly_deposits
as

with max_for_month as (

    select dt, user_id, total_deposits_for_month,

    max(total_deposits_for_month) over (partition by dt)
    as max_for_month

    from running_balances
    where is_last_day_of_month = true

)

select dt, user_id, total_deposits_for_month
from max_for_month
where total_deposits_for_month = max_for_month
order by dt;
;

\copy (select * from highest_monthly_deposits) to 'reports/highest-monthly-deposits.csv' with csv header;
