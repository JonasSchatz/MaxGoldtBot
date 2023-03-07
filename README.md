# MaxGoldtBot

This is a Reddit bot. It reads all submissions and comments from a subreddit and
checks if they contain any links to bild.de. If so, the bot responds with the
following quote from German writer Max Goldt:

> Diese Zeitung ist ein Organ der Niedertracht. Es ist falsch, sie zu lesen.
> Jemand, der zu dieser Zeitung beiträgt, ist gesellschaftlich absolut
> inakzeptabel. Es wäre verfehlt, zu einem ihrer Redakteure freundlich oder auch
> nur höflich zu sein. Man muß so unfreundlich zu ihnen sein, wie es das Gesetz
> gerade noch zuläßt. Es sind schlechte Menschen, die Falsches tun.

The response comment will also contain archive.is versions of the linked bild.de
articles, so that future readers are not forced to visit bild.de if they want
to read the article.

This program is licensed under the MIT license, see the LICENSE file. To see what
has changed over time, have a look at
[CHANGELOG.md](https://github.com/jonasschatz/MaxGoldtBot/blob/master/CHANGELOG.md).

## Prerequisites

To run this bot, you will need:

- Python 3 (tested with 3.9 on MacOS)
- The following packages (install via `pip` / `pip3`):
  - `archiveis` (a simple wrapper for archive.is)
  - `praw` (the Python Reddit wrapper)
- Docker / docker-compose. While the latter might seem like overkill, it is a very
  convenient way to set up the bot with the correct configuration.

## Configuration

The sample configuration file (`.env.sample`) should give you a good
idea of what you need to configure to make this bot work. Rename it to `.env` to
make it work. The configuration file should contain the following items:

- **`client_id`** -- this is the ID of your Reddit application. To obtain one,
  go to reddit.com > preferences > apps (old reddit) or User Settings > Safety &
  Privacy > Manage third-party app authorization (new reddit) and create a new
  app of type "script". The client ID is displayed beneath your application's name.
- **`client_secret`** -- this is the secret key of your Reddit application.
  Never let anyone see this! You can find it in the details of your app under
  reddit.com > preferences > apps.
- **`user_agent`** -- this is a User-Agent string that the bot will provide to
  Reddit when making requests. Generally, the user agent string should have the
  following format:
  `platform:tld.yourdomain.yourapp:vX.Y.Z (by /u/YourUsername)`
- **`username`** -- this is the username of your Reddit bot.
- **`password`** -- this is your Reddit bot's password. Without it, the bot can
  read Reddit comments, but cannot reply to them.
- **`subreddit`** -- The subreddit the bot should be active on, e.g. `"test"`.
  Make sure to ask the Mod's permission before you let it loose. On
  [r/de](www.reddit.com/r/de) it is not allowed due to source derailment.

## Deployment

After entering your details in the `.env` file, you can run the bot by simply
running `docker compose up` in your terminal.

## Subreddit

This bot has its own subreddit where you can ask questions and make suggestions:
[/r/MaxGoldtBot](https://www.reddit.com/r/MaxGoldtBot)
