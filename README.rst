++++++++++++++++++
Notes on code test
++++++++++++++++++

How I did it
============

1.  Downloaded the CSV files into a folder named "datafiles".

2.  Made a new empty postgresql database::

        $ createdb splashfinancial

3.  Created two tables and loaded in spreadsheet data::

        drop table if exists starting_balances cascade;

        create table starting_balances
        (
            user_id integer not null,
            initial_amount numeric not null,
            program text not null
        );

        \copy starting_balances from 'datafiles/StartingData.csv' with csv header;

        drop table if exists transactions;

        create table transactions
        (
            transaction_date date not null,
            user_id integer not null,
            amount numeric
        );

        \copy transactions from 'datafiles/Jan.csv' with csv header;
        \copy transactions from 'datafiles/Feb.csv' with csv header;
        \copy transactions from 'datafiles/Mar.csv' with csv header;

4.  Created a view named running_balances that calculates the current
    balance for each user every day::

        create view running_balances as

        -- Create a table with one row per day.
        with days as (
            select generate_series(
                date '2017-01-01',  -- starting value
                date '2017-04-01',  -- ending value
                interval '1 day'    -- increment
            )::date as dt
        )

        select days.dt, starting_balances.user_id,
        starting_balances.initial_amount, starting_balances.program,
        transactions.amount,

        -- Accumulate all the transaction amounts.
        sum(coalesce(transactions.amount, 0))
        over (partition by starting_balances.user_id order by days.dt)
        as total_amount,

        starting_balances.initial_amount +
        sum(coalesce(transactions.amount, 0))
        over (partition by starting_balances.user_id order by days.dt)
        as current_balance

        from days

        cross join starting_balances

        left join transactions
        on days.dt = transactions.transaction_date
        and starting_balances.user_id = transactions.user_id

        order by starting_balances.user_id, days.dt

        ;


6.  Wrote results for a few users to a spreadsheet so I could spot-check
    the results::

        \copy (
            select * from running_balances
            where running_balances.user_id in (149, 13, 103, 6)
        ) to stdout with csv header;

Concerns
========

Deposits: net or gross?
-----------------------

It isn't clear from the instructions if I can deposit $800 and withdraw
$799 each month and still avoid penalties.

When are penalties applied?
----------------------

It isn't clear when to apply penalties and penalties might set up more
penalties in the next month.  Since I have data through the end of
March, and no sign of penalties, I imagine they don't care

Users can't change programs
---------------------------

This data layout (program stored with starting balances) prevents people
from switching at a point in time.

Why did I do it in SQL?
=======================

MySQL, Access, and SQLite, for example, do not support SQL window
functions.  but window functions are part of the ANSI standard SQL
language and they were designed **exactly for these kinds of problems**
(running totals, moving averages, trends, ranks, etc).

Many of my peers might do all this work in a general purpose programming
language.  There are a few reasons why that's a bad idea:

1.  Writing the logic to accumulate sums is tricky.  Meanwhile, there
    are dozens of excellent tutorials out for using window functions.

2.  Really smart programmers have been optimizing the window function
    internal code for **years** now.  A home-rolled solution will not
    likely run as fast and may even fail when given unexpected inputs
    (like leap days, for example).

3.  Home-rolled code is not as flexible.  Right now, the program rules
    look at the balance on the last day of the month.  But if we want to
    look at a 30-day or 90-day moving average, it would **trivial** to
    calculate those statistics with a windowing function, but not so
    easy with a home-rolled approach.

4.  Now, there's no internal software library to support.  We just need
    to tell new developers to read any tutorial on window functions and
    they can understand how to maintain and update this code.

    In fact, a savvy-enough business analyst could be given read-only
    access to the database and run these queries themselves.


If I had more time...
=====================

Add test data with expected results
-----------------------------------

It helps when a description also includes some contrived sample data and
some expected results to test against.

During development, I can run input data through the system and compare
the calculated results vs the expected results.

I'll either discover a bug in the software or vagueness in the
description of how the software ought to work (for example, net or gross
deposits, or any vs all.

Store the rules for programs in the database
--------------------------------------------





.. vim: set syntax=rst:
