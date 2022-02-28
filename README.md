# Bellingcat Discord Bot

``` shell
virtualenv env
source env/bin/activate
set -x DISCORD_TOKEN ...
set -x DISCORD_APP_ID ...
make models # just need to run once, or if MODELS list changes
make run
```

Then message the bot (either via direct message or by mentioning it)
with the command `help` to see all that can be done.

# License
Copyright &copy; 2022 Josh Junon. Released under the [MIT License](LICENSE).

Written for [Bellingcat](https://www.bellingcat.com/).
