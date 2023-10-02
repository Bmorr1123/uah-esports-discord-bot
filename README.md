# uah-esports-discord-bot
This bot will track the practice logs and more for the UAH Esports discord.

# How to use the Practice Log functionality of the bot
## Create a team. The command is `/team create`
- Make sure to choose the correct team color
- Make sure to select the correct esport
- If you are planning to do the logs for the team, I would recommend adding yourself to the team. *if you do not do this now, you can still do it later using /team add_player*

## Use the command `/log scrim` or `/log practice`
- Select the correct log type. (Practice or Scrimmage) *games will be implemented later*
- Date is formatted MM/DD *it can be 1/2 or 01/05, as long as they are valid numbers*
- Duration is the amount of practice you got, and you select the unit for the duration in the next parameter
- Unit is the type of duration. It can be `Hours, Maps, Games, or a Best-of`. Choose whatever makes the most sense.
### Optional:
- Result is really only applicable for Scrimmages or Matches. Avoid this for the time being please.
- Team_name and team_id allow you to specify which team you'd like to log a practice for. If you do not specify, it will do whatever team you are on. *(and might error if you're on multiple teams oops)*

## How to check your log. There are two ways.
- `/log get_log`: This returns the .csv containing all logged info for your team.
- `/log get_most_recent`: This returns a json object representing your most recent practice.

## How to add players `/team add_player`
- Just tag the player you want to join, and the command will return an updated team object. The players discord ID will be in the list, rather than their username.
- You do **NOT** need to add all players. It just makes it easier for the players to log matches.

I hope this is helpful, if something breaks on you, please hesitate to contact me.
