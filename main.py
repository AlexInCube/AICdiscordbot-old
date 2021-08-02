import random
from getpass import getpass

import discord
import mysql.connector
from discord.ext import commands
from discord.ext.commands import bot
from mysql.connector import errorcode

from config import settings

bot = commands.Bot(command_prefix=settings["prefix"])

admin_id = 290168459944263680

cnx = None
cur = None


def load_cog_commands(filename):
    bot.load_extension(filename)
    cog = bot.get_cog(filename)
    commands = cog.get_commands()
    print("Загружено комманд: " + filename + " " + str([c.name for c in commands]))


load_cog_commands("audio_commands")
# region Подключаемся к базе данных MySQL


DB_NAME = "userdata"

try:
    config = {
        "host": "localhost",
        "user": settings["login"],
        "password": settings["password"]
    }
except:
    print("Ошибка при чтении из config.py, введите логин и пароль вручную")
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
        print("Не удалось создать базу данных: {}".format(err))
        exit(1)


def use_database(cur):
    global cnx
    try:
        cur.execute("USE {}".format(DB_NAME))
        print("Используем базу {}".format(DB_NAME))
    except mysql.connector.Error:
        create_database(cur)
        print("База данных {} успешно создана.".format(DB_NAME))
        cnx.database = DB_NAME


# Пытаемся подключиться к MySQL серверу
def connect_to_mysql():
    global cnx
    global cur
    try:
        cnx = mysql.connector.Connect(**config)
        cur = cnx.cursor()
        print("Подключение к MySQL произошло успешно")
        # Пытаемся использовать базу которую указали в DB_NAME
        use_database(cur)
        return True
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Что-то не так с логином или паролем")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Не найдена база данных {} ".format(DB_NAME))
        else:
            print("Не удалось подключиться к базе даннных")
            # print(err)
        return False


connect_to_mysql()


def check_connection_to_mysql():
    global cnx
    if cnx is None:
        trying = connect_to_mysql()
        if trying:
            pass
        else:
            return False

    if cnx.is_connected():
        return True
    else:
        print("Подключение к MySQL отсутствует, пытаемся подключиться")
        try:
            cnx.reconnect(2, 0)
        except:
            print("Не удалось подключиться")
            return False

        if cnx.is_connected():
            use_database(cur)
            print("Подключение к MySQL произошло успешно")
            return True



if check_connection_to_mysql():
    # Создаём таблицы в базе
    TABLES = {'user': (
        "CREATE TABLE `user`("
        "UserID BIGINT UNSIGNED NOT NULL UNIQUE,"
        "Score int DEFAULT 0"
        ") ENGINE=InnoDB"
    )}

    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print("Создаём таблицу {}: ".format(table_name), end='')
            cur.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("Уже существует.")
            else:
                print(err.msg)
        else:
            print("OK")
# endregion


load_cog_commands("other_commands")
load_cog_commands("user_data_commands")


# region События бота
@bot.event
async def on_ready():
    # Если бот запустился
    print("Бот готов принимать комманды")
    await bot.change_presence(activity=discord.Game("//help_aic"))


@bot.event
async def on_disconnect():
    global cnx
    global cur
    cur.close()
    cnx.close()


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
    try:
        await bot.process_commands(message)
    except:
        return 0


# endregion
bot.run(settings['token'])
