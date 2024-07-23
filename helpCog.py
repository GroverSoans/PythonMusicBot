import discord
from discord.ext import commands

class helpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.helpMessage = """
```
General commands:
/help: displays all the available commands
/p <keyword>: finds the selected song on youtube and plays it in the voice channel
/q: displays all the songs currently in the queue
/skip: skips the current song that is being played
/clear: stops the music and clears the current queue
/leave: Disconects the bot from the voice channel
/pause: pauses the current song that is being played
/resume: resumes playing the current song
```
"""
        self.textChannelText = []

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is ready!")
        await self.send_to_all(await self.get_command_list())
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.textChannelText.append(channel)

        await self.sendToAll(self.helpMessage)

    async def sendToAll(self, msg):
        for text_channel in self.textChannelText:
            await text_channel.send(msg)

    @commands.command(name="help", help="Displays all the availabel commands")
    async def help(self, ctx):
        await ctx.send(self.helpMessage)


        
    