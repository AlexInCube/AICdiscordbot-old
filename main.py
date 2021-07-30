import random

import discord
import mysql.connector
from discord.ext import commands
from discord.ext.commands import bot
from getpass import getpass
from mysql.connector import errorcode
from config import settings

bot = commands.Bot(command_prefix=settings["prefix"])

admin_id = 290168459944263680

def load_cog_commands(filename):
    bot.load_extension(filename)
    cog = bot.get_cog(filename)
    commands = cog.get_commands()
    print("Загружено комманд: " + filename + " " + str([c.name for c in commands]))

load_cog_commands("audio_commands")
# region Подключаемся к базе данных MySQL

DB_NAME = "userdata"
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
    try:
        cur.execute("USE {}".format(DB_NAME))
        print("Используем базу {}".format(DB_NAME))
    except mysql.connector.Error:
        create_database(cur)
        print("База данных {} успешно создана.".format(DB_NAME))
        cnx.database = DB_NAME


# Пытаемся подключиться к MySQL серверу
try:
    cnx = mysql.connector.Connect(**config)
    cur = cnx.cursor()

    show_db_query = "SHOW DATABASES"
    print("Список баз данных: ")
    cur.execute(show_db_query)
    dblist = cur.fetchall()
    print(dblist)
    # Пытаемся использовать базу которую указали в DB_NAME
    use_database(cur)
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Что-то не так с логином или паролем")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Не найдена база данных {} ".format(DB_NAME))
    else:
        print("Не удалось подключиться к базе даннных: ")
        print(err)

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
