

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
print("Loaded commands: "+str([c.name for c in commands]))
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

@bot.event
async def on_ready():
    # Если бот запустился
    print("Bot online")
    # await client.get_channel(813753159070515242).send("Здарова всем!")


@bot.event
async def on_message(message):
    # Говорим что-то в чат если писал AlexInCube
    # if message.author.id == 290168459944263680:
    #    await message.channel.send('Привет моему разрабу')

    # Булим Keynadi
    if message.author.id == 194369371169095680:
        if random.random() > 0.99:
            bulling_array = ["Как там поживает EximiaWorld?", "Когда разбанишь продавца говна?",
                             "Лучше бы деньги на лечение себе отложил."]
        await message.channel.send(random.choice(bulling_array))

    # Эта строчка обязательно, иначе никакие команды не будут работать
    await bot.process_commands(message)


bot.run(settings['token'])
