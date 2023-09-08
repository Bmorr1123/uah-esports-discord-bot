import os, discord
import discord.ext.commands as commands
import practice_log_cog

class EsportsBot(commands.Bot):
    async def on_ready(self):
        print(f"Logged in as {self.user.name} ({self.user.id})")


def main():
    token = os.getenv("UAH_ESPORTS_TOKEN")
    intents = discord.Intents.default()

    bot = EsportsBot(intents=intents)
    bot.add_application_command(practice_log_cog.logs)
    bot.run(token)


if __name__ == '__main__':
    main()

