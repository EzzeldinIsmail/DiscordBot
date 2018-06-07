import discord
from discord import Embed, Colour, Message
from discord.ext.commands import Bot
import time
from re import search, I
from disclib import Character
from itertools import cycle
import datetime
from random import randint
import asyncio
from sys import exc_info
from sqlite3 import connect, Cursor
from typing import Union
from random import choice
from math import ceil

# TODO document discord api
# TODO set_online
# TODO implement types and typing
# TODO crit chance
# TODO gold --> xp converter
# TODO error checking (on_command_error)
# TODO check gold/min
# TODO rebalance pvp
# TODO add more quests (from quests and items)
# TODO add more weapons
# TODO add more craftables
# TODO add more lore (decriptions)
# TODO add seperation comments
# TODO giving money
# TODO tavern DLC
# TODO subclasses (own level) DLC

"""
The discord bot 315zizx meant for personal use and not completely modified for multi server use.
This bot implementes most basic bot stuff excpet music (I like my laptop in one piece thank you),
it also has the text based mmorpg currently under development and improvement. All user data is 
stored in a database using sqlite3.
`` = monospace text
``` = indent monospace text
"""

__version__ = '0.9.5'
userid = ''
msg: discord.Message = ''
client = discord.Client()
bot: asyncio = Bot(command_prefix=',')

def arg(ctx): return ' '.join(ctx.message.content.strip().split(' ')[1:])  # Returns arguments

def check(cursor, db: str, field: str, req: Union[str, int]):
    """Used to check if req exists in the database"""
    if type(req) == str:
        cursor.execute('SELECT * FROM {} WHERE {} = "{}"'.format(db, field, req.replace("'", "\'")))  # Query for strings
    else:
        cursor.execute('SELECT * FROM {} WHERE {} = {}'.format(db, field, req))    # Query for numbers
    return cursor.fetchall() == []

async def tloop(interval, end, txt):
    s = time.time()
    for i in cycle(['.', '..', '...']):
        await bot.edit_message(txt, txt.content+i)
        await asyncio.sleep(interval)
        if time.time() > s+end:
            break

async def record(ctx, message):
    channel, send = cursor.execute('SELECT bot, record FROM servers WHERE ID = ?',(ctx.message.server.id,)).fetchall()[0]
    if send != 'N':
        await bot.send_message(bot.get_channel(channel), message)


@bot.event
async def on_server_join(server):
    with connect('main.db') as db:
        cursor = db.cursor()
        cursor.execute('INSERT INTO servers VALUES (?, ?, ?, ?, ?)', (server.id, 'None', 'None', 'N', 'N'))
        db.commit()

@bot.event
async def on_server_remove(server):
    with connect('main.db') as db:
        cursor = db.cursor()
        cursor.execute('DELETE FROM servers WHERE ID = ?', (server.id,))
        db.commit()


@bot.event
async def on_member_join(member):
    with connect('main.db') as db:
        cursor = db.cursor()
        channel = cursor.execute('SELECT bot FROM servers WHERE ID=?', (member.server.id,)).fetchall()[0][0]
    for i in member.server.roles:
        if i.name == "Wait... You're Online?":
            roles = discord.utils.get(member.server.roles, name="Wait... You're Online?")    # Gets role
            await bot.add_roles(member, roles)       # Adds role to new member (Make sure bot role is above that role)
    await bot.send_message(bot.get_channel(channel), "Welcome to the server <@{}>!".format(member.id)) # Welcomes new member to server


@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name='PyCharm'))    # Sets status to playing PyCharm
    data = cursor.execute('SELECT online, bot FROM servers').fetchall()
    for send, channel in data:
        if send != 'N':
            await bot.send_message(bot.get_channel(channel), "I am online!")


@bot.event                          # Event handler at start of every function
async def on_message(message):              # Async function to handle multiple things at once
    message.content: str            # Gets content of message
    message.author.id: str          # Gets id of sender of message
    global userid
    global msg
    userid = message.author.id
    msg = message
    prefix = ','
    if message.content.startswith(prefix):
        if message.content.lower() == prefix+'help':    # All commands
            await bot.send_message(message.author, """
            Normal commands:
                ``on``: makes the bot go online
                ``off``: makes the bot go offline (takes a while) 
                ``set_prefix {symbol}``: sets that symbol as prefix
                ``set_channel``: sets channel message is typed in as bot's message channel
                ``hello``: replies hi to the message 
                ``say {sentence}``: makes the bot say what follows
                ``bots {sentence} {number}``: makes bot say sentence a number of times and then delete twice that amount of messages
                ``compliment``: makes the bot compliment you
                ``created``: returns when the users account was created                
                ``kill {person}``:  kills person
                ``die``: kills oneself
                ``purge {n}``: delete that many messages
            Game commands:
                ``character``: gets info of character
                ``create {name} {class}``: creates a character (can only have one)
                ``inventory``: gets the characters inventory
                ``quests {n}``: lists all available quest names of that level
                ``quest {name}``: retrieves the information of the supplied quest 
                ``start {name}``: starts the quest supplied
                ``collect``: finishes quest if one is pending
                ``shop``: lists all items in shop
                ``inspect {item}``: gets information for item
                ``buy {item}``: buys item 
                ``leaderboard``: gets server leaderboard
                """)

        else:
            global char
            char = Character(message.author)

            db.commit()
            await bot.process_commands(message)     # Sends message to commands

    elif message.content.lower() == 'omak':
        await bot.send_message(message.channel, ':middle_finger:')


# Bot commands
@bot.command()
async def version(): await bot.say(__version)


@bot.command(pass_context=True)
async def set_channel(ctx):
    """Sets the channel for the bot to talk in"""
    cursor.execute('UPDATE servers SET bot=? WHERE ID=?', (ctx.message.channel.id, ctx.message.server.id))
    db.commit()
    await bot.send_message(ctx.message.channel, '{} has been declared mine.'.format(ctx.message.channel.name))


@bot.command(pass_context=True, aliases=['record'])
async def rec(ctx):
    serid=ctx.message.server.id
    send = cursor.execute('SELECT record FROM servers WHERE ID =?',(serid,)).fetchall()[0][0]
    if send != 'N':
        cursor.execute('UPDATE servers SET record = ? WHERE ID = ?', ('N', serid))
        await bot.send_message(ctx.message.channel, 'Recording has been turned off.')
    else:
        cursor.execute('UPDATE servers SET record = ? WHERE ID = ?', ('Y', serid))
        await bot.send_message(ctx.message.channel, 'Recording has been turned on.')
        await record(ctx, 'HELLO WORLD!')
    db.commit()


@bot.command(pass_context=True)
async def trial(ctx):
    await bot.say(type(ctx) == discord.ext.commands.context.Context)


@bot.command()
async def say(*args):
    """Makes bot say whatever is passed to it"""
    await bot.say(' '.join(args))


@bot.command(pass_context=True)     # Pass context data which contains everything
async def created(ctx):
    """Finds when user account was created"""
    await bot.say('Your account was created at: {}'.format(ctx.message.author.created_at.strftime('%H:%M:%S, %d %a %b %y'))) # time formatting



@bot.command()
async def compliment():
    """Compliments the user"""
    await bot.say('<@{}>, you are amazing <3'.format(userid))


@bot.command()
async def hello():
    """Makes bot reply to user"""
    await bot.say("Hi, <@{}>".format(userid) + '.')


@bot.command()
async def on():
    """Changes bot's status to on"""
    await bot.change_presence(game=discord.Game(name='PyCharm'), status=discord.Status.online)


@bot.command()
async def kill(person):
    """Kills person by user"""
    await bot.say("<@{}> has killed {}! Bring in the police!".format(userid, person))


@bot.command()
async def die():
    """Makes the user kill themselves"""
    await bot.say('<@{}> have killed themself! :upside_down::gun:'.format(userid))


@bot.command(aliases=['bott'])
async def bots(*args):
    n = int(args[-1])
    for _ in range(n):
        await bot.say(' '.join(args[:-1]))
        await asyncio.sleep(5)
    await bot_purge(n*2)


async def bot_purge(n):
    await bot.purge_from(msg.channel, check=lambda x: True, limit=n)


@bot.command(pass_context=True)
async def purge(ctx):
    await bot.purge_from(ctx.message.channel, check= lambda x: True, limit=(int(ctx.message.content.split(' ')[1]) + 1))


@bot.command(pass_context=True, aliases=['exit'])
async def shutdown(ctx):
    if ctx.message.author.id != '235810944981139456':
        await bot.say('Fuck off :middle_finger:')
        return
    await bot.change_presence(status=discord.Status.offline)
    await asyncio.sleep(2)
    exit(5)

@bot.command(pass_context=True)
async def ping(ctx):
    for channel in ctx.message.server.channels:
        if channel.name == 'pings':
            await bot.send_message(channel, arg(ctx))
            break
    else:
        await bot.say('I did not find a pings channel to send the message to.')


with connect('main.db') as db:
    """Everything below here has to do with the mmorpg"""
    cursor = db.cursor()


    @bot.command(pass_context=True, aliases=['character_make', 'make_character'])
    async def create(ctx):
        """Creates a character if the user doesn't already have one"""
        try:
            name = ' '.join(ctx.message.content.split(' ')[1:-1])  # Gets name
            classs = ctx.message.content.split(' ')[-1]  # Get class
        except IndexError:  # Preparation for errors
            name = None
            classs = None
        if name is None or classs is None:  # Checks for wrong entry
            await bot.say('You have to enter a name and a class for the character eg:\n ```make_character Viktor Warrior```')
        elif classs.lower() != 'rogue' and classs.lower() != 'warrior' and classs.lower() != 'wizard':  # Cheks for wrong class entry
            await bot.say('You can only choose one of the three classes: warrior, wizard or rogue')
        elif ctx.message.author.bot:  # Checks for botting
            await bot.say('Bots cannot make characters')
        elif check(cursor, 'characters', 'ID', userid):  # Checks if the user already has a character
            extra = 'None'
            # Creates standarised class names and items
            if classs.lower() == 'warrior':
                extra = 'Armour, Great axe'
            elif classs.lower() == 'wizard':
                extra = 'Glasses, Wand'
            elif classs.lower() == 'rogue':
                extra = 'Dagger, Lockpick'
            cursor.execute('INSERT INTO characters(ID, name, class, exp, gold, level, extra) '
                           'VALUES (?, ?, ?, ?, ?, ?, ?)',
                           (userid, name.replace("'", "\'").capitalize(), classs.capitalize(), 0, 100, 1, extra))
            db.commit()
            await bot.say('You have successfuly created the character {}, class {}'.format(name, classs))
            await record('{} has created the character {}.'.format(char.username, name.replace("'", "\'")))
        else:
            await bot.say('You already have a character.')


    @bot.command(pass_context=True, aliases=['char'])
    async def character(ctx):
        """Checks if the user has a character and creates one if they don't"""
        if not char.char:  # Checks if the user has a character
            await bot.say('You do not have a character made please make a character by using the command make_character {name} {class}.')
        else:

            embed = Embed(              # Creates the character profile embed
                title='Character details:',
                colour=char.colour,
            )
            embed.set_footer(text='At {}'.format(datetime.datetime.utcnow().strftime('%H:%M:%S, %d %a %b %y')))
            if char.role == 'None':
                embed.set_author(name='{}'.format(char.username), icon_url=image)
            else:
                embed.set_author(name='{} <{}>'.format(char.username, char.role), icon_url=char.avatar)
            embed.add_field(name='Name', value=char.charname)
            for i in char.ach.split(', '):
                embed.add_field(name='Achievement', value=i)
            embed.add_field(name='Class', value=char.classs)
            embed.add_field(name='Exp', value='{}/{}'.format(char.exp, char.limit))
            embed.add_field(name='Gold', value="{}G".format(char.gold))
            embed.add_field(name='Level', value=char.lvl)
            embed.add_field(name='Reputation', value=char.rep)
            embed.add_field(name='Current quest', value=char.curquest)

            await bot.say(embed=embed)


    @bot.command(aliases=['inv', 'bag'])
    async def inventory():
        """Displays the user's items"""
        if check(cursor, 'characters', 'ID', userid):
            await bot.say('You do not have a character made please make a character by using the command make_character {name} {class}.')
        else:
            extra, name = cursor.execute('SELECT extra, name FROM characters WHERE ID = {}'.format(userid)).fetchall()[0]
            embed = Embed(  # Creates the inventory embed
                title='Character inventory:',
                colour=Colour.gold(),
                description='{} items'.format(len(extra.split(', ')))
            )
            embed.set_author(name=name)
            embed.set_footer(text='At {}'.format(datetime.datetime.utcnow().strftime('%H:%M:%S, %d %a %b %y')))
            for i in extra.split(', '):
                embed.add_field(name='Item', value=i)

            await bot.say(embed=embed)


    @bot.command(pass_context=True)
    async def stats(ctx):
        """Gets user's calculated stats"""

        embed = Embed(title='Stats', colour=Colour.dark_red())      # Creates user stats' embed
        embed.set_author(name=char.charname)
        embed.add_field(name='Armour', value=char.armour)
        embed.add_field(name='Damage', value=char.dmg)
        embed.add_field(name='Dodge', value=char.dodge)
        embed.set_footer(text='At {}'.format(datetime.datetime.utcnow().strftime('%H:%M:%S, %d %a %b %y')))
        await bot.say(embed=embed)


    @bot.command(pass_context=True, aliases=['ins'])
    async def inspect(ctx):
        """Displays other users' characters"""
        if len(ctx.message.mentions) > 1:
            await bot.say('You cannot inspect more than one person at a time.')
            return
        elif check(cursor, 'characters', 'ID', ctx.message.mentions[0].id):
            await bot.say('This person does not have a character.')
            return

        char = Character(ctx.message.mentions[0])

        embed = Embed(              # Creates the character profile embed
            title='Character details:',
            colour=char.colour,
        )
        embed.set_footer(text='At {}'.format(datetime.datetime.utcnow().strftime('%H:%M:%S, %d %a %b %y')))  # Gets and formats current date&time
        if char.role == 'None':
            embed.set_author(name='{}'.format(char.username))
        else:
            embed.set_author(name='{} <{}>'.format(char.username, char.role))
        embed.add_field(name='Name', value=char.charname)
        for i in char.ach.split(', '):
            embed.add_field(name='Achievement', value=i)
        embed.add_field(name='Class', value=char.classs)
        embed.add_field(name='Exp', value='{}/{}'.format(char.exp, char.limit))
        embed.add_field(name='Gold', value="{}G".format(char.gold))
        embed.add_field(name='Level', value=char.lvl)
        embed.add_field(name='Reputation', value=char.rep)
        embed.add_field(name='Current quest', value=char.curquest)

        embed.add_field(name='Armour', value=char.armour)
        embed.add_field(name='Damage', value=char.dmg)
        embed.add_field(name='Dodge', value=char.dodge)

        for i in char.extra.split(', '):
            embed.add_field(name='Item', value=i)

        await bot.say(embed=embed)


    @bot.command(pass_context=True, aliases=['battle', 'attack'])
    async def pvp(ctx):
        """Starts a pvp battle between the user and the person mentioned"""
        if not 0 < len(ctx.message.mentions) < 2:  # Checks that the battle is only between two users
            await bot.say('Wrong amount of mentions.')
            return

        char2 = Character(ctx.message.mentions[0])
        text = await bot.say('The battle will begin shortly')
        turn = True
        data = []
        while char.armour > 0 and char2.armour > 0:
            s = '{}: {}/{}hp VS {}: {}/{}hp\n'.format(
                char.charname.upper(), char.armour, char.health, char2.charname.upper(), char2.armour, char2.health)
            if turn:
                if randint(0, 99) < char2.dodge:
                    data.append('{} has attacked but {} dodged!\n'.format(char.charname, char2.charname))
                else:
                    data.append('{} has delt {} damage!\n'.format(char.charname, char.dmg))
                    char2.armour -= char.dmg
            else:
                if randint(0, 99) < char.dodge:
                    data.append('{} has attacked but {} dodged!\n'.format(char2.charname, char.charname))
                else:
                    data.append('{} has delt {} damage!\n'.format(char2.charname, char2.dmg))
                    char.armour -= char2.dmg

            if len(data) > 5:
                s += ''.join(data[-5:])
            else:
                s += ''.join(data)

            await asyncio.sleep(.8)
            turn = not turn  # Flips turn so other user attacks
            await bot.edit_message(text, s)
        if char.armour <= 0:
            await bot.say('{} has won!'.format(char2.charname))
            await record(ctx, '{} has battled {} and {} has won!'.format(char.username, char2.username, char2.username))
        elif char2.armour <= 0:
            await bot.say('{} has won!'.format(char.charname))
            await record(ctx, '{} has battled {} and {} has won!'.format(char.username, char2.username, char.username))


    @bot.command()
    async def quests(n=None):
        """Displays all the quests in the database"""
        if n is None:
            await bot.say('You need to give in the level of quests thats you want to retrieve eg:\n ```quests 1```')
        else:
            cursor.execute('SELECT name, time FROM quests WHERE level = {} GROUP BY requirement, name ORDER BY name, time '.format(n))
            lines = cursor.fetchall()
            s = 'Details:\n``Level {} quests``\n'.format(n)
            s += ('\n```{:<30}    {:<5}```\n'.format('Name', 'Time'))  # Displayed in indent monospace mode so the characters line up
            for name in lines:
                s += '```{:<30}    {:<5}```'.format(*name)  # Adding the quests with indent monospace style
            await bot.say(s)


    @bot.command()
    async def quest(*args):
        """Displays the information for the quest"""
        name = ' '.join(args).capitalize()
        if check(cursor, 'quests', 'name', name):  # If the quest exists
            await bot.say('Quest {} was not found.'.format(name))
        else:
            lines = cursor.execute('SELECT * FROM quests WHERE name = "{}"'.format(name.replace("'", '\''))).fetchall()[0]  # Retrieves all quest data
            desc, time, exp, gold, level, requirement, achievement, reputation, reward = lines[1:]
            embed = Embed(              # Creates quest embed
                title=name,
                description=desc,
                colour=Colour.red()
            )
            embed.add_field(name='Time', value='{}min'.format(time))
            embed.add_field(name='Exp', value=exp)
            embed.add_field(name='Gold', value='{}G'.format(gold))
            embed.add_field(name='Achievement', value=achievement)
            embed.add_field(name='Reputation', value=reputation)
            embed.add_field(name='Level', value=level)
            if requirement.find(', ') != -1:            # If there is multiple requirements do it a special way
                embed.add_field(name='Reward', value=reward, inline=False)
                for i in requirement.split(', '):
                    embed.add_field(name='Requirement', value=i, inline=True)
            else:
                embed.add_field(name='Reward', value=reward)
                embed.add_field(name='Requirement', value=requirement)

            await bot.say(embed=embed)


    @bot.command(pass_context=True, aliases=['log_quest'])
    async def start(ctx):
        """Starts quest for user"""
        name = arg(ctx).capitalize().replace("'", "\'")
        if check(cursor, 'quests', 'name', name):  # Checks if quest exists
            await bot.say('Quest {} was not found.'.format(name))
            return
        qr = cursor.execute('SELECT requirement FROM quests WHERE name = "{}"'.format(name)).fetchall()[0][0]
        cr = char.extra.split(', ')

        if char.curquest != 'Currently no pending quests':  # Checks for already pending quests
            await bot.say('You already have a quest pending.')
            return
        elif qr.lower() != 'none':
            for i in qr.lower().split(', '):
                if i not in [x.lower() for x in cr]:# Checks if user has requirement for quest
                    await bot.say('You do not have the requirements to do this.')
                    return

        failure = 20
        ql, achv = cursor.execute('SELECT level, achievement FROM quests WHERE name = "{}"'.format(name)).fetchall()[0] # Gets quest level
        cl = char.lvl
        if ql == 0:
            failure = 0
        elif achv != 'None' and ql > 30:
            failure = 40

        if ql > cl:  # Changes failure rate
            failure += int((ql-cl) * 8.67)
        elif cl > ql:
            failure -= int((cl-ql) * 5)

        if char.curpet != 'None':
            failure -= char.pet['lvl']

        failure = min(max(failure, 0), 100)
        tim, exp, gold =  cursor.execute('SELECT time, exp, gold FROM quests WHERE name = "{}"'.format(name)).fetchall()[0]  # Gets quest info
        cursor.execute('INSERT INTO logs(ID, time, duration, exp, gold, name, failure) VALUES (?, ?, ?, ?, ?, ?, ?)',
                       (char.id, int(time.time()), tim, exp, gold, name, failure))  # Logs quest info
        db.commit()             # commits changes
        if tim < 60:
            await bot.say('Your character has started adventuring on quest {} for {}mins, {} exp and {}G, wish them luck!' .format(name, tim, exp, gold))
            # prints quest confirmation
        else:
            await bot.say('Your character has started adventuring on quest {} for {}h and {}mins, {} exp and {}G, wish them luck!'
                          .format(name, (tim//60), (tim % 60), exp, gold))

        await record(ctx, '{} has started on the quest {}.'.format(char.username, name))


    @bot.command(pass_context=True)
    async def abandon(ctx):
        """Abandons current quest"""
        if not char.char:
            await bot.say('You do not have a character.')
            return
        elif char.curquest == 'Currently no pending quests':
            await bot.say('You currently have no pending quests to give up.')
            return
        name = cursor.execute('SELECT name FROM logs WHERE ID = ?', (char.id,)).fetchall()[0][0]
        cursor.execute('DELETE FROM logs WHERE ID = ?', (char.id,))
        db.commit()
        await bot.say('{} quest abandoned'.format(name))
        await record(ctx, '{} has abandoned the quest {}.'.format(char.username, name))


    @bot.command(pass_context=True, aliases=['collect_quest', 'finish'])
    async def collect(ctx):
        """Collects already started quest"""
        lines = cursor.execute('SELECT time, duration, exp, gold, name, failure FROM logs WHERE ID = ?', (char.id,)).fetchall()
        if lines == []:  # Checks if there are currenlty any pending quests
            await bot.say('You do not currently have a pending request.')
        else:
            tim, duration, exp, gold, name, failure = lines[0]
            achievement, qrep, item = cursor.execute('SELECT achievement, reputation, reward FROM quests WHERE name = "{}"'.format(name)).fetchall()[0]
            end = int(tim + (duration * 60))
            if time.time() < end:  # Checks if the quest duraation has finished
                until = (end - time.time())
                await bot.say('Your quest is not done yet there is still {} mins and {} seconds.'.format(int(until / 60), int(until % 60)))
                return
            elif randint(0, 99) < failure:
                cursor.execute('DELETE FROM logs WHERE ID = {}'.format(userid))  # Deletes quest from logs
                db.commit()
                await bot.say('You have failed this quest. Good luck next time!')
                return

            char.exp += exp  # Updates values
            char.gold += gold
            char.rep += qrep
            if char.exp > char.limit:  # Checks if the user has leveled up
                char.exp = char.exp % char.limit  # Calculates leftover xp
                char.lvl += 1
                await bot.say('Congratulations you have reached level {}'.format(char.lvl))  # Prints level up message

            if achievement == 'None':
                pass
            elif achievement in char.ach.split(', '):
                pass
            else:
                await bot.say('Congratulations! You have gotten the achievement {}.'.format(achievement))
                if char.ach == 'None':  # Leaves no beginning None
                    char.ach = achievement.capitalize()
                else:
                    char.ach += ', {}'.format(achievement)

            if item == 'None':
                pass
            elif item in char.extra.split(', '):
                pass
            else:
                if randint(0, 99) < 20:
                    if char.extra == 'None':
                        char.extra = item
                    else:
                        char.extra += ', {}'.format(item)

                    await bot.say('Congratulations! You have found the item {}.'.format(item))
            cursor.execute('UPDATE characters SET exp=?, gold=?, level =?, achievements=?, reputation=?, extra=? WHERE ID = ?',
                           (char.exp, char.gold, char.lvl, char.ach, char.rep, char.extra, char.id))
            db.commit()
            if char.curpet != 'None':
                char.pet['exp'] += int(exp*(10/100))
                if char.pet['exp'] > char.pet['limit']:
                    char.pet['exp'] %= char.pet['limit']
                    char.pet['lvl'] += 1
                char.happiness()
                char.pet_update()
                char.gold -= 100
                char.char_update()
            # Updates character stats
            db.commit()
            await bot.say('"{}" quest collected.'.format(name))
            await record(ctx, '{} has finished the quest {}.'.format(char.username, name))
            cursor.execute('DELETE FROM logs WHERE ID = {}'.format(char.id))  # Deletes quest from logs
            db.commit()


    @bot.command(pass_context=True, aliases=['store'])
    async def shop(ctx):
        """Displays all the shop items"""
        lines = cursor.execute('SELECT name, price FROM shop ORDER BY price, name, description').fetchall()      # Gets all items from shop
        s = '{}: {}G \n```{:<30}    {:<6}```\n'.format(char.charname, char.gold, 'Items', 'Price')
        for n, p in lines:
            s += '```{:<30}    {:<6}```'.format(n, p)          # Adds items with indent monospace style
        s += '\n{}: {}G'.format(char.charname, char.gold)
        await bot.say(s)


    @bot.command()
    async def identify(*args):
        """Displays all informations about supplied item"""
        name = ' '.join(args).capitalize()
        if check(cursor, 'shop', 'name', name):             # Checks if the item exists
            await bot.say("The item you want to inspect does not exist.")
        else:
            desc, price, classs, req = cursor.execute('SELECT description, price, class, requirement FROM shop WHERE name = "{}"'.
                                                      format(name)).fetchall()[0]  # Gets item details

            embed = Embed(          # Creates item embed
                title=name,
                description=desc,
                colour=Colour.green()
            )
            embed.add_field(name='Price', value=price)
            embed.add_field(name='Class requirement', value=classs)
            embed.add_field(name='Item requirment', value=req)

            await bot.say(embed=embed)


    @bot.command(pass_context=True)
    async def buy(ctx):
        """Buys item for user's character"""
        name = arg(ctx).capitalize().replace("'", "\'")
        if not char.char:             # Checks if the user has a character
            await bot.say('You need to make a character first before you can access the shop, use the command make_character {name} {class}.')
            return
        elif check(cursor, 'shop', 'name', name):               # Checks if the item exists
            await bot.say('This item does not exist')
            return
        desc, ig, ic, ir  = cursor.execute("SELECT description, price, class, requirement FROM shop WHERE name ='{}'".format(name)).fetchall()[0]
        if ig > char.gold:  # Checks if the user has enough money to buy the item
            await bot.say('You do not have enough money to buy this item.')
            return
        elif char.extra != 'None' and name in char.extra.split(', '):           # Checks if user already has item
            await bot.say('You already have this item.')
            return
        elif ic != 'None' and ic != char.classs:                         # Checks if the item is not class specific
            await bot.say('This is item is locked off only for the {} class.'.format(ic))
            return
        elif ir != 'None' and ir not in char.extra.split(', '):         # Checks if the user does not already have the item
            await bot.say('This item requires you to have {} before you buy it.'.format(ir))
            return
        char.gold -= ig
        if char.extra == 'None': char.extra = name
        else: char.extra += ', {}'.format(name)         # Updates users items
        cursor.execute("UPDATE characters SET gold ={}, extra= '{}' WHERE ID = {}".format(char.gold, char.extra, char.id))
        db.commit()
        await bot.say('Congratulations!:tada: You bought {}: ``{}`` for {}G and now you have {}G left'.format(name, desc, ig, char.gold))
        await record(ctx, '{} has bought the item {}.'.format(char.username, name))


    @bot.command(aliases=['craft_list'])
    async def schemes():
        lines = cursor.execute('SELECT name, requirements FROM craft ORDER BY name').fetchall()  # Gets all items from shop
        s = 'Details: \n```{:<30}    {:<30}```\n'.format('Item', 'Requirements')
        for n, p in lines:
            s += '```{:<30}    {:<30}```'.format(n, p)  # Adds items with indent monospace style
        await bot.say(s)


    @bot.command(pass_context=True)
    async def plan(ctx):
        item = arg(ctx).capitalize()
        if check(cursor, 'craft', 'name', item):             # Checks if the item exists
            await bot.say("The item you want to plan does not exist.")
        else:
            name, desc, classs, level, req = cursor.execute('SELECT name, description, class, level, requirements FROM craft WHERE name = "{}"'.
                                                      format(item)).fetchall()[0]  # Gets item details

            embed = Embed(          # Creates item embed
                title=name,
                description=desc,
                colour=Colour.purple()
            )
            embed.add_field(name='Class requirement', value=classs)
            embed.add_field(name='Level', value=level)
            for i in req.split(', '):
                embed.add_field(name='Item requirment', value=i)

            await bot.say(embed=embed)


    @bot.command(pass_context=True)
    async def craft(ctx):
        """Attempts to craft an item"""
        item = arg(ctx)
        item = item.capitalize()
        if not char.char:
            await bot.say('You need to create a character first to craft items.')
            return
        elif check(cursor, 'craft', 'name', item):
            await bot.say('This item does not exist.')
            return
        else:
            name, desc, classs, level, req = cursor.execute('SELECT name, description, class, level, requirements FROM craft WHERE name = ?', (item,)).fetchall()[0]
            if char.classs != classs:
                await bot.say('You cannot craft this item as it is locked for the {} class'.format(classs))
                return
            elif level > char.lvl:
                await bot.say('Your level is not high enough to craft this items.')
                return
            else:
                for i in req.split(', '):
                    if i not in char.extra.split(', '):
                        await bot.say('You do not have all the items needed to craft this {}'.format(item))
                        return

        ue = char.extra.split(', ')
        for i in req.split(', '):
            ue.remove(i)
        ue.append(item)
        char.extra = ', '.join(ue)
        cursor.execute('UPDATE characters SET extra =? WHERE ID =?', (char.extra, char.id))
        await bot.say('You have sucessfuly carfted the item: {}'.format(item))
        await record(ctx, '{} has crafted {}'.format(char.username, item))
        db.commit()


    @bot.command(aliases=['book'])
    async def archive():
        l = cursor.execute('SELECT name FROM lore').fetchall()
        s = 'Archive data:\nName:\n'
        for i in l:
            s += '```{}```'.format(*i)
        await bot.say(s)


    @bot.command()
    async def read(*s):
        s = ' '.join(s)
        s = s.capitalize()
        if check(cursor, 'lore', 'name', s):
            await bot.say('The archive has no information about this, please tell us more...')
            return

        name, desc, lvl, req, ach, rep = cursor.execute('SELECT name, description, level, requirements, achievement, reputation FROM lore WHERE name =?',(s,)).fetchall()[0]
        ul, ue, ua, ur = cursor.execute('SELECT level, extra, achievements, reputation FROM characters WHERE ID=?', (userid,)).fetchall()[0]
        if not char.char:
            await bot.say('The archive only serves those who have power. Come back as a hero.')
        elif lvl > char.lvl:
            await bot.say('You need to be at least level {} to access this information. Come back when you\'ve grown up.'.format(lvl))
            return
        elif req != 'None':
            if req not in char.extra.split(', '):
                await bot.say('You need {} to access this data. I would suggest you go get it.'.format(req))
                return
        elif ach != 'None':
                if ach not in char.ach.split(', '):
                    await bot.say('You do need to earn the achievement {} before you can access this data. Chop! Chop! Get to work!'.format(ach))
                    return
        elif rep != 0:
            if rep < 0:
                if char.rep > rep:
                    await bot.say('You need to reach {} rep to get this data. Wanna join the dark side?'.format(rep))
                    return
            else:
                await bot.say('You need to reach {} rep to get to this data. Have you considered joining a charity?'.format(rep))
                return

        embed = Embed(title=name, description=desc, colour=int('0xF0FFFF', 16))

        await bot.say(embed=embed)


    @bot.command(aliases=['pet_store'])
    async def zookeeper():
        lines = cursor.execute('SELECT species, price FROM zoo ORDER BY species').fetchall()  # Gets all items from shop
        s = 'Details: \n {}: {}G\n```{:<30}    {:<30}```\n'.format(char.charname, char.gold, 'Species', 'Price')
        for sp, p in lines:
            s += '```{:<30}    {:<30}```'.format(sp, p)  # Adds items with indent monospace style
        await bot.say(s)


    @bot.command(pass_context=True)
    async def check_out(ctx):
        species = arg(ctx).capitalize()
        if check(cursor, 'zoo', 'species', species):
            await bot.say('This pet does not exist')
            return
        desc, species, price, heal, damage, armour = cursor.execute('SELECT description, species, price, heal, damage, armour FROM zoo WHERE species =?',
                                                                    (species,)).fetchall()[0]
        embed = Embed(title=species, description=desc)
        embed.add_field(name='Species', value=species)
        embed.add_field(name='Price', value=price)
        embed.add_field(name='Heal', value=heal)
        embed.add_field(name='Damage', value=damage)
        embed.add_field(name='Armour', value=armour)

        await bot.say(embed=embed)


    @bot.command(pass_context=True)
    async def adopt(ctx):
        species = arg(ctx).capitalize()
        if not char.char:
            await bot.say('I\'m sorry but we only adobt fighting creatures to heros, would you be interested in a hamster?')
            return
        elif check(cursor, 'zoo', 'species', species):
            await bot.say('We do not have any pets in that species, did you discover a new type?')
            return
        price = cursor.execute('SELECT price FROM zoo WHERE species=?', (species,)).fetchall()[0][0]
        if char.curpet != 'None':
            if species in char.pettypes:
                await bot.say('You can only have one pet per species.')
                return
        if price > char.gold:
            await bot.say('You do not have enough income to adobt this pet')
            return
        desc = cursor.execute('SELECT description FROM zoo WHERE species=?', (species,)).fetchall()[0][0]
        char.gold -= price
        await bot.say('What do you want to name it?')
        name = await bot.wait_for_message(author=ctx.message.author, channel=ctx.message.channel)
        cursor.execute('INSERT INTO pets VALUES (?, ?, ?, ?, ?, ?)',(char.id, name.content.capitalize(), species, 0, 1, 100))
        db.commit()
        char.char_update()
        await bot.say('Congratulations! You have rescued the a {} pet: {} Thank you for helping this poor animal!'.format(species, desc))
        await record(ctx, '{} has adopted a {} pet called {}.'.format(char.username, species, name.content.capitalize()))


    @bot.command(pass_context=True)
    async def my_pets(ctx):
        embed = Embed(title='Pet room', description='{} pets'.format(len(char.pettypes)))
        for i in char.pettypes:
            embed.add_field(name='Pet', value=i)
            embed.add_field(name='Name', value=char.pets[i]['name'])
            embed.add_field(name='Happiness', value=char.pets[i]['happiness'])

        await bot.say(embed=embed)


    @bot.command(pass_context=True)
    async def my_pet(ctx):
        name = arg(ctx).capitalize()
        if name not in char.pettypes:
            await bot.say('You do not have this pet.')
            return

        embed = Embed(title=char.pets[name]['name'])
        embed.add_field(name='Exp', value=char.pets[name]['exp'])
        embed.add_field(name='Level', value=char.pets[name]['lvl'])
        embed.add_field(name='Happiness', value=char.pets[name]['happiness'])
        embed.add_field(name='Heal', value=char.pets[name]['heal'])
        embed.add_field(name='Damage', value=char.pets[name]['dmg'])
        embed.add_field(name='Armour', value=char.pets[name]['armour'])

        await bot.say(embed=embed)


    @bot.command(pass_context=True)
    async def interact(ctx):
        species = arg(ctx).capitalize()
        if char.curpet == 'None':
            await bot.say('You do not have a pet to interact with.')
            return
        char.pet['happiness'] += 20
        gif = choice([
            'mOxCUSoRZ7vDq/giphy.gif', 't3yZAynLPVkGY/200w.gif', 'Ul16jlcdV1B04/200w.gif', 'l0ExvA6hnrdzQ5zoI/200w.gif', 'xTiTnp3zOLUGbBF4ME/200w.gif',
            'OzjugO1GZzaxy/200w.gif'

        ])
        embed= Embed(title='You have sucessfully petted your pet, here is a special surprise for you')
        embed.set_image(url='https://media.giphy.com/media/' + gif)
        await bot.say(embed=embed)


    @bot.command(pass_context=True)
    async def set_pet(ctx):
        species = arg(ctx).capitalize()
        if species not in char.pettypes:
            await bot.say('You do not own this type of pet to set it as your companion.')
            return
        cursor.execute('UPDATE characters SET pet=? WHERE ID=?', (species, char.id))
        db.commit()


    @bot.command(pass_context=True)
    async def lose(ctx):
        species = arg(ctx).capitalize()
        if species not in char.pettypes:
            await bot.say('You do not own a pet of this species.')
            return
        cursor.execute('DELETE FROM pets WHERE ID=? AND species=?', (char.id, species))
        if char.curpet == species:
            cursor.execute('UPDATE characters SET pet=? WHERE ID=?', ('None', char.id))
        db.commit()
        await bot.say('You have lost the pet type {}.'.format(species))
        await record(ctx, '{} has lost the pet type {}.'.format(char.username, species))

    @bot.command(pass_context=True, aliases=['pet_battle'])
    async def pokemon(ctx):
        if not 0 < len(ctx.message.mentions) < 2:  # Checks that the battle is only between two users
            await bot.say('Wrong amount of mentions.')
            return
        char2= Character(ctx.message.mentions[0])
        text = await bot.say('The battle will begin shortly')
        turn = True
        data = []
        while char.pet['armour'] > 0 and char2.pet['armour']> 0:
            s = '{}: {}/{}hp VS {}: {}/{}hp\n'.format(
                char.pet['name'].upper(), char.pet['armour'], char.pet['health'],
                char2.pet['name'].upper(), char2.pet['armour'], char2.pet['health'])
            if turn:
                if randint(0, 99) < ((char.pet['happiness']/1000)*100):
                    data.append('{} has delt {}dmg and managed to heal themselves!\n'.
                                format(char.pet['name'], char.pet['dmg']))
                    char.pet['armour'] = min(char.pet['health'], char.pet['armour']+char.pet['heal'])
                    char2.pet['armour'] -= char.pet['dmg']
                else:
                    data.append('{} has delt {} damage!\n'.format(char.pet['name'], char.pet['dmg']))
                    char2.pet['armour'] -= char.pet['dmg']
            else:
                if randint(0, 99) < ((char2.pet['happiness']/1000)*100):
                    data.append('{} has delt {}dmg and managed to heal themselves!\n'.
                                format(char2.pet['name'], char2.pet['dmg']))
                    char2.pet['armour'] = min(char2.pet['health'], char2.pet['armour'] + char2.pet['heal'])
                    char.pet['armour'] -= char2.pet['dmg']
                else:
                    data.append('{} has delt {} damage!\n'.format(char2.pet['name'], char2.pet['dmg']))
                    char.pet['armour'] -= char2.pet['dmg']

            if len(data) > 5:
                s += ''.join(data[-5:])
            else:
                s += ''.join(data)

            await asyncio.sleep(.8)
            turn = not turn  # Flips turn so other user attacks
            await bot.edit_message(text, s)
        if char.pet['armour'] <= 0:
            await bot.say('{} has won!'.format(char2.pet['name']))
            await record(ctx, '{}\'s pet has battled {}\'s pet and {}\'s pet has won!'.
                         format(char.username, char2.username, char2.username))
        elif char2.pet['armour'] <= 0:
            await bot.say('{} has won!'.format(char.pet['name']))
            await record(ctx, '{}\'s pet has battled {}\'s pet and {}\'s pet has won!'.
                         format(char.username, char2.username, char.username))


    @bot.command(pass_context=True)
    async def start_ship(ctx):
        if 'Ship' not in char.extra.split(', '):
            await bot.say('Please buy a ship before starting your sea adventures.')
            return
        await bot.say('Please enter the name of your ship:')
        name = await bot.wait_for_message(author=ctx.message.author, channel=ctx.message.channel)
        cursor.execute('INSERT INTO ships VALUES (?, ?, ?, ?, ?, ?)', (char.id, name.content.capitalize(), 0, 1, 1, 'None'))
        db.commit()


    @bot.command(pass_context=True)
    async def sail(ctx):
        try:
            n = int(arg(ctx))
        except (TypeError, ValueError):
            await bot.say('Please enter a number for the amount of time you wish to sail for.')
            return

        if char.ship == 'None':
            await bot.say('Get a ship before you set sail.')
            return
        elif char.sailing:
            await bot.say('You are already sailing.')
            return
        elif char.shiplvl < (n/60):
            await bot.say('Your level {} ship cannot sail for this long.'.format(char.shiplvl))
            return

        cursor.execute('INSERT INTO shiplogs VALUES (?, ?, ?)', (char.id, int(time.time()), n))
        db.commit()
        await bot.say('You have started sailing.')


    @bot.command(pass_context=True)
    async def dock(ctx):
        if check(cursor, 'shiplogs', 'ID', char.id):
            await bot.say('You did not go sailing.')
            return
        elif char.docktime > time.time():
            await bot.say('Your ship did not finish sailing.')
            return

        char.gold += (char.sailduration /60) *50
        char.shipexp += char.sailduration
        if char.shipexp > char.shiplimit:
            char.shipexp %= char.shiplimit
            char.shiplvl += 1
            char.crew += char.shiplvl

        char.ship_update()
        char.char_update()
        cursor.execute('DELETE FROM shiplogs WHERE ID=?', (char.id,))
        db.commit()
        await bot.say('You have finished sailing.')

    @bot.command(pass_context=True)
    async def upgrades(ctx):
        lines = cursor.execute('SELECT name, price FROM cabin ORDER BY price, name, description').fetchall()  # Gets all items from shop
        s = '{}: {}G \n```{:<30}    {:<6}```\n'.format(char.charname, char.gold, 'Improvement', 'Price')
        for n, p in lines:
            s += '```{:<30}    {:<6}```'.format(n, p)  # Adds items with indent monospace style
        s += '\n{}: {}G'.format(char.charname, char.gold)
        await bot.say(s)

    @bot.command(pass_context=True)
    async def improve(ctx):
        item = arg(ctx).capitalize()
        if item in char.improve.split(', '):
            await bot.say('You already have this improvement.')
            return

        if check(cursor, 'cabin', 'name', item):
            await bot.say('This improvement does not exist.')
            return

        price, req, crew, lvl = cursor.execute('SELECT price, requirement, crew, level FROM cabin WHERE name=?', (item,)).fetchall()[0]

        if price > char.gold:
            await bot.say('You do not have enough gold for this item.')
            return
        elif crew > char.crew:
            await bot.say('You do not have enough crew to buy this item.')
            return
        elif lvl > ship.lvl:
            await bot.say('Your level is not high enough to buy this improvement.')
        elif req != 'None':
            for i in req.split(', '):
                if i not in char.improve.split(', '):
                    await bot.say('You do not have the requirement to build this imrpovement.')
                    return

        char.gold -= price
        if char.improve == 'None':
            char.improve = '{}'.format(item)
        else:
            char.improve += ', {}'.format(item)
        char.char_update()
        char.ship_update()
        await bot.say('You have sucessfult bought an improvement.')

    @bot.command(pass_context=True)
    async def ship_battle():
        if not 0 < len(ctx.message.mentions) < 2:  # Checks that the battle is only between two users
            await bot.say('Wrong amount of mentions.')
            return

        char2 = Character(ctx.message.mentions[0])
        text = await bot.say('The battle will begin shortly')
        turn = True
        data = []
        while char.shiparmour > 0 and char2.shiparmour > 0:
            s = ':ship: {}: {}/{}hp VS :ship: {}: {}/{}hp\n'.format(
                char.ship.upper(), char.shiparmour, char.shiphealth, char2.ship.upper(), char2.shiparmour, char2.shiphealth)
            if turn:
                data.append('{} has delt {} damage!\n'.format(char.ship, char.shipdmg))
                char2.shiparmour -= char.shipdmg
            else:
                data.append('{} has delt {} damage!\n'.format(char2.ship, char2.shipdmg))
                char.shiparmour -= char2.shipdmg


            if randint(0, 99) < 20:
                n = randint(0, 99)
                if n > char.shipluck:
                    data.append('The storm has come dealing {} to {}!\n'.format(char.shiphealth*(5/100), char.ship))
                    char.shiparmour -= char.shiphealth*(5/100)
                if n > char.shipluck:
                    data.append('The storm has come dealing {} to {}!\n'.format(char2.shiphealth*(5/100), char2.ship))
                    char2.shiparmour -= char2.shiphealth*(5/100)

            if len(data) > 5:
                s += ''.join(data[-5:])
            else:
                s += ''.join(data)

            await asyncio.sleep(.8)
            turn = not turn  # Flips turn so other user attacks
            await bot.edit_message(text, s)
        if char.armour <= 0:
            await bot.say('{} has won!'.format(char2.ship))
            await record(ctx, '{}\'s ship has battled {}\'s ship and {}\'s ship has won!'.format(char.username, char2.username, char2.username))
        elif char2.armour <= 0:
            await bot.say('{} has won!'.format(char.ship))
            await record(ctx, '{}\'s ship has battled {}\'s ship and {}\'s ship has won!'.format(char.username, char2.username, char.username))


    @bot.command(pass_context=True)
    async def arena(ctx):
        if char.curquest != 'Currently no pending quests':
            await bot.say('You are currently on a quest so you cannot enter the arena.')
            return
        if char.curpet != 'None':
            strength = ceil(char.lvl*2 + char.pet['lvl']/2)
        else:
            strength = char.lvl*2
        cursor.execute('INSERT INTO arenalogs VALUES (?, ?, ?, ?, ?)', (self.id, time.time(), 5, strength, 1))
        db.commit()
        await bot.say('You have entered the arena, good luck!')

    @bot.command(pass_context=True)
    async def rest(ctx):
        if self.stage == 0:
            await bot.say('You did not start the arena to rest.')
            return
        elif self.exit > time.time():
            await bot.say('You are still on stage {}.'.format(self.stage))
            return
        if char.strength < randint(0, self.stage*2):
            await bot.say('You have failed the arena.')
            return

        await bot.say('You have finished stage {}. Would you like to continue?'.format(self.stage))
        ans = bot.wait_for_message(author=ctx.message.author, channel=ctx.message.channel)
        if search('\Wy\W', ans, I):
            await bot.say('You have progressed on to the next stage!')
            char.stage += 1
            char.arena_update()
            return

        for i in range(1, char.stage+1):
            cursor.execute('SELECT name, weight FROM arenarewards WHERE level = ?', (i,)).fetchall()
            names = [x for x, y in n]
            weights = [y for x, y in n]
            item = choices(names, weights)
            if item in char.extra.split(', '):
                await bot.say('You have found an item that you already have.')
            elif char.extra == 'None':
                char.extra = item
                await bot.say('You have cashed out and earned {}!')
            else:
                await bot.say('You have cashed out and earned {}!')
                char.extra += ', {}'.format(item)

        cursor.execute('DELETE FROM arenalogs WHERE ID=?', (char.id,))
        char.char_update()
        db.commit()

    @bot.command(pass_context=True)
    async def arenarewards(ctx):
        lines = cursor.execute('SELECT name, level FROM arenarewards ORDER BY level').fetchall()  # Gets all items from shop
        s = '{}: {}G \n```{:<30}    {:<6}```\n'.format(char.charname, char.gold, 'Name', 'At stage')
        for n, l in lines:
            s += '```{:<30}    {:<6}```'.format(n, l)  # Adds items with indent monospace style
        s += '\n{}: {}G'.format(char.charname, char.gold)
        await bot.say(s)

    @bot.command(pass_context=True)
    async def check_reward(ctx):
        name = arg(ctx).capitalize()
        if check(cursor, 'arenarewards', 'name', name):             # Checks if the item exists
            await bot.say("The reward you want to inspect does not exist.")
        else:
            name, desc, stage, chance = cursor.execute('SELECT name, description, level, weight FROM arenarewards WHERE name =?',
                                                      (name,)).fetchall()[0]  # Gets item details

            embed = Embed(          # Creates item embed
                title=name,
                description=desc,
                colour=Colour.dark_green()
            )
            embed.add_field(name='Stage', value=stage)
            embed.add_field(name='Chance', value='{}%'.format(chance))

            await bot.say(embed=embed)

    @bot.command(pass_context=True)
    async def subclasses(ctx):
        await bot.say('Not ready')
        return
        if char.sub != 'None':
            await bot.say('You already have a subclass.')
            return
        elif char.lvl < 20:
            await bot.say('Your character is not a high level enough to attempt to achieve a subclass')
            return

        if char.classs == 'Warrior':
            await bot.say('You have the option to choose between: paladin, guardian, mercenary.')
            ans = await bot.wait_for_message(author=ctx.message.author, channel=ctx.message.channel)
            ans = ans.content.lower()
            while ans != 'paladin' and ans != 'guardian' and ans != 'mercenary':
                await bot.say('You did not enter the right subclass.')
                ans = await bot.wait_for_message(author=ctx.message.author, channel=ctx.message.channel)
                ans = ans.content.lower()



    @bot.command(pass_context=True)
    async def tavern(ctx):
        if not char.char:
            await bot.say('Please make a character to access the heros tavern.')
            return
        await bot.say('What would you like to do here?\n``gamble``, ``fight``, ``drink``, ``bid``')
        ans = bot.wait_for_message(60, author=ctx.message.author, channel=ctx.message.channel)
        ans = ans.content.lower()
        if ans == 'gamble':
            n = await bot.wait_for_message('How much would you like to gamble:')
            n = n.content.lower()
            try:
                n = int(n)
            except (ValueError, NameError):
                await bot.say('Please enter an integer value.')
                return

            if n > char.gold:
                await bot.say('You do not have this much money to gamble with, stop trying to take loans!')
                return
            txt = await bot.say('Pulling lever... :slot_machine:')
            char.gold -= n
            mult = (n / 10000) + 1
            if randint(0, 99) < randint(min(max((char.rep / 5), 0), 49), 50):
                char.gold += int(n * mult)
                await bot.edit_message(txt, 'Congratulations! Your {}G have become {}G and now you have {}G in total!'.format(n, int(n * mult), char.gold))
                await record(ctx, '{} has gained {}G.'.format(char.username, (n * mult) - n))
            else:
                await bot.edit_message(txt, "I'm sorry, better luck next time!")
                await record(ctx, '{} has lost {}G.'.format(char.username, n))

            cursor.execute('UPDATE characters SET gold = ? WHERE ID  = ?', (char.gold, char.id))
            db.commit()
        elif ans == 'fight':
            if randint(0, 99) > char.lvl*2:
                await bot.say('You have fought someone stronger thank you and lost + your money got taken away. GG')
                char.gold -= (char.gold*(1/100))
                char.char_update()
            else:
                await bot.say('Congrats, you won this fight and some people were impressed by your bravery.')
                if char.ship != 'None':
                    char.crew += 5
                    char.ship_update()
        elif ans == 'drink':
            await bot.say('You have been challenged to a drinking competition, will you accept?')
            ans = await bot.wait_for_message(20, author=ctx.message.author, channel=ctx.message.channel)
            ans = ans.content.lower()
            if search('\Wy\W', ans, I):
                luck = self.lvl*2 + abs(char.rep) if char.rep < 0 else char.lvl * 2
                if randint(0,99) > luck:
                    await bot.say('You have passed out from too much drinking and have gotten pickpocketed.')
                    char.gold -= (char.gold * (1 / 100))
                    char.char_update()
                else:
                    await bot.say('The other person has passed out drunk and you win your drinking bet. GGWP')
                    char.gold += (char.gold * (1 / 100))
                    char.char_update()
            elif ans is None:
                await bot.say('You took too long to answer and now your hero has started daydreaming, happy?')
                return
            else:
                await bot.say('Then why did you pick the drinking option in the first place??')
                return
        elif ans == 'bid':
            await bot.say('Not available')
            return
            n = cursor.execute('SELECT count(*) FROM tavern').fetchall()[0][0]
            item, price = cursor.execute('SELECT item, price FROM tavern').fetchall()[randint(0, n)]
            await bot.say('We will now bid on the item: {}, well start the bidding at {}\n One more person needs to join the bidding, to join type ``bid``'
                          .format(item, price))
            def biddable(msg):
                char2= Character(msg.author)
                return char2.char

            ans = await bot.wait_for_message(60, channel=ctx.message.channel, content='bid', check=biddable)
            if ans is None:
                await bot.say('No one has joined the bidding so it will stop due to a lack of participants.')
                return
            char2 = Character(ans.author)
            turn = True
            def intable(msg):
                try:
                    int(msg.content)
                    return True
                except (ValueError, TypeError):
                    return False

            await bot.say('The bidding will start! If no one bids for 15secs the winner will be declared.')
            ans = bot.wait_for_message(15, author=p, channel=ctx.message.channel, check=intable)
            p = ans.author
            while True:
                if turn:
                    p = await bot.get_user_info(char.id)
                else:
                    p = await bot.get_user_info(char2.id)
                ans = bot.wait_for_message(15, author=p, channel=ctx.message.channel, check=intable)




    @bot.command()
    async def role(person, *args):
        """Gives the person a role to be displayed next to their name"""
        person = person.capitalize()
        name = " ".join(args).capitalize()
        if msg.author.id == '235810944981139456':
            cursor.execute("UPDATE characters SET role = ? WHERE name = ?", (name, person))
            db.commit()
            await bot.say('The person {} has now been dubbed <{}>'.format(person, name))
        else:
            await bot.say('You do not have permission to give people roles.')

    @bot.command()
    async def leaderboard():
        """Gets all characters leaderboard"""
        details = cursor.execute('SELECT name, level, exp FROM characters ORDER BY level DESC, exp DESC, name ASC, ID, achievements, gold').fetchall()
        embed = Embed(
            title='Leader Board',
            colour=Colour.lighter_grey()
        )
        for name, level, exp in details:
            embed.add_field(name=name, value="Level:{}, exp:{}/{}".format(level, exp, int(1000 * 1.5 ** (level - 1))), inline=False)

        await bot.say(embed=embed)


if __name__ == '__main__':
    bot.run('NDQ4OTA4NjYxNjQxNzA3NTUw.DedAYg.E7rKIVT8dn5ufjuDBHVtxIMTR5g')
