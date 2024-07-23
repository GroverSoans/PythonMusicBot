import discord
from discord.ext import commands

import yt_dlp


FFMPEG_OPTIONS = {'options': '-vn'}
YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': True}

class musicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.is_playing = False
        self.is_paused = False

        self.musicQueue = []

        self.vc = None

    def searchYT(self, item):
        with yt_dlp.YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception:
                return False

        return {'source': info[['url']], 'title': info['title']}
            
    async def play_next(self, ctx):
        if self.queue:
            url, title = self.queue.pop(0)
            source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
            ctx.voice_client.play(source, after=lambda e: self.client.loop.create_task(self.play_next(ctx)))
            await ctx.send(f'Now playing: **{title}**')
        elif not ctx.voice_client.is_playing():
            await ctx.send("Queue is empty.")


    async def playMusic(self, ctx):
        if len(self.musicQueue) > 0:
            self.is_playing = True
            m_url = self.musicQueue[0][0]['source']

            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.musicQueue[0][1].connect()

                if self.vc == None:
                    await ctx.send("Could not connect to the voice channel")
                    return
                
                else:
                    await self.vc.move_to(self.musicQueue[0][1])

                self.musicQueue.pop(0)

                self.vc.play(discord.FFmpegOpusAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.playNext())


            else:
                self.is_playing = False

    @commands.command(name="play", aliases=["p", "playing"], help="Play the selcted song from Youtube")
    async def play(self, ctx, *args):
        print('function is called')
        query = " ".join(args)

        voiceChannel = ctx.author.voice.channel
        if voiceChannel is None:
            await ctx.send("Connect to the voice channel")
        elif self.is_paused:
            self.vc.resume()
        else:
            song = self.searchYT(query)
            if type(song) == type(True):
                await ctx.send("Could not play the song. Incorrect format, Please try again.")
            else:
                await ctx.send("Song added to the queue")
                self.musicQueue.append([song, voiceChannel])

                if self.is_playing == False:
                    await self.playMusic(ctx)

    @commands.command(name="pause", help="Pauses the current song being played")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()

    @commands.command(name="resume", aliases = ["r"], help="Resumes playing the current song")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()

    @commands.command(name="skip", aliases=["s"], help = "Skips the currently played song")
    async def skip(self, ctx, *args):
        if self.vc != None and self.vc:
            self.vc.stop()
            await self.playMusic(ctx)

    @commands.command(name="queue", aliases=["q"], help="Displays all the songs that are currently in the queue")
    async def queue(self, ctx):
        retval = ""

        for i in range(0, len(self.musicQueue)):
            if i > 4: break
            retval += self.musicQueue[i][0]['title'] + '\n'

        if retval != "":
            await ctx.send(retval)
        else:
            await ctx.send("There is currently no music in the queue.")

    @commands.command(name="clear", aliases=["c"], help="Clears the queue and stops the current song")
    async def clear(self, ctx, *args):
        if self.vc != None and self.is_playing:
            self.vc.stop()
        self.musicQueue = []
        await ctx.send("Music queue cleared")

    @commands.command(name="leave", aliases=["l", "disconnect", "d"], help="Kick the bot from the voice channel")
    async def leave(self, ctx):
        self.is_paused = False
        self.is_playing = False
        await self.vc.disconnect()
        


        




