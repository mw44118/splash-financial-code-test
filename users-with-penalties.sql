-- These are the program 1 users that have penalties
select *
from running_balances
where program = '1'
and is_last_day_of_month = true

and (
    total_transaction_count_for_month < 5
    and total_deposits_for_month < 300
    and current_balance < 1200)

order by dt, user_id
;

-- These are program 2 users with penalties
