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
    cur = main.cur


    query = ("SELECT UserID, Score FROM user "
             "WHERE UserID = %s")

    cur.execute(query, (user_id,))
    for (UserID, score) in cur:
        return score


def change_balance(ctx, new_money):
    cur = main.cur
    cnx = main.cnx

    main.check_connection_to_mysql()

    user_id = ctx.message.author.id
    query = ("UPDATE User Set Score = %s WHERE UserID = %s")
    cur.execute(query, (new_money, user_id))
    cnx.commit()


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


def setup(bot):
    bot.add_cog(user_data_commands(bot))
