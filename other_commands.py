import random
import time

import discord
from discord.ext import commands

from main import bot
from user_data_commands import change_balance, get_balance


class other_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Далее идёт список команд
    # Команда roll аналогичная той что в Доте 2
    @commands.command()
    async def roll(self, ctx, *args):
        if len(args) == 0:
            await ctx.send(random.randint(0, 100))
        elif len(args) == 1:
            await ctx.send(random.randint(0, int(args[0])))
        elif len(args) == 2:
            await ctx.send(random.randint(int(args[0]), int(args[1])))

    @commands.command()
    async def flip(self, ctx):
        await ctx.send(random.choice(["Орёл", "Решка"]))

    @commands.command()
    async def join(self, ctx):
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await ctx.send("Я уже зашёл на канал")
        else:
            channel = ctx.author.voice.channel
            await channel.connect()

    @commands.command()
    async def leave(self, ctx):
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice:
            if voice.is_connected():
                await voice.disconnect()
        else:
            await ctx.send("Я не нахожусь ни на одном канале")

    @commands.command()
    async def ping(self, ctx):
        """ Pong! """
        before = time.monotonic()
        #before_ws = int(round(bot.latency * 1000, 1))
        message = await ctx.send("🏓 Понг")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"🏓 Пинг: {int(ping)}")

    @commands.command()
    async def help_aic(self, ctx):
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

    @commands.command()
    async def slot(self, ctx):
        """ Roll the slot machine """
        emojis = "🍎🍊🍐🍋🍉🍇🍓🍒"
        a = random.choice(emojis)
        b = random.choice(emojis)
        c = random.choice(emojis)

        slotmachine = f"**[ {a} {b} {c} ]\n{ctx.author.name}**,"

        if (a == b == c):
            change_balance(ctx, get_balance(ctx) + 2)
            await ctx.send(f"{slotmachine} Всё совпадает, вы победили! Вы получили 2 очка, проверьте баланс //balance 🎉")
        elif (a == b) or (a == c) or (b == c):
            change_balance(ctx,get_balance(ctx)+1)
            await ctx.send(f"{slotmachine} 2 совпадения в ряду, вы победили! Вы получили 1 очко, проверьте баланс //balance 🎉")
        else:
            await ctx.send(f"{slotmachine} Нет совпадений, вы проиграли 😢")


def setup(bot):
    bot.add_cog(other_commands(bot))
