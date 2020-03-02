# uno-telegram-bot
A UNO Telegram bot, currently on [@zeroxisbot](https://t.me/zeroxisbot). Made to be hosted on Heroku.

## How to host

* Install the Python `requeriments.txt` with `pip install -r requirements.txt`. In Heroku that will be done automatically.

* Install PostgreSQL, set up a database and run `psql < database.sql`. In Heroku, you may install the Heroku Postgres add-on, and run `heroku pg:psql < database.sql`.

* Set up a bot in BotFather.

* Set up these enviroment variables in your server:
	* `TELEGRAM_BOT_TOKEN`: The Telegram bot's token, taken from BotFather.
	* `TELEGRAM_BOT_WEBHOOK`: The public URL of your server, with a trailing slash.
	* `DATABASE_URL`: A database URL containing the connection info, with the format `postgresql://user:password@host:port/databasename`. The Heroku Postgres add-on automatically creates this variable.
	* `PORT`: The host port that the public URL is listening from. Heroku will automatically create this variable.

* Start `main.py` file to host the bot. In Heroku, `Procfile` will take care of that.