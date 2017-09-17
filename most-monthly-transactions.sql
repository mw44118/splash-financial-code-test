drop view if exists most_monthly_transactions cascade;

create view most_monthly_transactions
as

with max_for_month as (

    select dt, user_id, total_transaction_count_for_month,

    max(total_transaction_count_for_month) over (partition by dt)
    as max_for_month

    from running_balances
    where is_last_day_of_month = true

)

select dt, user_id, total_transaction_count_for_month
from max_for_month
where total_transaction_count_for_month = max_for_month
order by dt;
;

select *
from most_monthly_transactions
;

