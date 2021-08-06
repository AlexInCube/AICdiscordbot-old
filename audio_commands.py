import asyncio
import os

import discord
import requests
import youtube_dl
from discord.ext import commands
from youtube_dl import YoutubeDL

from main import bot

# region Настройки для YoutubeDL
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
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

# endregion



async def get_next_music(name, queue):
    while True:
        # Получить "рабочий элемент" вне очереди.
        sleep_for = await queue.get()

        # Спать "sleep_for" секунд.
        await asyncio.sleep(sleep_for)

        # Сообщение очереди, для обработки «рабочего элемента».
        queue.task_done()

        print(f'{name} has slept for {sleep_for:.2f} seconds')

# Поиск видео с Youtube
def search(arg):
    with YoutubeDL({'format': 'bestaudio', 'noplaylist': 'True'}) as ydl:
        try:
            requests.get(arg)
        except:
            info = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]
        else:
            info = ydl.extract_info(arg, download=False)

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
        await ctx.send("Извлекаем звук из: " + audio_name)

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
                os.rename(file, audio_name + ".mp3")

        file_size = os.path.getsize(audio_name + ".mp3")
        if file_size >= 8000000:
            await ctx.send("Файл весит больше 8МБ, из-за этого его нельзя отправить")
        else:
            await ctx.send(file=discord.File(r"" + audio_name + ".mp3"))

        song_there = os.path.isfile(audio_name + ".mp3")
        try:
            if song_there:
                os.remove(audio_name + ".mp3")
        except PermissionError:
            return

    @commands.command()
    async def play(self, ctx, *, query):

        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice:
            if voice.is_connected():
                voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        else:
            channel = ctx.author.voice.channel
            if channel:
                await channel.connect()
                voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
            else:
                await ctx.send(ctx.author.mention + " зайди сначала в голосовой канал")
                return

        FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        video, source = search(query)

        voice.play(discord.FFmpegPCMAudio(source, **FFMPEG_OPTS), after=lambda e: print('done', e))
        user_name = ctx.message.author.display_name
        await ctx.send(f"{user_name} " + "включил " + video["title"])


    @commands.command()
    async def play_file(self, ctx):
        if ctx.message.attachments == []:
            await ctx.send("Отсутствует файл")
            return 0

        attach = ctx.message.attachments[0]

        if attach.url.endswith('mp3') or attach.url.endswith('wav') or attach.url.endswith('ogg'):
            pass
        else:
            await ctx.send("Файл "f"{attach.filename}" + " не является аудиофайлом")
            return 0

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

        await attach.save(f"{attach.filename}")

        if voice.is_playing():
            voice.stop()

        voice.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source=r"" + attach.filename))

        user_name = ctx.message.author.display_name
        await ctx.send(f"{user_name} " + "включил " + f"{attach.filename}")

        while voice.is_playing():
            await asyncio.sleep(0.1)

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
            await ctx.send(ctx.message.author.display_name + " поставил меня на паузу")
        else:
            await ctx.send("Сейчас ничего не играет")

    @commands.command()
    async def resume(self, ctx):
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice.is_paused():
            voice.resume()
            await ctx.send(ctx.message.author.display_name + " снял меня с паузы")
        else:
            await ctx.send("Аудио не на паузе")

    @commands.command()
    async def stop(self, ctx):
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        voice.stop()


def setup(bot):
    bot.add_cog(audio_commands(bot))
