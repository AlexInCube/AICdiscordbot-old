import asyncio
import random
import time

import discord
from discord.ext import commands

from main import bot, creator_id
from user_data_commands import change_balance, get_balance, create_balance, change_user_value_in_table, \
    get_user_value_in_table


class other_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Далее идёт список команд
    @commands.command()
    async def help_aic(self, ctx):
        await ctx.send("У всех команд бота, префикс // \n"
                       "Сами команды: \n"
                       "extract_audio [ссылка на видео с youtube] - Извлекает аудиодорожку из видео на ютубе и скидывает её в текстовый канал. \n"
                       "play [ссылка на видео с youtube/прикреплённый файл/любой текст (поиск)] - Мне нужно писать что эта команда делает?\n"
                       "pause - Приостанавливает, но не сбрасывает проигрывание аудиодорожки. \n"
                       "resume - Возобновляет проигрывание аудиодорожки, если оно было остановлено командой pause. \n"
                       "stop - Сбрасывает проигрывание аудиодорожки. \n"
                       "ping - показывает задержку между вами и ботом \n"
                       "roll - [*минимальное/максимальное значение, *максимальное значение] - Если просто написать roll, будет случайно выбрано число от 0 до 100.\n"
                       "flip - Подкинуть монетку.\n"
                       "slot - Сыграть в слот машину.\n"
                       "balance - Посмотреть свои очки.\n"
                       "stats - Посмотреть всю статистику о себе"
                       "timer - [секунд] - Запустить таймер, стандартное значение: 10 секунд.\n")

    # Команда roll аналогичная той что в Доте 2
    @commands.command()
    async def roll(self, ctx, *args):
        try:
            if len(args) == 0:
                await ctx.send(random.randint(0, 100))
            elif len(args) == 1:
                await ctx.send(random.randint(0, int(args[0])))
            elif len(args) == 2:
                await ctx.send(random.randint(int(args[0]), int(args[1])))
        except ValueError:
            await ctx.send("Это должно быть числом!")

    @commands.command()
    async def alcotest(self, ctx):
        beer_perc = random.randint(0, 100)
        await ctx.send(f":beer: Ваша кровь состоит на {beer_perc}% из пива :beer: ")

    @commands.command()
    async def flip(self, ctx):
        await ctx.send(random.choice(["Орёл", "Решка"]))

    @commands.command()
    async def join(self, ctx, channel_name):
        if ctx.message.author.id == creator_id:
            voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
            if voice and voice.is_connected():
                await ctx.send("Я уже зашёл на канал")
            else:
                channel = discord.utils.get(ctx.guild.channels, name=channel_name)
                await channel.connect()

    @commands.command()
    async def leave(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice:
            if voice.is_connected():
                await voice.disconnect()
        else:
            await ctx.send("Я не нахожусь ни на одном канале")

    @commands.command()
    async def ping(self, ctx):
        """ Pong! """
        before = time.monotonic()
        message = await ctx.send("🏓 Понг")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"Задержка к Discord API: {int(round(bot.latency * 1000, 1))}\n Задержка редактирования сообщения: {int(ping)}")

    @commands.command()
    async def timer(self, ctx, *args):
        second_int = 10
        if len(args) == 1:
            try:
                second_int = int(args[0])
            except:
                await ctx.send("Целые числа пиши, а то я не понимаю.")
                return 0

        try:
            if second_int > 300:
                await ctx.send("Я не могу думать больше 300 секунд.")
                raise BaseException
            if second_int <= 0:
                await ctx.send("Я не могу считать негативные числа, будь на позитиве.")
                raise BaseException
            message = await ctx.send("Осталось" + str(second_int) + " секунд")
            while True:
                second_int -= 1
                if second_int == 0:
                    await message.edit(content="Таймер окончен!")
                    break
                await message.edit(content=f"Осталось {second_int} секунд")
                await asyncio.sleep(1)
            await message.edit(content=f"{ctx.author.mention}, ваш таймер закончился!")
        except ValueError:
            await ctx.send("Это должно быть числом!")

    @commands.command()
    async def slot(self, ctx):
        """ Слот-машина """
        emojis = "🍎🍊🍐🍋🍉🍇🍓🍒"
        a = random.choice(emojis)
        b = random.choice(emojis)
        c = random.choice(emojis)
        jackpot = 5
        win = 1
        user_id = ctx.message.author.id
        user_name = "<@" + f"{str(user_id)}" + ">"
        slotmachine = f"**[ {a} {b} {c} ]\n{user_name}**,"

        create_balance(user_id)
        change_user_value_in_table(user_id, "user", "SlotsTotal",
                                   get_user_value_in_table(user_id, "user", "SlotsTotal")+1)

        if (a == b == c): # Если выпало 3 одинаковых фрукта
            change_balance(user_id, get_balance(user_id) + jackpot)
            change_user_value_in_table(user_id, "user", "SlotsWins",
                                       get_user_value_in_table(user_id, "user", "SlotsWins") + 1)
            await ctx.send(
                f"{slotmachine}"
                + " ВАМ АХУЕТЬ КАК ПОВЕЗЛО! Вы получили 5 очков, проверьте баланс //balance 🎉")
        elif (a == b) or (a == c) or (b == c): # Если есть 2 повторяющихся фрукта
            change_balance(user_id, get_balance(user_id) + win)
            change_user_value_in_table(user_id, "user", "SlotsWins",
                                       get_user_value_in_table(user_id, "user", "SlotsWins") + 1)
            await ctx.send(
                f"{slotmachine}"
                + " 2 совпадения в ряду, вы победили! Вы получили 1 очко, проверьте баланс //balance 🎉")
        else:
            await ctx.send(f"{slotmachine} нет совпадений, вы проиграли 😢")




def setup(bot):
    bot.add_cog(other_commands(bot))
