drop view if exists program_one_penalties cascade;

create view program_one_penalties
as
select user_id, program, dt,
total_transaction_count_for_month,
5 as minimum_transactions_per_month,

total_deposits_for_month,
300 as minimum_deposits_for_month,

current_balance,
1200 as minimum_end_of_month_balance,

8 as penalty,

case when (
    total_transaction_count_for_month < 5
    and total_deposits_for_month < 300
    and current_balance < 1200)
then true
else false
end as apply_penalty

from running_balances
where program = 1
and is_last_day_of_month = true

order by dt, user_id
;

drop view if exists program_two_penalties cascade;

create view program_two_penalties
as
select user_id, program, dt,
total_transaction_count_for_month,
1 as minimum_transactions_per_month,

total_deposits_for_month,
800 as minimum_deposits_for_month,

current_balance,
5000 minimum_end_of_month_balance,

4 as penalty,

case when (
    total_transaction_count_for_month < 1
    and total_deposits_for_month < 800
    and current_balance < 5000)
then true
else false
end as apply_penalty

from running_balances
where program = 2
and is_last_day_of_month = true

order by dt, user_id
;

drop view if exists program_penalties;

create view program_penalties
as
select * from program_one_penalties
union
select * from program_two_penalties

order by dt, user_id, program
;

drop view if exists total_per_user_penalties;

create view total_per_user_penalties
as
select user_id, program, sum(penalty) as total_penalties
from program_penalties
where apply_penalty = true

group by 1, 2

order by 2, 1
;

select * from total_per_user_penalties;
