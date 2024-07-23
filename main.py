import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.messages = True  # Enable the messages intent (privileged)
intents.voice_states = True

bot = commands.Bot(command_prefix='/', intents=intents)
bot.remove_command("help")  # Remove the default help command

initial_extensions = ['cogs.helpCog', 'cogs.musicCog']

if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
            print(f'Loaded extension: {extension}')
        except Exception as e:
            print(f'Failed to load extension {extension}: {e}')

    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user}')

    bot.run(os.getenv('DISCORD_TOKEN'))
