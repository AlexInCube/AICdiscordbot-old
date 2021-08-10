from getpass import getpass
import utility
import discord
import mysql.connector
from discord.ext import commands
from discord.ext.commands import bot
from mysql.connector import errorcode

from config import settings

bot = commands.Bot(command_prefix=settings["prefix"], help_command=None)

creator_id = 290168459944263680  # Можете сюда вставить свой айди

# Используем эти переменные как глобальные, если их надо обновить то вызываем так: main.cnx
cnx = None
cur = None

utility.load_cog_commands(bot, "audio_commands")
# region Подключаемся к базе данных MySQL


DB_NAME = "userdata"

try:
    config = {
        "host": "localhost",
        "user": settings["login"],
        "password": settings["password"]
    }
except:
    print(utility.get_format_date_and_time() + "Ошибка при чтении из config.py, введите логин и пароль вручную")
    config = {
        "host": "localhost",
        "user": input("Имя пользователя: "),
        "password": getpass("Пароль: "),
    }


def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print(utility.get_format_date_and_time() + "Не удалось создать базу данных: {}".format(err))
        exit(1)


def use_database(cur):
    global cnx
    try:
        cur.execute("USE {}".format(DB_NAME))
        print(utility.get_format_date_and_time() + "Используем базу {}".format(DB_NAME))
    except mysql.connector.Error:
        create_database(cur)
        print(utility.get_format_date_and_time() + "База данных {} успешно создана.".format(DB_NAME))
        cnx.database = DB_NAME


# Пытаемся подключиться к MySQL серверу
def connect_to_mysql():
    global cnx
    global cur
    try:
        cnx = mysql.connector.Connect(**config)
        cur = cnx.cursor()

        print(utility.get_format_date_and_time() + "Подключение к MySQL произошло успешно")
        # Пытаемся использовать базу которую указали в DB_NAME
        use_database(cur)
        return True
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print(utility.get_format_date_and_time() + "Что-то не так с логином или паролем")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print(utility.get_format_date_and_time() + "Не найдена база данных {} ".format(DB_NAME))
        else:
            print(utility.get_format_date_and_time() + "Не удалось подключиться к базе даннных")
            # print(err)
        return False


connect_to_mysql()


def check_connection_to_mysql():
    global cnx
    global cur
    if cnx is None:
        trying = connect_to_mysql()
        if trying:
            pass
        else:
            return False

    if cnx.is_connected():
        return True
    else:
        print(utility.get_format_date_and_time() + "Подключение к MySQL отсутствует, пытаемся подключиться")
        try:
            cnx.reconnect(2, 0)
            cur = cnx.cursor()
        except:
            print(utility.get_format_date_and_time() + "Не удалось подключиться")
            return False

        if cnx.is_connected():
            use_database(cur)
            print(utility.get_format_date_and_time() + "Подключение к MySQL произошло успешно")
            return True


if check_connection_to_mysql():
    # Создаём таблицы в базе
    TABLES = {}
    TABLES['user'] = (
        "CREATE TABLE `user`("
        "UserID BIGINT UNSIGNED NOT NULL UNIQUE,"
        "Score int DEFAULT 0,"
        "SlotsTotal int DEFAULT 0,"
        "SlotsWins int DEFAULT 0"
        ") ENGINE=InnoDB")

    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print(utility.get_format_date_and_time() + f"Создаём таблицу {table_name}: ", end='')
            cur.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("Уже существует.")
            else:
                print(err.msg)
        else:
            print(utility.get_format_date_and_time() + "OK")
# endregion

utility.load_cog_commands(bot, "user_data_commands")
utility.load_cog_commands(bot, "other_commands")


# region События бота
@bot.event
async def on_ready():
    # Если бот запустился
    print(utility.get_format_date_and_time() + "Бот готов принимать комманды")
    await bot.change_presence(activity=discord.Game("//help_aic"))


@bot.event
async def on_disconnect():
    global cnx
    global cur
    if isinstance(cnx, None):
        return 0

    if cnx.is_connected():
        cur.close()
        cnx.close()


@bot.event
async def on_message(message):
    # Эта строчка обязательна, иначе никакие команды не будут работать
    try:
        await bot.process_commands(message)
    except:  # Если человек неправильно написал команду, то забьём на это и не будем засирать терминал бота.
        return 0


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(
            embed=discord.Embed(description=f'{ctx.author.name}, команда не найдена!', colour=discord.Color.red()))


# endregion
bot.run(settings['token'])
