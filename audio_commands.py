import asyncio
import os
from asyncio import sleep

import discord
import requests
import youtube_dl
from discord.ext import commands
from requests import get
from youtube_dl import YoutubeDL

from main import bot

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

def search(arg):
    with YoutubeDL({'format': 'bestaudio', 'noplaylist':'True'}) as ydl:
        try: requests.get(arg)
        except: info = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]
        else: info = ydl.extract_info(arg, download=False)

    return (info, info['formats'][0]['url'])

class audio_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def extract_audio(self, ctx, url: str):
        with YoutubeDL({'format': 'bestaudio', 'noplaylist': 'True'}) as ydl:
            try:
                requests.get(url)
            except:
                info = ydl.extract_info(f"ytsearch:{url}", download=False)['entries'][0]
            else:
                info = ydl.extract_info(url, download=False)

        audio_name = str(info["title"])
        await ctx.send("Извлекаем звук из: "+audio_name)

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }


        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        for file in os.listdir("./"):
            if file.endswith(".mp3"):
                os.rename(file, audio_name+".mp3")

        file_size = os.path.getsize(audio_name+".mp3")
        if file_size >= 8000000:
            await ctx.send("Файл весит больше 8МБ, из-за этого его нельзя отправить")
        else:
            await ctx.send(file=discord.File(r""+audio_name+".mp3"))

        song_there = os.path.isfile(audio_name+".mp3")
        try:
            if song_there:
                os.remove(audio_name+".mp3")
        except PermissionError:
            return


    @commands.command()
    async def play(self, ctx, *, query):
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice:
            if voice.is_connected():
                voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        else:
            channel = ctx.author.voice
            if channel:
                await channel.channel.connect()
                voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
            else:
                await ctx.send(ctx.author.mention+" зайди сначала в голосовой канал")
                return

        FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        video, source = search(query)

        voice.play(discord.FFmpegPCMAudio(source, **FFMPEG_OPTS), after=lambda e: print('done', e))
        voice.is_playing()

    @commands.command()
    async def play_file(self, ctx):
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice:
            if voice.is_connected():
                voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        else:
            channel = ctx.author.voice
            if channel:
                await channel.channel.connect()
                voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
            else:
                await ctx.send(ctx.author.mention + " зайди сначала в голосовой канал")
                return

        for attach in ctx.message.attachments:
            await attach.save(f"{attach.filename}")

        voice.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source=r""+attach.filename))

        while voice.is_playing():
            sleep(.1)

        song_there = os.path.isfile(r"" + attach.filename)
        try:
            if song_there:
                os.remove(r"" + attach.filename)
        except PermissionError:
            return



    @commands.command()
    async def pause(self, ctx):
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            voice.pause()
        else:
            await ctx.send("Сейчас ничего не играет")


    @commands.command()
    async def resume(self, ctx):
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice.is_paused():
            voice.resume()
        else:
            await ctx.send("Аудио не на паузе")


    @commands.command()
    async def stop(self, ctx):
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        voice.stop()

def setup(bot):
    bot.add_cog(audio_commands(bot))