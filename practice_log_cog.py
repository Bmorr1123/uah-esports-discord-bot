import json
from typing import Union

import discord
import discord.ext.commands as commands
import logmanager

class PracticeLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logs = logmanager.LogManager()

    # @commands.Cog.listener()
    # async def on_member_join(self, member):
    #     channel = member.guild.system_channel
    #     if channel is not None:
    #         await channel.send(f'Welcome {member.mention}.')

    @commands.slash_command(description="Creates a team", guild_ids=[566299354088865812])
    async def create_team(
            self,
            ctx,
            *,
            team_name: str,
            team_id: int = None,
            # users: list[discord.Member] = None,
            game: str = None
    ):
        """
        This function creates a team.
        :param ctx:
        :param team_name: The name of the team.
        :param team_id: Optional: The id of the team.
        :param game: Optional: The game the team plays.
        :return: The created team's info.
        """
        team_id = self.logs.create_team(team_name=team_name, id=team_id, game=game)
        await ctx.respond(self.format_codeblock(
            self.format_json(
                self.logs.get_team(team_id=team_id)
            ),
            "json"
        ))

    @commands.slash_command(description="Gets team info", guild_ids=[566299354088865812])
    async def get_team_info(self, ctx: discord.ApplicationContext, *, team_name: str = None, team_id: int = None):
        if team_name:
            if team_name in self.logs.name_map:
                team_id = self.logs.name_map[team_name]
        if not team_id:
            author: discord.Member | discord.User = ctx.author
            if author.id in self.logs.player_map:
                team_id = self.logs.player_map[author.id]

        team_info = self.logs.get_team(team_id=team_id)

        await ctx.respond(self.format_codeblock(self.format_json(team_info), "json"))

    @commands.slash_command(description="Logs a practice", guild_ids=[566299354088865812])
    async def log(self, ctx, *, member: discord.Member = None):
        await ctx.respond("Log")

    def format_json(self, data):
        return json.dumps(data, indent=4)

    def format_codeblock(self, code, language=None):
        return f"```{language if language else ''}\n{code}```"
