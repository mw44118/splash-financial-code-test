++++++++++++++++++
Notes on code test
++++++++++++++++++

How I did it
============

1.  Downloaded the CSV files into a folder named "datafiles".

2.  Made a new empty postgresql database::

        $ createdb splashfinancial

3.  Created two tables and loaded in spreadsheet data::

        $ psql splashfinancial -f make-splash-tables.sql

4.  Created a view named running_balances that figures out each user's
    balance on each day.

5.  Manually spot-checked a few results.

6.  Wrote queries for each of the questions.

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


Ideas for improvement
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

Right now, there's no table that describes what program one's
requirements are.

Imagine being able to insert a row for a new program, setting the
minimum monthly balance, minimum count of transactions, and minimum
total monthly deposits, and the system would automatically detect who
should be penalized.







.. vim: set syntax=rst:
