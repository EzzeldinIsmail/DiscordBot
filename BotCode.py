import discord
from discord import Embed, Colour
from discord.ext.commands import Bot
import time
# from re import search
import datetime
from random import randint
import asyncio
from sys import exc_info
from sqlite3 import connect, Cursor
from typing import Union
# TODO document discord api
# TODO gold --> xp converter
# TODO implement error checking
# TODO check gold/min
# TODO add more quests (from quests and items)
# TODO add more weapons
# TODO add more craftables
# TODO ship dlc (upgrade ship and ship battles)
"""
The discord bot 315zizx meant for personal use and not completely modified for multi server use.
This bot implementes most basic bot stuff excpet music (I like my laptop in one piece thank you),
it also has the text based mmorpg currently under development and improvement. All user data is 
stored in a database using sqlite3, and only server related stuff is kept in text filed.
`` = monospace text
``` = indent monospace text
"""

__version__ = '0.9.5'
userid = ''
msg: discord.Message = ''
prefix = open('data.txt', 'r').readlines()[0].strip()
channel = open('data.txt', 'r').readlines()[1].strip()
client = discord.Client()
bot: asyncio = Bot(command_prefix=prefix)
discord.Message: asyncio

def limit(lvl):
    return int(1000*1.5**(lvl-1))

def check(cursor, db: str, field: str, req: Union[str, int]):
    """Used to check if req exists in the database"""
    if type(req) == str:
        cursor.execute('SELECT * FROM {} WHERE {} = "{}"'.format(db, field, req.replace("'", "\'")))  # Query for strings
    else:
        cursor.execute('SELECT * FROM {} WHERE {} = {}'.format(db, field, req))    # Query for numbers
    word = cursor.fetchall()
    return word


@bot.event
async def on_error(event, *args, **kwargs):
    if event == 'quests' and args == []:
        await bot.say('You have to pass the level of the quest that you would like to recieve.')
    else:
        raise exc_info()


@bot.event
async def on_member_join(member):
    roles = discord.utils.get(member.server.roles, name="Wait... You're Online?")    # Gets role
    await bot.add_roles(member, roles)       # Adds role to new member
    await bot.send_message(bot.get_channel(channel), "Welcome to the server <@{}>!".format(member.id)) # Weolcomes new member to server


@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name='PyCharm'))    # Sets status to playing PyCharm
    await bot.send_message(bot.get_channel(channel), "I am online!")


@bot.event                          # Event handler at start of every function
async def on_message(message):              # Async function to handle multiple things at once
    message.content: str            # Gets content of message
    message.author.id: int          # Gets id of sender of message
    global userid
    global msg
    userid = message.author.id
    msg = message
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
            db.commit()
            await bot.process_commands(message)     # Sends message to commands

    elif message.content.lower() == 'omak':
        await bot.send_message(message.channel, ':middle_finger:')


# Bot commands
@bot.command()
async def version():
    await bot.say(__version)


@bot.command()
async def set_prefix(pr):
    with open('data.txt', 'r+') as f:
        lines = f.readlines()
        lines[0] = pr+'\n'
        f.seek(0, 0)
        f.truncate()
        f.writelines(lines)


@bot.command(pass_context=True)
async def set_channel(ctx):
    """Sets the channel for the bot to talk in"""
    message = ctx.message
    with open('data.txt', 'r+') as f:
        lines = f.readlines()
        lines[0] = "{}\n".format(message.channel.id)
        f.seek(0, 0)
        f.truncate()
        f.writelines(lines)


@bot.command()
async def say(*args):
    """Makes bot say whatever is passed to it"""
    await bot.say(' '.join(args))


@bot.command(pass_context=True)     # Pass context data which contains everything
async def created(ctx):
    """Finds when user account was created"""
    message = ctx.message
    await bot.say('Your account was created at: {}'.format(message.author.created_at.strftime('%H:%M:%S, %d %a %b %y')))    # Finds when user was created and
    #  time formatting


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
    n = int(ctx.message.content.split(' ')[1]) + 1
    await bot.purge_from(ctx.message.channel, check= lambda x: True, limit=n)


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
    message = ' '.join(ctx.message.content.split(' ')[1:])
    server = ctx.message.server
    for channel in server.channels:
        if channel.name == 'pings':
            await bot.send_message(channel, message)
            break
    else:
        await bot.say('I did not find a pings channel to send the message to.')


with connect('main.db') as db:
    """Everything below here has to do with the mmorpg"""
    cursor = db.cursor()

    @bot.command(pass_context=True, aliases=['char'])
    async def character(ctx):
        """Checks if the user has a character and creates one if they don't"""
        user = ctx.message.author
        image = ctx.message.author.avatar_url
        word = check(cursor, 'characters', 'ID', userid)
        if word == []:  # Checks if the user has a character
            await bot.say('You do not have a character made please make a character by using the command make_character {name} {class}.')
        else:
            if check(cursor, 'logs', 'ID', userid) == []:
                quest = 'Currently no pending quests'
            else:
                quest = cursor.execute('SELECT name FROM logs WHERE ID = {}'.format(userid)).fetchall()[0][0]
            name, classs, exp, gold, level, achievements, role, reputation = cursor.execute('SELECT name, class, exp, gold, level, achievements, role, '
                                                                                'reputation FROM characters WHERE ID ={}'.format(userid)).fetchall()[0]
            # sql query returns array of tuples so access the first tuple and unpack
            colour = 'FFFFFF'                                   # Decides user colour depending on level
            if level < 10: colour = int('0xFF0000', 16)
            elif level < 20: colour = int('0xFF7F00', 16)
            elif level < 30: colour = int('0xFFFF00', 16)
            elif level < 40: colour = int('0x00FF00', 16)
            elif level < 50: colour = int('0x0000FF', 16)
            elif level < 60: colour = int('0x4B0082', 16)
            elif level < 70: colour = int('0x9400D3', 16)

            embed = Embed(              # Creates the character profile embed
                title='Character details:',
                colour=colour,
            )
            embed.set_footer(text='At {}'.format(datetime.datetime.utcnow().strftime('%H:%M:%S, %d %a %b %y')))
            if role == 'None':
                embed.set_author(name='{}'.format(user.name), icon_url=image)
            else:
                embed.set_author(name='{} <{}>'.format(user.name, role), icon_url=image)
            embed.add_field(name='Name', value=name)
            for i in achievements.split(', '):
                embed.add_field(name='Achievement', value=i)
            embed.add_field(name='Class', value=classs)
            embed.add_field(name='Exp', value='{}/{}'.format(exp, limit(level)))
            embed.add_field(name='Gold', value="{}G".format(gold))
            embed.add_field(name='Level', value=level)
            embed.add_field(name='Reputation', value=reputation)
            embed.add_field(name='Current quest', value=quest)

            await bot.say(embed=embed)

    @bot.command(aliases=['ins'])
    async def inspect(*args):
        """Displays other users' characters"""
        name = ' '.join(args).capitalize().replace("'", "\'")
        l = check(cursor, 'characters', 'name', name)
        if l == []:         # Checks if the character exists
            await bot.say('{} does not exist.'.format(name))
        else:
            id = cursor.execute('SELECT ID FROM characters WHERE name = ?', (name,)).fetchall()[0][0]
            if check(cursor, 'logs', 'ID', id) == []:           # Checks for pending wuests to display
                quest = 'Currently no pending quests'
            else:
                quest = cursor.execute('SELECT name FROM logs WHERE ID = {}'.format(id)).fetchall()[0][0]
            name, classs, exp, gold, level, achievements, role, reputation = cursor.execute('SELECT name, class, exp, gold, level, achievements, role, '
                                                                                'reputation FROM characters WHERE name=?', (name,)).fetchall()[0]
            user =  await bot.get_user_info(id)
            user = user.name

            colour = 'FFFFFF'
            if level < 10: colour = int('0xFF0000', 16)
            elif level < 20: colour = int('0xFF7F00', 16)
            elif level < 30: colour = int('0xFFFF00', 16)
            elif level < 40: colour = int('0x00FF00', 16)
            elif level < 50: colour = int('0x0000FF', 16)
            elif level < 60: colour = int('0x4B0082', 16)
            elif level < 70: colour = int('0x9400D3', 16)

            embed = Embed(              # Creates the character profile embed
                title='Character details:',
                colour=colour,
            )
            embed.set_footer(text='At {}'.format(datetime.datetime.utcnow().strftime('%H:%M:%S, %d %a %b %y')))  # Gets and formats current date&time
            if role == 'None':
                embed.set_author(name='{}'.format(user))
            else:
                embed.set_author(name='{} <{}>'.format(user, role))
            embed.add_field(name='Name', value=name)
            for i in achievements.split(', '):
                embed.add_field(name='Achievement', value=i)
            embed.add_field(name='Class', value=classs)
            embed.add_field(name='Exp', value='{}/{}'.format(exp, limit(level)))
            embed.add_field(name='Gold', value="{}G".format(gold))
            embed.add_field(name='Level', value=level)
            embed.add_field(name='Reputation', value=reputation)
            embed.add_field(name='Current quest', value=quest)

            await bot.say(embed=embed)

    @bot.command(pass_context=True, aliases=['character_make', 'make_character'])
    async def create(ctx):
        """Creates a character if the user doesn't already have one"""
        try:
            name = ' '.join(ctx.message.content.split(' ')[1:-1]) # Gets name
            classs = ctx.message.content.split(' ')[-1] # Get class
        except IndexError:      # Preparation for errors
            name = None
            classs = None
        if name is None or classs is None:      # Checks for wrong entry
            await bot.say('You have to enter a name and a class for the character eg:\n ```make_character Viktor Warrior```')
        elif classs.lower() != 'rogue' and classs.lower() != 'warrior' and classs.lower() != 'wizard': # Cheks for wrong class entry
            await bot.say('You can only choose one of the three classes: warrior, wizard or rogue')
        elif ctx.message.author.bot:            # Checks for botting
            await bot.say('Bots cannot make characters')
        elif check(cursor, 'characters', 'ID', userid) == []:  # Checks if the user already has a character
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
        else:
            await bot.say('You already have a character.')


    @bot.command(aliases=['inv', 'bag'])
    async def inventory():
        """Displays the user's items"""
        if check(cursor, 'characters', 'ID', userid) == []:
            await bot.say('You do not have a character made please make a character by using the command make_character {name} {class}.')
        else:
            extra, name = cursor.execute('SELECT extra, name FROM characters WHERE ID = {}'.format(userid)).fetchall()[0]
            embed = Embed(  # Creates the inventory embed
                title='Character inventory:',
                colour=Colour.orange(),
                description='{} items'.format(len(extra.split(', ')))
            )
            embed.set_author(name=name)
            embed.set_footer(text='At {}'.format(datetime.datetime.utcnow().strftime('%H:%M:%S, %d %a %b %y')))
            for i in extra.split(', '):
                embed.add_field(name='Item', value=i)

            await bot.say(embed=embed)

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
        lines = check(cursor, 'quests', 'name', name)
        if lines == []:  # If the quest exists
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

    @bot.command(aliases=['log_quest'])
    async def start(*args):
        """Starts quest for user"""
        name = ' '.join(args).capitalize().replace("'", "\'")
        lines = check(cursor, 'quests', 'name', name)
        if lines == []:  # Checks if quest exists
            await bot.say('Quest {} was not found.'.format(name))
        else:
            qr = cursor.execute('SELECT requirement FROM quests WHERE name = "{}"'.format(name)).fetchall()[0][0]
            cr = cursor.execute("SELECT extra FROM characters WHERE ID = {}".format(userid)).fetchall()[0][0].split(', ')

            if check(cursor, 'logs', 'ID', userid) != []:  # Checks for already pending quests
                await bot.say('You already have a quest pending.')
                return
            elif qr.lower() not in [x.lower() for x in cr] and qr.lower() != 'none':     # Checks if user has requirement for quest
                await bot.say('You do not have the requirements to do this.')
                return

            failure = 20
            cursor.execute('SELECT level, achievement FROM quests WHERE name = "{}"'.format(name))
            ql, achv = cursor.fetchall()[0] # Gets quest level
            cursor.execute("SELECT level FROM characters WHERE ID = '{}'".format(userid))
            cl = cursor.fetchall()[0][0]  # Gets character level
            if ql == 0:
                failure = 0
            elif achv != 'None' and ql > 30:
                failure = 40
            elif ql > cl:  # Changes failure rate
                failure += int((ql-cl) * 8.67)
            elif cl > ql:
                failure -= int((cl-ql) * 5)
            failure = min(max(failure, 0), 100)
            tim, exp, gold =  cursor.execute('SELECT time, exp, gold FROM quests WHERE name = "{}"'.format(name)).fetchall()[0]  # Gets quest info
            cursor.execute('INSERT INTO logs(ID, time, duration, exp, gold, name, failure) VALUES (?, ?, ?, ?, ?, ?, ?)',
                           (userid, int(time.time()), tim, exp, gold, name, failure))  # Logs quest info
            db.commit()             # commits changes
            if tim < 60:
                await bot.say('Your character has started adventuring on quest {} for {}mins, {} exp and {}G, wish them luck!' .format(name, tim, exp, gold))
                # prints quest confirmation
            else:
                await bot.say('Your character has started adventuring on quest {} for {}h and {}mins, {} exp and {}G, wish them luck!'
                              .format(name, (tim//60), (tim % 60), exp, gold))

    @bot.command(pass_context=True)
    async def abandon(ctx):
        """Abandons current quest"""
        id = ctx.message.author.id
        if check(cursor, 'characters', 'ID', id) == []:
            await bot.say('You do not have a character.')
            return
        elif check(cursor, 'logs', 'ID', id) == []:
            await bot.say('You currently have no pending quests to give up.')
            return
        name = cursor.execute('SELECT name FROM logs WHERE ID = ?', (id,)).fetchall()[0][0]
        cursor.execute('DELETE FROM logs WHERE ID = ?', (id,))
        db.commit()
        await bot.say('{} quest abandoned'.format(name))

    @bot.command(pass_context=True, aliases=['collect_quest', 'finish'])
    async def collect(ctx):
        """Collects already started quest"""
        userid = ctx.message.author.id
        cursor.execute('SELECT time, duration, exp, gold, name, failure FROM logs WHERE ID = ?', (userid,))
        lines = cursor.fetchall()
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

            cursor.execute('SELECT exp, gold, level, achievements, reputation, extra FROM characters WHERE ID = {}'.format(userid))
            uexp, ugold, level, achievements, urep, extra = cursor.fetchall()[0]
            exp += uexp  # Updates values
            gold += ugold
            urep += qrep
            if exp > limit(level):  # Checks if the user has leveled up
                exp = exp % limit(level)  # Calculates leftover xp
                level += 1
                await bot.say('Congratulations you have reached level {}'.format(level))  # Prints level up message

            if achievement == 'None':
                pass
            elif achievement in achievements.split(', '):
                pass
            else:
                await bot.say('Congratulations! You have gotten the achievement {}.'.format(achievement))
                if achievements == 'None':  # Leaves no beginning None
                    achievements = achievement.capitalize()
                else:
                    achievements += ', {}'.format(achievement)

            if item == 'None':
                pass
            elif item in extra.split(', '):
                pass
            else:
                if randint(0, 99) < 20:
                    await bot.say('Congratulations! You have found the item {}.'.format(item))
                    if extra == 'None':
                        extra = item
                    else:
                        extra += ', {}'.format(item)


            cursor.execute('UPDATE characters SET exp=?, gold=?, level =?, achievements=?, reputation=?, extra=? WHERE ID = ?', (exp, gold, level, achievements,
                                                                                                                        urep, extra, userid))
            # Updates character stats
            db.commit()
            await bot.say('"{}" quest collected.'.format(name))
            cursor.execute('DELETE FROM logs WHERE ID = {}'.format(userid))  # Deletes quest from logs
            db.commit()

    @bot.command(aliases=['store'])
    async def shop():
        """Displays all the shop items"""
        lines = cursor.execute('SELECT name, price FROM shop ORDER BY price, name, description').fetchall()      # Gets all items from shop
        s = 'Details: \n```{:<30}    {:<6}```\n'.format('Items', 'Price')
        for n, p in lines:
            s += '```{:<30}    {:<6}```'.format(n, p)          # Adds items with indent monospace style
        await bot.say(s)

    @bot.command()
    async def identify(*args):
        """Displays all informations about supplied quest"""
        name = ' '.join(args).capitalize()
        if check(cursor, 'shop', 'name', name) == []:             # Checks if the item exists
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


    @bot.command()
    async def buy(*args):
        """Buys item for user's character"""
        name = ' '.join(args).capitalize().replace("'", "\\'")
        lines = check(cursor, 'characters', 'ID', userid)
        i = check(cursor, 'shop', 'name', name)
        if lines == []:             # Checks if the user has a character
            await bot.say('You need to make a character first before you can access the shop, use the command make_character {name} {class}.')
        elif i == []:               # Checks if the item exists
            await bot.say('This item does not exist')
        else:
            ug, ue, uc = cursor.execute('SELECT gold, extra, class FROM characters WHERE ID = {}'.format(userid)).fetchall()[0]
            desc, ig, ic, ir  = cursor.execute("SELECT description, price, class, requirement FROM shop WHERE name ='{}'".format(name)).fetchall()[0]
            if ig > ug:  # Checks if the user has enough money to buy the item
                await bot.say('You do not have enough money to buy this item.')
            elif ue != 'None' and name in ue.split(', '):           # Checks if user already has item
                await bot.say('You already have this item.')
            elif ic != 'None' and ic != uc:                         # Checks if the item is not class specific
                await bot.say('This is item is locked off only for the {} class.'.format(ic))
            elif ir != 'None' and ir not in ue.split(', '):         # Checks if the user does not already have the item
                await bot.say('This item requires you to have {} before you buy it.'.format(ir))
            else:
                ug -= ig
                if ue == 'None': ue = name
                else: ue += ', {}'.format(name)         # Updates users items
                cursor.execute("UPDATE characters SET gold ={}, extra= '{}' WHERE ID = {}".format(ug, ue, userid))
                db.commit()
                await bot.say('Congratulations!:tada: You bought {}:{} for {}G and now you have {}G left'.format(name, desc, ig, ug))


    @bot.command()
    async def leaderboard():
        """Gets all characters leaderboard"""
        details = cursor.execute('SELECT name, level, exp FROM characters ORDER BY level DESC, exp DESC, name ASC, ID, achievements, gold').fetchall()
        embed = Embed(
            title='Leader Board',
            colour=Colour.lighter_grey()
        )
        for name, level, exp in details:
            embed.add_field(name=name, value="Level:{}, exp:{}/{}".format(level, exp, limit(level)), inline=False)

        await bot.say(embed=embed)


    @bot.command()
    async def role(person, *args):
        """Gives the person a role to be displayed next to their name"""
        person = person.capitalize()
        name = " ".join(args).capitalize()
        if msg.author.id == 235810944981139456:
            cursor.execute('UPDATE characters SET role = ? WHERE name = ?', (name, person))
            db.commit()
            await bot.say('The person {} has now been dubbed <{}>'.format(person, name))
        else:
            await bot.say('You do not have permission to give people roles.')


    @bot.command(pass_context=True, aliases=['battle', 'attack'])
    async def pvp(ctx):
        """Starts a pvp battle between the user and the person mentioned"""
        message = ctx.message
        user = ctx.message.author
        if not  0 < len(message.mentions) < 2:          # Checks that the battle is only between two users
            await bot.say('Wrong amount of mentions.')
        else:
            mention = message.mentions[0]
            uc, un, ul, ue = cursor.execute('SELECT class, name, level, extra FROM characters WHERE ID = ?', (user.id,)).fetchall()[0]
            mc, mn, ml, me = cursor.execute('SELECT class, name, level, extra FROM characters WHERE ID = ?', (mention.id,)).fetchall()[0]
            ue = len(ue.split(', '))
            me = len(me.split(', '))
            ud = {'Name': un, 'Class': uc, 'Level':ul, 'Extra':ue}
            md = {'Name': mn, 'Class': mc, 'Level':ml, 'Extra':me}
            for i in [ud, md]:
                # Creates user stats
                """ At lvl 20, 20 items
                        Armour  Damage  Dodge
                Warrior 3.63M   732K    26
                Wizard  3.32M   831K    39
                Rogue   3.02M   665K    66
                """
                if i['Class'] == 'Warrior':
                    i['Armour'] = int(300 * (1.6**i['Level']))
                    i['Health'] = int(300 * (1.6**i['Level']))
                    i['Damage'] = int((110 * i['Extra']) * (1.5**i['Level']))
                    i['Dodge'] = int(15 * (1.05** i['Extra']))
                elif i['Class'] == 'Wizard':
                    i['Armour'] = int(275 * (1.6**i['Level']))
                    i['Health'] = int(275 * (1.6 ** i['Level']))
                    i['Damage'] = int((125 * i['Extra']) * (1.5**i['Level']))
                    i['Dodge'] = int(10 * (1.05** i['Extra']))
                elif i['Class'] == 'Rogue':
                    i['Armour'] = int(250 * (1.6**i['Level']))
                    i['Health'] = int(250 * (1.6 ** i['Level']))
                    i['Damage'] = int((100 * i['Extra']) * (1.5**i['Level']))
                    i['Dodge'] = int(25 * (1.05**i['Extra']))
            text = await bot.say('The battle will begin shortly')
            turn = True
            data = []
            while ud['Armour'] > 0 and md['Armour'] > 0:
                s = '{}: {}/{}hp VS {}: {}/{}hp\n'.format(ud['Name'].upper(), ud['Armour'], ud['Health'], md['Name'].upper(), md['Armour'], md['Health'])
                if turn:
                    if randint(0, 99) < md['Dodge']:
                        data.append('{} has attacked but {} dodged!\n'.format(ud['Name'], md['Name']))
                    else:
                        data.append('{} has delt {} damage!\n'.format(ud['Name'], ud['Damage']))
                        md['Armour'] -= ud['Damage']
                else:
                    if randint(0, 99) < ud['Dodge']:
                        data.append('{} has attacked but {} dodged!\n'.format(md['Name'], ud['Name']))
                    else:
                        data.append('{} has delt {} damage!\n'.format(md['Name'], md['Damage']))
                        ud['Armour'] -= md['Damage']
                if len(data) > 5:
                    s+= ''.join(data[-5:])
                else:
                    s+= ''.join(data)

                await asyncio.sleep(.8)
                turn = not turn         # Flips turn so other user attacks
                await bot.edit_message(text, s)
            if ud['Armour'] <= 0:
                await bot.say('{} has won!'.format(md['Name']))
            elif md['Armour'] <= 0:
                await bot.say('{} has won!'.format(ud['Name']))


    @bot.command(pass_context=True)
    async def stats(ctx):
        """Gets user's calculated stats"""
        user = ctx.message.author.name
        name, classs, level, extra = cursor.execute('SELECT name, class, level, extra FROM characters WHERE ID = ?', (userid,)).fetchall()[0]
        extra = len(extra.split(', '))
        if classs == 'Warrior':
            armour = int(300 * (1.6 ** level))
            damage = int((110 * extra) * (1.5 ** level))
            dodge = int(10 * (1.05 ** extra))
        elif classs == 'Wizard':
            armour = int(275 * (1.6 ** level))
            damage = int((125 * extra)*(1.5 ** level))
            dodge = int(15 * (1.05 ** extra))
        elif classs == 'Rogue':
            armour = int(250 * (1.6 ** level))
            damage = int((100 * extra)*(1.5 ** level))
            dodge = int(20 * (1.05 ** extra))

        embed = Embed(title='Stats', colour=Colour.dark_red())      # Creates user stats' embed
        embed.set_author(name=user)
        embed.add_field(name='Armour', value=armour)
        embed.add_field(name='Damage', value=damage)
        embed.add_field(name='Dodge', value=dodge)
        embed.set_footer(text='At {}'.format(datetime.datetime.utcnow().strftime('%H:%M:%S, %d %a %b %y')))
        await bot.say(embed=embed)


    @bot.command(pass_context=True, aliases=['gamble', 'casino', 'slots'])
    async def gambling(ctx):
        """Attempts to play slots"""
        n = ctx.message.content.split(' ')[1]
        au = ctx.message.author
        try:
            n = int(n)
        except (ValueError, NameError):
            await bot.say('Please enter an integer value.')
            return
        ug, rep = cursor.execute('SELECT gold, reputation FROM characters WHERE ID = ?', (au.id,)).fetchall()[0]
        if check(cursor, 'characters', 'ID', au.id) == []:
            await bot.say('Please make a character first to gamble.')
            return
        elif n > ug:
            await bot.say('You do not have this much money to gamble with, stop trying to take loans!')
            return
        txt = await bot.say('Pulling lever... :slot_machine:')
        ug -= n
        mult = (n/10000)+ 1
        if randint(0, 99) < randint(min(max((rep/5), 0), 49), 50):
            ug += int(n * mult)
            await bot.edit_message(txt,'Congratulations! Your {}G have become {}G and now you have {}G in total!'.format(n, int(n*mult), ug))

        else:
            await bot.edit_message(txt, "I'm sorry, better luck next time!")

        cursor.execute('UPDATE characters SET gold = ? WHERE ID  = ?', (ug, au.id))
        db.commit()


    @bot.command()
    async def craft(item):
        """Attempts to craft an item"""
        item = item.capitalize()
        if check(cursor, 'characters', 'ID', userid) == []:
            await bot.say('You need to create a character first to craft items.')
            return
        elif check(cursor, 'craft', 'name', item) == []:
            await bot.say('This item does not exist.')
            return
        else:
            name, desc, classs, level, req = cursor.execute('SELECT name, description, class, level, requirements FROM craft WHERE name = ?', (item,)).fetchall()[0]
            uc, ul, ue = cursor.execute('SELECT class, level, extra FROM characters WHERE ID =?', (userid,)).fetchall()[0]
            if uc != classs:
                await bot.say('You cannot craft this item as it is locked for the {} class'.format(classs))
                return
            elif level > ul:
                await bot.say('Your level is not high enough to craft this items.')
                return
            else:
                for i in req.split(', '):
                    if i not in ue.split(', '):
                        await bot.say('You do not have all the items needed to craft this {}'.format(item))
                        return

        ue = ue.split(', ')
        for i in req.split(', '):
            ue = ue.remove(i)
        ue.append(item)
        ue = ', '.join(ue)
        cursor.execute('UPDATE characters SET extra =? WHERE ID =?', (ue, userid))
        db.commit()

    @bot.command(aliases=['craft_list'])
    async def schemes():
        lines = cursor.execute('SELECT name, requirements FROM craft ORDER BY name').fetchall()  # Gets all items from shop
        s = 'Details: \n```{:<30}    {:<30}```\n'.format('Item', 'Requirements')
        for n, p in lines:
            s += '```{:<30}    {:<30}```'.format(n, p)  # Adds items with indent monospace style
        await bot.say(s)

    @bot.command(pass_context=True)
    async def plan(ctx):
        item = ' '.join(ctx.message.content.split(' ')[1:]).capitalize()
        if check(cursor, 'craft', 'name', item) == []:             # Checks if the item exists
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
        if check(cursor, 'lore', 'name', s) == []:
            await bot.say('The archive has no information about this, please tell us more...')
            return

        name, desc, lvl, req, ach, rep = cursor.execute('SELECT name, description, level, requirements, achievement, reputation FROM lore WHERE name =?',(s,)).fetchall()[0]
        ul, ue, ua, ur = cursor.execute('SELECT level, extra, achievements, reputation FROM characters WHERE ID=?', (userid,)).fetchall()[0]
        if lvl > ul:
            await bot.say('You need to be at least level {} to access this information. Come back when you\'ve grown up.')
            return
        elif req != 'None':
            if req not in ue.split(', '):
                await bot.say('You need {} to access this data. I would suggest you go get it.')
                return
        elif ach != 'None':
                if ach not in ua.split(', '):
                    await bot.say('You do need to earn the achievement {} before you can access this data. Chop! Chop! Get to work!'.format(ach))
                    return
        elif rep != 0:
            if rep < 0:
                if ur > rep:
                    await bot.say('You need to reach {} rep to get this data. Wanna join the dark side?'.format(rep))
                    return
            else:
                await bot.say('You need to reach {} rep to get to this data. Have you considered joining a charity?'.format(rep))
                return

        embed = Embed(title=name, description=desc, colour=int('0xF0FFFF', 16))

        await bot.say(embed=embed)


if __name__ == '__main__':
    bot.run('NDQ4OTA4NjYxNjQxNzA3NTUw.DedAYg.E7rKIVT8dn5ufjuDBHVtxIMTR5g')
