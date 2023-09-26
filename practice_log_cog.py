import datetime
import json
from typing import Union

import discord
import discord.ext.commands as commands
import logmanager
import re


logs = discord.SlashCommandGroup("log", "Logging commands")
teams = discord.SlashCommandGroup("team", "Team related commands")
logger = logmanager.LogManager()

# ----------------------------------------------------------------------------------------------------------- Models ---
class TeamNotFoundException(Exception):
    def __init__(self):
        super().__init__("Could not find a team!")

# ------------------------------------------------------------------------------------------------ Utility Functions ---

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

def sort_teams_into_bad_and_good():
    most_recent_practices = {team: logger.get_most_recent_practice(team) for team in logger.team_name_to_id.values()}

    about_two_weeks_ago = datetime.date.today() - datetime.timedelta(14)

    guilty, innocent = [], []
    for team, practice in most_recent_practices.items():
        tup = (team, practice["Date"].strftime("%m/%d/%Y"))
        if practice["Date"] < about_two_weeks_ago:
            guilty.append(tup)
        else:
            innocent.append(tup)
    return guilty, innocent
# ----------------------------------------------------------------------------------------------------- Autocomplete ---

async def get_team_names(ctx: discord.AutocompleteContext):
    return [team for team in logger.team_name_to_id.keys() if team.lower().startswith(ctx.value.lower())]

units = [
    "hours",
    "games",
    "maps",
    "best-of"
]
async def get_unit_options(ctx: discord.AutocompleteContext):
    return [unit for unit in units if unit.startswith(ctx.value.lower())]

log_types = [
    "Practice",
    "Scrimmage",
    "Match"
]
async def get_log_type(ctx: discord.AutocompleteContext):
    return [log_type for log_type in log_types if log_type.startswith(ctx.value.lower())]

games_with_acronyms = [
    ["Rock Leg", "RL"],
    ["Valiant", "Val"],
    ["League of Legends (stinky)", "LoL"],
    ["Rainbow Dick Siege", "R6"],
    ["Apesex Legends", "Apex"],
    ["Kartio Mart", "MK8dlx"],
    ["Overwatch 1++", "OW2"],
    ["Call of Booty", "COD"],
    ["Counter-Stroke", "CS"],
    ["Other", "Other"]
]

game_acronym_map = {game: acronym for game, acronym in games_with_acronyms}

games = [
    name for name, acronym in games_with_acronyms
]
async def get_games(ctx: discord.AutocompleteContext):
    return [game for game in games if game.lower().startswith(ctx.value.lower())]

team_colors = [
    "Blue", "White", "Yellow", "Black"
]

async def get_team_color(ctx: discord.AutocompleteContext):
    return [color for color in team_colors if color.lower().startswith(ctx.value.lower())]

result_options = [
    "Win", "Loss", "N/A"
]

async def get_log_results(ctx: discord.AutocompleteContext):
    return [option for option in result_options if option.lower().startswith(ctx.value.lower())]

# --------------------------------------------------------------------------------------------------------- Commands ---

@teams.command(name="create", description="Creates a team.")  # guild_ids=[566299354088865812]
@discord.option(
    "team_name",
    str,
    description="The color of the team you are making. For example: Blue",
    required=True,
    autocomplete=discord.utils.basic_autocomplete(get_team_color)
)
@discord.option(
    "game",
    str,
    required=True,
    autocomplete=discord.utils.basic_autocomplete(get_games)
)
@discord.option(
    "add_self_to_team",
    bool,
    required=False
)
async def create_team(
        ctx,
        *,
        team_name,
        game: str = None,
        add_self_to_team: bool = False
):
    if game in games:
        game = game_acronym_map[game]
    elif game in game_acronym_map.values():
        game = game
    else:
        await ctx.respond("You must select a game from the list!")
        return

    if team_name not in team_colors:
        await ctx.respond("You must select a color from the list!")
        return

    team_name = f"{game} {team_name}"

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

@teams.command(name="get", description="Gets team info.")  # guild_ids=[566299354088865812]
@discord.option(
    "team_name",
    str,
    description="Optional: The name of the team you want to get.",
    autocomplete=discord.utils.basic_autocomplete(get_team_names),
    required=False
)
async def get_team_info(ctx: discord.ApplicationContext, *, team_name=None, team_id: int = None):

    try:
        team_id = get_team_id_using(team_id=team_id, team_name=team_name, ctx=ctx)
    except TeamNotFoundException:
        await ctx.respond("Could not find team! The command user must pass a team name, a team id, or be listed as a player on a team.")
        return

    team_info = logger.get_team(team_id=team_id)

    await ctx.respond(format_codeblock(format_json(team_info), "json"))

@teams.command(name="all", description="Gets team info.")  # guild_ids=[566299354088865812]
async def get_team_info(ctx: discord.ApplicationContext):
    await ctx.respond(format_codeblock(format_json(logger.teams), "json"))


def verify_parameters_for_log(ctx, result, unit, duration, str_date, team_id=None, team_name=None):
    if result not in result_options:
        return f"Result must be one of: {', '.join(result_options)}"
    if unit not in units:
        return f"Unit must be one of: {', '.join(units)}"
    try:
        duration = int(float(duration))
    except ValueError:
        return f"Duration must be formatted as an int or float."
    if str_date:
        m = re.match("\\d?\\d/\\d?\\d", str_date)
        if m:
            s, e = m.span()
            if not (s == 0 and e == len(str_date)):
                return f"Date was not formatted correctly"
        else:
            f"Date was not formatted correctly"
    try:
        team_id = get_team_id_using(team_id=team_id, team_name=team_name, ctx=ctx)
    except TeamNotFoundException:
        return "Could not find team! The command user must pass a team name, a team id, or be listed as a player on a team."

    return None

@logs.command(description="Logs a practice.")  # guild_ids=[566299354088865812]
@discord.option(
    "team_name",
    str,
    description="Optional: The name of the team you want to operate on.",
    autocomplete=discord.utils.basic_autocomplete(get_team_names),
    required=False
)
@discord.option(
    "duration",
    float,
    description="The number of units you played. For example: \"2\" hours or a Best-of \"5\"",
    required=True
)
@discord.option(
    "unit",
    str,
    description="The unit of time you're measuring your practice in. For example \"hours\" or \"best-of\".",
    required=True,
    autocomplete=discord.utils.basic_autocomplete(get_unit_options)
)
@discord.option(
    "date_of",
    str,
    description="Date formatted as Month/Day. For example: 6/9 or 4/20",
    required=True
)
@discord.option(
    "result",
    str,
    description="Did you win, lose, or is it not applicable? Default is N/A",
    required=False,
    autocomplete=discord.utils.basic_autocomplete(get_log_results)
)
async def practice(ctx, *, date_of: str, duration: float, unit: str, result: str = "N/A", team_id: int = None, team_name=None):

    error = verify_parameters_for_log(ctx, result, unit, duration, date_of, team_id, team_name)
    if error:
        await ctx.respond(error)
        return

    team_id = get_team_id_using(team_id=team_id, team_name=team_name, ctx=ctx)

    if date_of:
        if date_of.count("/") < 2:
            date_of += f"/{datetime.date.today().year}"
        date_of = datetime.datetime.strptime(date_of, "%m/%d/%Y").date()

        # Handling the case that the date was last year (such as in December)
        if datetime.date.today() - date_of < datetime.timedelta(0):
            date_of = f"{date_of.strftime('%m/%d')}/{date_of.year - 1}"  # Removing 1 from the year
            date_of = datetime.datetime.strptime(date_of, "%m/%d").date()
    else:
        date_of = datetime.date.today()

    duration = f"{duration} {unit}" if unit != "best-of" else f"{unit}-{duration}"

    logger.add_log(team_id, date_of, duration, "Practice", ctx.author.name, result)

    await ctx.respond("Logged practice")


@logs.command(description="Logs a scrimmage.")  # guild_ids=[566299354088865812]
@discord.option(
    "team_name",
    str,
    description="Optional: The name of the team you want to operate on.",
    autocomplete=discord.utils.basic_autocomplete(get_team_names),
    required=False
)
@discord.option(
    "duration",
    float,
    description="The number of units you played. For example: \"2\" hours or a Best-of \"5\"",
    required=True
)
@discord.option(
    "unit",
    str,
    description="The unit of time you're measuring your practice in. For example \"hours\" or \"best-of\".",
    required=True,
    autocomplete=discord.utils.basic_autocomplete(get_unit_options)
)
@discord.option(
    "date_of",
    str,
    description="Date formatted as Month/Day. For example: 6/9 or 4/20",
    required=True
)
@discord.option(
    "result",
    str,
    description="Did you win, lose, or is it not applicable? Default is N/A",
    required=False,
    autocomplete=discord.utils.basic_autocomplete(get_log_results)
)
@discord.option(
    "opponent_name",
    str,
    description="Optional: The name of the team you scrimmed against.",
    required=False
)
async def scrim(ctx, *, date_of: str, duration: float, unit: str, result: str = "N/A", opponent_name: str = None, team_id: int = None, team_name=None):

    error = verify_parameters_for_log(ctx, result, unit, duration, date_of, team_id, team_name)
    if error:
        await ctx.respond(error)
        return

    team_id = get_team_id_using(team_id=team_id, team_name=team_name, ctx=ctx)

    if date_of:
        if date_of.count("/") < 2:
            date_of += f"/{datetime.date.today().year}"
        date_of = datetime.datetime.strptime(date_of, "%m/%d/%Y").date()

        # Handling the case that the date was last year (such as in December)
        if datetime.date.today() - date_of < datetime.timedelta(0):
            date_of = f"{date_of.strftime('%m/%d')}/{date_of.year - 1}"  # Removing 1 from the year
            date_of = datetime.datetime.strptime(date_of, "%m/%d").date()
    else:
        date_of = datetime.date.today()

    duration = f"{int(duration)} {unit}" if unit != "best-of" else f"{unit}-{duration}"

    logger.add_log(team_id, date_of, duration, "Scrimmage", ctx.author.name, result, opponent_name)

    await ctx.respond("Logged scrim")


@teams.command(description="Adds a player to a team.")  # guild_ids=[566299354088865812]
@discord.option(
    "team_name",
    str,
    description="Optional: The name of the team you want to operate on.",
    autocomplete=discord.utils.basic_autocomplete(get_team_names),
    required=False
)
async def add_player(ctx, *, player: discord.Member, team_id: int = None, team_name=None):
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

@teams.command(description="Removes a player from a team.")  # guild_ids=[566299354088865812]
@discord.option(
    "team_name",
    str,
    description="Optional: The name of the team you want to operate on.",
    autocomplete=discord.utils.basic_autocomplete(get_team_names),
    required=False
)
async def remove_player(ctx, *, player: discord.Member, team_id: int = None, team_name=None):
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

@logs.command(description="Returns csv containing practices for a team.")  # guild_ids=[566299354088865812]
@discord.option(
    "team_name",
    str,
    description="Optional: The name of the team you want to operate on.",
    autocomplete=discord.utils.basic_autocomplete(get_team_names),
    required=False
)
async def get_log(ctx, *, team_name=None, team_id: int = None):
    try:
        team_id = get_team_id_using(team_id=team_id, team_name=team_name, ctx=ctx)
    except TeamNotFoundException:
        await ctx.respond(
            "Could not find team! The command user must pass a team name, a team id, or be listed as a player on a team.")
        return

    file_path = logger.get_log_file(id=team_id)
    await ctx.respond(file=discord.File(file_path))


@logs.command(description="Returns csv containing practices for a team.")  # guild_ids=[566299354088865812]
@discord.option(
    "team_name",
    str,
    description="Optional: The name of the team you want to operate on.",
    autocomplete=discord.utils.basic_autocomplete(get_team_names),
    required=False
)
async def get_most_recent(ctx, *, team_name=None, team_id: int = None):
    try:
        team_id = get_team_id_using(team_id=team_id, team_name=team_name, ctx=ctx)
    except TeamNotFoundException:
        await ctx.respond(
            "Could not find team! The command user must pass a team name, a team id, or be listed as a player on a team.")
        return

    most_recent = logger.get_most_recent_practice(team_id)

    most_recent["Date"] = most_recent["Date"].strftime("%m/%d/%Y")
    most_recent["Submitted On"] = most_recent["Submitted On"].strftime("%m/%d/%Y")

    await ctx.respond(
        format_codeblock(
            format_json(most_recent),
            "json"
         )
    )

@logs.command(description="Calls out teams which have not practiced.")  # guild_ids=[566299354088865812]
@discord.default_permissions(manage_messages=True)
async def snitch(ctx: discord.ApplicationContext):
    await ctx.respond("Snitching on these bitches...")

    guilty, innocent = sort_teams_into_bad_and_good()

    inverse_map = logger.get_inverse_team_map()

    guilty = "\n\t".join([f"{inverse_map[team_id]}: {last_practice_date}" for team_id, last_practice_date in guilty])
    innocent = "\n\t".join([f"{inverse_map[team_id]}: {last_practice_date}" for team_id, last_practice_date in innocent])

    response = f"Guilty Mfers:\n\t{guilty}\nInnocent Angels:\n\t{innocent}"

    await ctx.respond(content=format_codeblock(response))

@logs.command(description="Pings teams which have not practiced.")  # guild_ids=[566299354088865812]
@discord.default_permissions(manage_messages=True)
async def ping_baddies(ctx: discord.ApplicationContext):
    guilty, innocent = sort_teams_into_bad_and_good()
    inverse_map = logger.get_inverse_team_map()

    to_ping = {team_id: logger.get_team(team_id)["players"] for team_id, last_practice in guilty}

    if len(to_ping) == 0:
        await ctx.respond("There are no baddies!!!")
        return

    msg = "The following teams need to practice:\n"
    for team_id, players in to_ping.items():
        msg += f"**{inverse_map[team_id]}**:\n\t" + "\n\t".join([f"<@{player}>" for player in players]) + "\n"

    await ctx.respond(msg)
