# uno-telegram-bot

A UNO Telegram bot, currently on [@zeroxisbot](https://t.me/zeroxisbot). Made to be hosted on Heroku.

## How to play

With this bot, you can create and join rooms with other people and play UNO with them.

### Commands

**/new** - Creates a new room.

**/join** \<room_number\> - Joins a room with that number.

**/leave** - Leaves the current room. If no one is left in the room, it will self destruct.

**/begin** - Actually start the game.

**/end** - End the current game, losing all its data.

**/status** - Show information about the current room and the game if it began.

**/chat** \<message\> - Send a message to all other people in the room.

When in game, send a message with the following commands to play.

**[color]\<kind\>[new color]** - Discard a card from your hand with the color and kind. If kind is a +4 or Wild, don't set the color before, but you have to set the new chosen color afterwards.

Possible plays:
|Command|Meaning|
|-|-|
|[color]\<kind\>[new color]|Discard card with color and kind. If kind colorless, set chosen color afterwards.
|d|Draw cards from pile|
|p|Pass turn to next player|

Possible colors:
|Command|Meaning|
|-|-|
|b|Blue|
|g|Green|
|r|Red|
|y|Yellow|

Possible types:
|Command|Meaning|
|-|-|
|0..9|Numbered kinds|
|R|Reverse|
|S|Skip|
|+2|Draw 2|
|+4|Draw 4|
|W|Wild / Color Chooser|

Examples: **g6**, **rr**, **+4y**

### Rules

This bot tries to follow the official rules, but it might slightly diverge from them in some cases.

* On the start of the game, a card is set as the current in the discard pile. It must not be a +4 or Wild card.
* Each player receives 7 random cards.
* Other cards are placed in the draw pile.
* Each player is randomly assigned an order of play.
* At each turn, a player can discard a card if it matches the current card in either color or kind. Colorless cards can be played on top of any other. They can also draw one card from the draw pile, and then afterwards either play that card they drew (if possible) or pass the turn.
* If a Reverse card is played, the order of players is inverted. If there are only 2 players, it works the same as a skip card.
* If a Skip card is played, the next player does not play, only the player after them.
* If a Draw 2 card is played, the next player must either draw 2 cards from the draw pile and lose their turn, or play a Draw 2 or Draw 4 card.
* If a Draw card is played on top of a Draw 2 card, the number of cards to be drawn is added, and the next player will have to draw the total amount of cards or continue adding.
* No Draw cards can be played on top of Draw 4 card.
* If a Draw 4 or Wild card is played, the player must set a new color that card will represent, as the next player must match that color, unless they play a colorless card.
* The player that reaches 0 cards in their hand wins.

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