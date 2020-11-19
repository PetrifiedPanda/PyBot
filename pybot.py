import discord
import time
import os
import re

from discord.ext import commands
from discord.ext.commands import context

bot = commands.Bot(command_prefix='-')

folder_name = 'temp'

if not os.path.exists(folder_name):
    os.makedirs(folder_name)

py_file_path = folder_name + '/bot_temp.py'
py_log_path = folder_name + '/bot_temp_log.py'
log_file_path = folder_name + '/log.txt'


@bot.event
async def on_ready():
    print("Ready")


@bot.command()
async def info(ctx: context):
    await ctx.send('I am a bot that can run python commands you send to me and act somewhat like a python console\n' +
                   'I do not handle any errors or wrong syntax well though')


@bot.command(aliases=['printLog'])
async def get_command_log(ctx: context):
    contents = get_file_contents(py_log_path)
    text = ''
    for line in contents:
        text += line
    if text != '':
        await ctx.send(text)
    else:
        await ctx.send('The log is empty')


@bot.command()
async def python(ctx: context, *, text):
    print("Python command invoked")

    print('Appending to file')
    append_to_file(py_file_path, text + '\n')
    append_to_file(py_log_path, text + '\n')

    print('Running file')
    """
    This does not spot errors in the given code!!!
    """
    os.system('python ' + py_file_path + ' >> ' + log_file_path)
    print('Sending Logfile contents')

    res_lines = get_file_contents(log_file_path)

    res_message = ''
    for line in res_lines:
        res_message += line

    print('Clearing logfile')
    overwrite_file(log_file_path, '')

    remove_destructive_commands()

    if res_message != '' and len(res_message) <= 2000:
        await ctx.send(res_message)
    elif len(res_message) > 2000:
        messages = []
        index = 0
        while index + 2000 < len(res_message):
            next_index = index + 2000
            messages.append(res_message[index: next_index])
            index = next_index
        messages.append(res_message[index:])
        for message in messages:
            await ctx.send(message)
    else:
        await ctx.send('Your code had no output, but was executed successfully (I hope)')


@bot.command()
async def clear(ctx: context):
    overwrite_file(py_file_path, '')
    await ctx.send('python \"console\" has been cleared')


# this also removes prints in function definitions
def remove_destructive_commands():
    contents = get_file_contents(py_file_path)

    pattern = re.compile(r'(print\(.*\))|(exit\(.*\))')
    new_contents = []
    for line in contents:
        new_contents.append(re.sub(pattern, 'pass', line))

    write_lines_to_file(py_file_path, new_contents)


def append_to_file(file_path: str, text: str):
    file = open(file_path, 'a')
    file.write(text)
    file.close()


def overwrite_file(file_path: str, text: str):
    file = open(file_path, 'w')
    file.write(text)
    file.close()


def write_lines_to_file(file_path: str, lines: list):
    file = open(file_path, 'w')
    for line in lines:
        file.write(line)
    file.close()


def get_file_contents(file_path: str) -> str:
    file = open(file_path, 'r')
    result = file.readlines()
    file.close()
    return result


# always clear python file before running bot
overwrite_file(py_file_path, '')

token = get_file_contents('token.txt')[0].strip()

bot.run(token)
