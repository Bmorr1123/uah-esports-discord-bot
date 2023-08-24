import discord
import discord.ext.commands as commands

class PracticeLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.Cog.listener()
    # async def on_member_join(self, member):
    #     channel = member.guild.system_channel
    #     if channel is not None:
    #         await channel.send(f'Welcome {member.mention}.')

    @commands.slash_command(description="Logs a practice", guild_ids=[566299354088865812])
    async def log(self, ctx, *, member: discord.Member = None):
        await ctx.respond("Log")
