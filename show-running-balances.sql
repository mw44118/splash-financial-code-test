drop view if exists running_balances;

create view running_balances as

-- Creates a table with one row per day.
with days as (
    select generate_series(date '2017-01-01', '2017-04-01', interval '1 day')::date as dt
)

select days.dt, starting_balances.user_id, starting_balances.initial_amount, starting_balances.program, transactions.amount,

-- Accumulate all the transaction amounts.
sum(coalesce(transactions.amount, 0))
over (partition by starting_balances.user_id order by days.dt)
as total_amount,

-- Accumulate monthly deposits
sum(coalesce(transactions.amount, 0))
over (
	partition by starting_balances.user_id,
	date_trunc('month', days.dt)
	order by days.dt)
as total_deposits_for_month,

-- Add initial balance to accumulated transaction amounts.
starting_balances.initial_amount +
sum(coalesce(transactions.amount, 0))
over (partition by starting_balances.user_id order by days.dt)
as current_balance,

-- Count up each user's transactions so far for the month.
count(transactions)
over (
	partition by starting_balances.user_id, date_trunc('month', days.dt)
	order by days.dt)
as total_transaction_count_for_month,


case when days.dt =
(date_trunc('month', days.dt) + interval '1 month - 1 day')::date
then true
else false
end as is_last_day_of_month

from days

cross join starting_balances

left join transactions
on days.dt = transactions.transaction_date
and starting_balances.user_id = transactions.user_id

order by starting_balances.user_id, days.dt
;

-- Spot-check data
select * from running_balances where user_id in (6);


