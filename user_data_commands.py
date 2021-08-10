import discord
from discord.ext import commands

import main


def create_balance(user_id):
    cur = main.cur
    cnx = main.cnx

    try:
        add_user = ("INSERT INTO user "
                    "(UserID, score) "
                    "VALUES (%s,%s)")

        data_user = (user_id, 0)

        cur.execute(add_user, data_user)
        cnx.commit()
    except:
        return 0


def get_balance(user_id):
    return get_user_value_in_table(user_id,"user","Score")

def get_user_value_in_table(user_id, table: str, key: str):
    cur = main.cur

    query = (f"SELECT UserID, {key} FROM {table} "
             f"WHERE UserID = {user_id}")

    cur.execute(query)
    for (UserID, key) in cur:
        return key


def change_user_value_in_table(user_id, table: str, key: str, value):
    cur = main.cur
    cnx = main.cnx

    main.check_connection_to_mysql()

    query = (f"UPDATE {table} Set {key} = {value} WHERE UserID = {user_id}")
    cur.execute(query)
    cnx.commit()


def change_balance(user_id, new_money):
    change_user_value_in_table(user_id, "user", "Score", new_money)


class user_data_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def balance(self, ctx):
        if main.check_connection_to_mysql():
            user_id = ctx.message.author.id
            create_balance(user_id)
            await ctx.send("<@" + str(user_id) + ">" + ", ваш баланс: " + str(get_balance(user_id)))
        else:
            await ctx.send("Возникла проблема с подключением к серверу")

    @commands.command()
    async def stats(self, ctx):
        if main.check_connection_to_mysql():
            user_id = ctx.message.author.id
            embedVar = discord.Embed(title=f"{ctx.message.author.display_name}", description="Статистика", color=0x00ff00)
            embedVar.set_thumbnail(url=ctx.author.avatar_url)
            embedVar.add_field(name="Очки", value=get_balance(user_id), inline=False)
            totalGames = get_user_value_in_table(user_id, "user", "SlotsTotal")
            embedVar.add_field(name="Сыграно слот-машин", value=totalGames, inline=False)
            winsGame = get_user_value_in_table(user_id, "user", "SlotsWins")
            embedVar.add_field(name="Побед в слот-машинах", value=winsGame, inline=False)
            embedVar.add_field(name="Соотношение побед/поражений", value=str(round((winsGame / totalGames) * 100)) + "%",inline=False)
            await ctx.send(embed=embedVar)
        else:
            await ctx.send("Возникла проблема с подключением к серверу")

def setup(bot):
    bot.add_cog(user_data_commands(bot))
