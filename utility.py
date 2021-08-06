# Загрузка команд из других .py файлов
from datetime import datetime


def load_cog_commands(bot, filename):
    bot.load_extension(filename)
    cog = bot.get_cog(filename)
    commands = cog.get_commands()
    print(get_format_date_and_time() + "Загружено комманд: " + filename + " " + str([c.name for c in commands]))


def get_format_date_and_time():
    now = datetime.now()
    dt_string = "[" + now.strftime("%d/%m/%Y %H:%M:%S") + "] "
    return dt_string
