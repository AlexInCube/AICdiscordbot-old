import time

import discord

import random


import youtube_dl
from discord.ext import commands
from discord.ext.commands import bot


from config import settings

bot = commands.Bot(command_prefix=settings["prefix"])


bot.load_extension("audio_commands")


cog = bot.get_cog("audio_commands")
commands = cog.get_commands()
print("Loaded audio commands: "+str([c.name for c in commands]))
# Команда roll аналогичная той что в Доте 2
@bot.command()
async def roll(ctx, *args):
    if len(args) == 0:
        await ctx.send(random.randint(0, 100))
    elif len(args) == 1:
        await ctx.send(random.randint(0, int(args[0])))
    elif len(args) == 2:
        await ctx.send(random.randint(int(args[0]), int(args[1])))

@bot.command()
async def flip(ctx):
    await ctx.send(random.choice(["Орёл","Решка"]))

@bot.command()
async def join(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await ctx.send("Я уже зашёл на канал")
    else:
        channel = ctx.author.voice.channel
        await channel.connect()


@bot.command()
async def leave(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice:
        if voice.is_connected():
            await voice.disconnect()
    else:
        await ctx.send("Я не нахожусь ни на одном канале")

@bot.command()
async def ping(ctx):
    """ Pong! """
    before = time.monotonic()
    before_ws = int(round(bot.latency * 1000, 1))
    message = await ctx.send("🏓 Понг")
    ping = (time.monotonic() - before) * 1000
    await message.edit(content=f"🏓 Пинг: {int(ping)}")

@bot.command()
async def help_aic(ctx):
    await ctx.send("У всех команд бота, префикс // \n"
                   "Сами команды: \n"
                   "extract_audio [ссылка на видео с youtube] - Извлекает аудиодорожку из видео на ютубе и скидывает её в текстовый канал. \n"
                   "play [ссылка на видео с youtube] - Играет аудиодорожку из видео, в том голосовом канале где был человек который призвал бота этой командой. \n"
                   "play_file [прикреплённый файл] - Играет аудиодорожку из прикреплённого файла.\n"
                   "pause - Приостанавливает, но не сбрасывает проигрывание аудиодорожки. \n"
                   "resume - Возобновляет проигрывание аудиодорожки, если оно было остановлено командой pause. \n"
                   "stop - Сбрасывает проигрывание аудиодорожки. \n"
                   "ping - показывает задержку между вами и ботом \n"
                   "join - призывает бота на канал где находится человек писавший эту команду \n"
                   "leave - выкидывает бота с канала \n"
                   "roll - [*минимальное/максимальное значение, *максимальное значение] - Если просто написать roll, будет случайно выбрано число от 0 до 100.\n"
                   "flip - Подкинуть монетку.\n"
                   "slot - Сыграть в слот машину.\n")

@bot.command()
async def slot(ctx):
    """ Roll the slot machine """
    emojis = "🍎🍊🍐🍋🍉🍇🍓🍒"
    a = random.choice(emojis)
    b = random.choice(emojis)
    c = random.choice(emojis)

    slotmachine = f"**[ {a} {b} {c} ]\n{ctx.author.name}**,"

    if (a == b == c):
        await ctx.send(f"{slotmachine} Всё совпадает, вы победили! 🎉")
    elif (a == b) or (a == c) or (b == c):
        await ctx.send(f"{slotmachine} 2 совпадения в ряду, вы победили! 🎉")
    else:
        await ctx.send(f"{slotmachine} Нет совпадений, вы проиграли 😢")

@bot.event
async def on_ready():
    # Если бот запустился
    print("Bot online")
    await bot.change_presence(activity=discord.Game("//help_aic"))


@bot.event
async def on_message(message):
    # Говорим что-то в чат если писал AlexInCube
    # if message.author.id == 290168459944263680:
    #    await message.channel.send('Привет моему разрабу')

    # Булим Keynadi
    if message.author.id == 194369371169095680:
        if random.random() > 0.99:
            bulling_array = ["Как там поживает EximiaWorld?"]
            await message.channel.send(random.choice(bulling_array))

    # Эта строчка обязательно, иначе никакие команды не будут работать
    await bot.process_commands(message)


bot.run(settings['token'])
