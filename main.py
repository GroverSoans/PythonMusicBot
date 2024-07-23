import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import yt_dlp
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

FFMPEG_OPTIONS = {'options': '-vn'}
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': True}

# Load the token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class MusicBot(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client 
        self.queue = []

    @commands.command(name="play", aliases=["p", "playing"], help="Play the selected song from Youtube")
    async def play(self, ctx, *, search):
        voice_channel = ctx.author.voice.channel if ctx.author.voice else None
        if not voice_channel:
            return await ctx.send("You need to be in a voice channel to play music.")
        if not ctx.voice_client:
            await voice_channel.connect()

        async with ctx.typing():
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(f"ytsearch:{search}", download=False)
                if 'entries' in info:
                    info = info['entries'][0]
                url = info['url']
                title = info['title']
                self.queue.append((url, title))
                await ctx.send(f'Added to queue: **{title}**')

            if not ctx.voice_client.is_playing():
                await self.play_next(ctx)

    async def play_next(self, ctx):
        if self.queue:
            url, title = self.queue.pop(0)
            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            ctx.voice_client.play(source, after=lambda e: self.client.loop.create_task(self.play_next(ctx)))
            await ctx.send(f'Now playing: **{title}**')
        elif not ctx.voice_client.is_playing():
            await ctx.send("Queue is empty.")
    
    @commands.command(name="skip", aliases=["s"], help="Skips the currently played song")
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Skipped the current song.")


    @commands.command(name="pause", help="Pauses the currently played song")
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("Paused the current song.")
    
    @commands.command(name="resume", help="Resumes the currently paused song")
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("Resumed the current song.")

    @commands.command(name="queue", aliases=["q"], help="Shows the current music queue")
    async def show_queue(self, ctx):
        if not self.queue:
            return await ctx.send("The queue is empty.")

        queue_list = "\n".join([f"{index}. {title}" for index, (_, title) in enumerate(self.queue)])
        embed = discord.Embed(title="Music Queue", description=queue_list, color=discord.Color.blue())
        await ctx.send(embed=embed)

    @commands.command(name="leave", aliases=["disconnect"], help="Leaves the voice channel and stops playing music")
    async def leave_channel(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            self.queue.clear()
            await ctx.send("Left the voice channel and cleared the queue.")
        else:
            await ctx.send("Not connected to a voice channel.")

    @commands.command(name="clear", aliases=["c"], help="Clears the music queue")
    async def clear_queue(self, ctx):
        self.queue.clear()
        await ctx.send("Queue cleared.")

    @commands.command(name="helpmusic", aliases=["musichelp"], help="Displays help for music commands")
    async def help_music(self, ctx):
        help_embed = discord.Embed(
            title="Music Bot Help",
            description="Here are the available commands for the Music Bot:",
            color=discord.Color.blue()
        )
        help_embed.add_field(
            name="/play, /p [search]",
            value="Plays the selected song from Youtube.",
            inline=False
        )
        help_embed.add_field(
            name="/skip, /s",
            value="Skips the currently played song.",
            inline=False
        )
        help_embed.add_field(
            name="/pause",
            value="Pauses the currently played song.",
            inline=False
        )
        help_embed.add_field(
            name="/resume",
            value="Resumes the currently paused song.",
            inline=False
        )
        help_embed.add_field(
            name="/queue, /q",
            value="Shows the current music queue.",
            inline=False
        )
        help_embed.add_field(
            name="/clear, /c",
            value="Clears the music queue.",
            inline=False
        )
        help_embed.add_field(
            name="/leave, /disconnect",
            value="Leaves the voice channel and stops playing music.",
            inline=False
        )

        await ctx.send(embed=help_embed)

client = commands.Bot(command_prefix="/", intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} is now running!')


async def main():
    await client.add_cog(MusicBot(client))
    await client.start(TOKEN)

asyncio.run(main())

