# How to make an update

## Set up variables

* `set PGUSER=postgres` - local postgres user
* `set PGPASSWORD=password` - local postgres password
* `set PGDATABASE=unotelegrambot` - local postgres database name
* `set UNO_SQL_UPDATE=<number>` - which update file number to use

## Writing the code

* Modify all the code you want, make a `sql-updates\%UNO_SQL_UPDATE%.sql` file.

## Apply changes to database locally

* `heroku update`
* `heroku config:get DATABASE_URL > DATABASE_URL.txt`
* `set /P DATABASE_URL=< DATABASE_URL.txt`
* `del DATABASE_URL.txt`
* `pg_dump --schema-only --no-privileges --no-owner -f database_heroku.sql "%DATABASE_URL%"`
* `dropdb %PGDATABASE%`
* `createdb %PGDATABASE%`
* `psql -f database_heroku.sql`
* `psql -f sql-updates\%UNO_SQL_UPDATE%.sql`
* `pg_dump --schema-only --no-privileges --no-owner -f database.sql`

## Add database.sql and others

* Stage all the code related to database changes
* `git add database.sql`
* `git commit -m "Dumb message"`
* `git push`

## Deploy

* `heroku ps:scale web=0`
* `heroku pg:psql < sql-updates\%UNO_SQL_UPDATE%.sql`
* Do manual deploy on Heroku dashboard
* `heroku ps:scale web=1`