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

