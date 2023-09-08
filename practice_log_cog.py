import datetime
import json
from typing import Union

import discord
import discord.ext.commands as commands
import logmanager


logs = discord.SlashCommandGroup("logs", "Logging commands")
logger = logmanager.LogManager()

class TeamNotFoundException(Exception):
    def __init__(self):
        super().__init__("Could not find a team!")

def format_json(data):
    return json.dumps(data, indent=4)

def format_codeblock(code, language=None):
    return f"```{language if language else ''}\n{code}```"

def get_team_id_using(team_id: int = None, team_name: str = None, ctx: discord.ApplicationContext = None):
    if team_id is None:
        if team_name in logger.team_name_to_id:
            return logger.team_name_to_id[team_name]
        elif ctx.author.id in logger.player_map:
            return logger.player_map[ctx.author.id]
        raise TeamNotFoundException()

    return team_id

@logs.command(description="Creates a team.", guild_ids=[566299354088865812])
async def create_team(
        ctx,
        *,
        team_name: str,
        # users: list[discord.Member] = None,
        game: str = None,
        add_self_to_team: bool = False
):
    """
    This function creates a team.

    :param ctx:
    :param team_name: The name of the team.
    :param team_id: Optional: The id of the team.
    :param game: Optional: The game the team plays.
    :param add_self_to_team: Optional: Whether to add the caller of the command to the team.
    :return: The created team's info.
    """
    team_id = logger.create_team(team_name=team_name, game=game)

    if add_self_to_team:
        print(team_id, ctx.author.id)
        logger.add_player_to_team(team_id, ctx.author.id)

    await ctx.respond(format_codeblock(
        format_json(
            logger.get_team(team_id=team_id)
        ),
        "json"
    ))

@logs.command(description="Gets team info.", guild_ids=[566299354088865812])
async def get_team_info(ctx: discord.ApplicationContext, *, team_name: str = None, team_id: int = None):

    try:
        team_id = get_team_id_using(team_id=team_id, team_name=team_name, ctx=ctx)
    except TeamNotFoundException:
        await ctx.respond("Could not find team! The command user must pass a team name, a team id, or be listed as a player on a team.")
        return

    team_info = logger.get_team(team_id=team_id)

    await ctx.respond(format_codeblock(format_json(team_info), "json"))

@logs.command(description="Logs a practice.", guild_ids=[566299354088865812])
async def log(ctx, *, practice_type: str, practice_date: str, duration: int, team_id: int = None, team_name: str = None):
    """

    :param ctx:
    :param practice_type:
    :param practice_date:
    :param duration:
    :param team_id:
    :param team_name:
    :return:
    """
    try:
        team_id = get_team_id_using(team_id=team_id, team_name=team_name, ctx=ctx)
    except TeamNotFoundException:
        await ctx.respond(
            "Could not find team! The command user must pass a team name, a team id, or be listed as a player on a team.")
        return

    if practice_date:
        practice_date += f"/{datetime.date.today().year}"
        try:
            date = datetime.datetime.strptime(practice_date, "%m/%d/%Y").date()

            # Handling the case that the date was last year (such as in December)
            if datetime.date.today() - date < datetime.timedelta(0):
                practice_date = f"{date.strftime('%m/%d')}/{date.year - 1}"  # Removing 1 from the year
                date = datetime.datetime.strptime(practice_date, "%m/%d").date()
        except Exception:
            await ctx.respond("Date was formatted incorrectly. Please input a date in format MM/DD.")
            return
    else:
        date = datetime.date.today()

    logger.log_practice(team_id, date, duration, practice_type, ctx.author.name)

    await ctx.respond("Logged practice")

@logs.command(description="Adds a player to a team.", guild_ids=[566299354088865812])
async def add_player(ctx, *, player: discord.Member, team_id: int = None, team_name: str = None):
    try:
        team_id = get_team_id_using(team_id=team_id, team_name=team_name, ctx=ctx)
    except TeamNotFoundException:
        await ctx.respond(
            "Could not find team! The command user must pass a team name, a team id, or be listed as a player on a team.")
        return

    if not isinstance(player, int):
        player = player.id
    await ctx.respond(
        format_codeblock(
            format_json(
                logger.add_player_to_team(team_id, player)
            ),
            "json"
        )
    )

@logs.command(description="Adds a player to a team.", guild_ids=[566299354088865812])
async def remove_player(ctx, *, player: discord.Member, team_id: int = None, team_name: str = None):
    try:
        team_id = get_team_id_using(team_id=team_id, team_name=team_name, ctx=ctx)
    except TeamNotFoundException:
        await ctx.respond(
            "Could not find team! The command user must pass a team name, a team id, or be listed as a player on a team.")
        return

    if not isinstance(player, int):
        player = player.id
    await ctx.respond(
        format_codeblock(
            format_json(
                logger.remove_player_from_team(team_id, player)
            ),
            "json"
        )
    )

@logs.command(description="Returns csv containing practices for a team.", guild_ids=[566299354088865812])
async def get_log(ctx, *, team_name: str = None, team_id: int = None):
    try:
        team_id = get_team_id_using(team_id=team_id, team_name=team_name, ctx=ctx)
    except TeamNotFoundException:
        await ctx.respond(
            "Could not find team! The command user must pass a team name, a team id, or be listed as a player on a team.")
        return

    file_path = logger.get_log_file(id=team_id)
    await ctx.respond(file=discord.File(file_path))


@logs.command(description="Returns csv containing practices for a team.", guild_ids=[566299354088865812])
async def get_most_recent(ctx, *, team_name: str = None, team_id: int = None):
    try:
        team_id = get_team_id_using(team_id=team_id, team_name=team_name, ctx=ctx)
    except TeamNotFoundException:
        await ctx.respond(
            "Could not find team! The command user must pass a team name, a team id, or be listed as a player on a team.")
        return

    most_recent = logger.get_most_recent_practice(team_id)

    most_recent["Date"] = most_recent["Date"].strftime("%m/%d/%Y")
    most_recent["Submitted At"] = most_recent["Submitted At"].strftime("%m/%d/%Y")

    await ctx.respond(
        format_codeblock(
            format_json(most_recent),
            "json"
         )
    )

@logs.command(description="Calls out teams which have not practiced.", guild_ids=[566299354088865812])
async def snitch(ctx: discord.ApplicationContext):
    response_obj = await ctx.respond("Snitching on these bitches...")
    most_recent_practices = {team: logger.get_most_recent_practice(team) for team in logger.team_name_to_id.values()}

    about_two_weeks_ago = datetime.date.today() - datetime.timedelta(14)

    guilty, innocent = [], []
    for team, practice in most_recent_practices.items():
        tup = (team, practice["Date"].strftime("%m/%d/%Y"))
        if practice["Date"] < about_two_weeks_ago:
            guilty.append(tup)
        else:
            innocent.append(tup)

    inverse_map = logger.get_inverse_team_map()

    guilty = "\n\t".join([f"{inverse_map[team_id]}: {last_practice_date}" for team_id, last_practice_date in guilty])
    innocent = "\n\t".join([f"{inverse_map[team_id]}: {last_practice_date}" for team_id, last_practice_date in innocent])

    response = f"Guilty Mfers:\n\t{guilty}\nInnocent Angels:\n\t{innocent}"

    await ctx.respond(content=format_codeblock(response))



