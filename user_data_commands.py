from discord.ext import commands

from main import cur, cnx


def create_balance(ctx):
    try:
        add_user = ("INSERT INTO user "
                    "(UserID, score) "
                    "VALUES (%s,%s)")

        data_user = (ctx.message.author.id, 0)

        cur.execute(add_user, data_user)
        cnx.commit()
    except:
        return 0

def get_balance(ctx):
    query = ("SELECT UserID, Score FROM user "
             "WHERE UserID = %s")

    user_id = ctx.message.author.id
    cur.execute(query, (user_id,))
    for (UserID, score) in cur:
        return score

def change_balance(ctx, new_money):
    money = get_balance(ctx)
    query = ("UPDATE User Set Score = %s WHERE UserID = %s")
    user_id = ctx.message.author.id
    cur.execute(query, (new_money,user_id))


class user_data_commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def balance(self, ctx):
        create_balance(ctx)
        await ctx.send("Ваш баланс: "+str(get_balance(ctx)))


def setup(bot):
    bot.add_cog(user_data_commands(bot))
