++++++++++++++++++
Notes on code test
++++++++++++++++++

Results
=======

Check the reports folder for three CSV files.  Hopefully, they have the
correct data.

How I did it
============

1.  Downloaded the CSV files into a folder named "datafiles".

2.  Made a new empty postgresql database::

        $ createdb splashfinancial

3.  Created two tables and loaded in spreadsheet data::

        $ psql splashfinancial -f make-splash-tables.sql

4.  Created a view named running_balances that figures out each user's
    balance on each day::

        $ psql splashfinancial -f make-running-balances.sql

5.  Manually spot-checked a few results::

        $ psql splashfinancial -c 'select * from running_balances where user_id in (6);'

6.  Wrote queries for each of the questions::

        $ psql splashfinancial -f users-with-penalties.sql
        $ psql splashfinancial -f highest-monthly-deposits.sql
        $ psql splashfinancial -f most-monthly-transactions.sql


Why did I do it in SQL?
=======================

Window functions are part of the ANSI standard SQL language and they
were designed **exactly for these kinds of problems** (running totals,
moving averages, trends, ranks, etc).

Many of my peers might do all this work in a general purpose programming
language.  There are a few reasons why that's a bad idea:

1.  Writing the logic to accumulate sums is tricky.  Meanwhile, there
    are dozens of excellent tutorials out for using window functions.

2.  Really smart programmers have been optimizing the window function
    internal code for **years** now.  A home-rolled solution will not
    likely run as fast.

    For 90 days * 100 accounts, you have at worst 10k combinations to
    worry about, so a slow implementation is fine.

    When you consider 3 years of data and a thousand accounts, you have
    a million combinations to consider.

3.  If we want to look at a 30-day or 90-day moving average, or many
    other windows of data, it would **trivial** to calculate those
    statistics with a windowing function, but not so easy with a
    home-rolled approach.

4.  Now, there's no internal software library to test and document.  We
    just need to tell new developers to read any tutorial on window
    functions and they can understand how to maintain and update this
    code.

    In fact, a savvy-enough business analyst could run these queries
    themselves.


Ideas for improvement
=====================

Add test data with expected results
-----------------------------------

English is vague!  It helps prevent wasted time when a description also
includes contrived sample data and expected results to test against.

Store the rules for programs in the database
--------------------------------------------

Right now, there's no table that describes what requirements for each
program.

A new program would require new queries to be written.

But imagine being able to insert a row for a new program, setting the
minimum monthly balance, minimum count of transactions, and minimum
total monthly deposits, and the system would automatically detect who
should be penalized.


.. vim: set syntax=rst:
