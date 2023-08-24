import os, discord
import discord.ext.commands as commands
import practice_log_cog

class EsportsBot(commands.Bot):
    async def on_ready(self):
        print(f"Logged in as {self.user.name} ({self.user.id})")



def main():
    token = os.getenv("UAH_ESPORTS_TOKEN")

    intents = discord.Intents.default()

    bot = EsportsBot()
    bot.add_cog(practice_log_cog.PracticeLogs(bot))
    bot.run(token)


if __name__ == '__main__':
    main()

