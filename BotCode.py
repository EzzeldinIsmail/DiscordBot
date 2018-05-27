import discord
from discord.ext.commands import Bot
# import time
# from re import search
from random import choices
import asyncio
from sys import exc_info
from sqlite3 import *
from typing import Union
# TODO document discord api
# TODO risk of failure for special quests, and items to alter
# TODO quests done, quests failed

userid = ''
msg: discord.Message = ''
prefix = open('data.txt', 'r').readlines()[0].strip()
channel = open('data.txt', 'r').readlines()[1].strip()
client = discord.Client()
bot: asyncio = Bot(command_prefix=prefix)
discord.Message: asyncio


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
async def off():
    """Changes bot's status to off (takes a while)"""
    await bot.change_presence(status=discord.Status.offline)


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


@bot.command()
async def bots(*args):
    n = int(args[-1])
    for _ in range(n):
        await bot.say(' '.join(args))
        await asyncio.sleep(5)
    await bot_purge(n*2)


async def bot_purge(n):
    await bot.purge_from(msg.channel, check=lambda x: True, limit=n)


@bot.command(pass_context=True)
async def purge(ctx):
    n = int(ctx.message.content.split(' ')[1]) + 1
    await bot.purge_from(ctx.message.channel, check= lambda x: True, limit=n)


@bot.command()
async def shutdown():
    await bot.change_presence(status=discord.Status.offline)
    await asyncio.sleep(10)
    exit(5)


with connect('main.db') as db:
    """Everything below here has to do with the mmorpg"""
    cursor = db.cursor()

    @bot.command(pass_context=True)
    async def character(ctx):
        """Checks if the user has a character and creates one if they don't"""
        user = ctx.message.author.name
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
            # sql query returns array of tuples so access the first typle after the first item cause of ID
            colour = 'FFFFFF'
            if level < 10: colour = int('0xFF0000', 16)
            elif level < 20: colour = int('0xFF7F00', 16)
            elif level < 30: colour = int('0xFFFF00', 16)
            elif level < 40: colour = int('0x00FF00', 16)
            elif level < 50: colour = int('0x0000FF', 16)
            elif level < 60: colour = int('0x4B0082', 16)
            elif level < 70: colour = int('0x9400D3', 16)

            embed = discord.Embed(              # Creates the character profile embed
                title='Character details:',
                colour=colour,
            )
            embed.set_footer(text='At {}'.format(datetime.datetime.utcnow().strftime('%H:%M:%S, %d %a %b %y')))
            if role == 'None':
                embed.set_author(name='{}'.format(user))
            else:
                embed.set_author(name='{} <{}>'.format(user, role))
            embed.add_field(name='Name', value=name)
            for i in achievements.split(', '):
                embed.add_field(name='Achievement', value=i)
            embed.add_field(name='Class', value=classs)
            embed.add_field(name='Exp', value='{}/{}'.format(exp, int(1000 * 1.2 ** (level+1))))
            embed.add_field(name='Gold', value="{}G".format(gold))
            embed.add_field(name='Level', value=level)
            embed.add_field(name='Reputation', value=reputation)
            embed.add_field(name='Current quest', value=quest)

            await bot.say(embed=embed)

    @bot.command()
    async def inspect(*args):
        name = ' '.join(args).capitalize()
        l = check(cursor, 'characters', 'name', name)
        if l == []:
            await bot.say('{} does not exist.'.format(name))
        else:
            id = cursor.execute('SELECT ID FROM characters WHERE name = ?', (name,)).fetchall()[0][0]
            if check(cursor, 'logs', 'ID', id) == []:
                quest = 'Currently no pending quests'
            else:
                quest = cursor.execute('SELECT name FROM logs WHERE ID = {}'.format(id)).fetchall()[0][0]
            name, classs, exp, gold, level, achievements, role, reputation = cursor.execute('SELECT name, class, exp, gold, level, achievements, role, '
                                                                                'reputation FROM characters WHERE name=?', (name,)).fetchall()[0]
            user =  await bot.get_user_info(id)
            user = user.name

            # sql query returns array of tuples so access the first typle after the first item cause of ID
            colour = 'FFFFFF'
            if level < 10: colour = int('0xFF0000', 16)
            elif level < 20: colour = int('0xFF7F00', 16)
            elif level < 30: colour = int('0xFFFF00', 16)
            elif level < 40: colour = int('0x00FF00', 16)
            elif level < 50: colour = int('0x0000FF', 16)
            elif level < 60: colour = int('0x4B0082', 16)
            elif level < 70: colour = int('0x9400D3', 16)

            embed = discord.Embed(              # Creates the character profile embed
                title='Character details:',
                colour=colour,
            )
            embed.set_footer(text='At {}'.format(datetime.datetime.utcnow().strftime('%H:%M:%S, %d %a %b %y')))
            if role == 'None':
                embed.set_author(name='{}'.format(user))
            else:
                embed.set_author(name='{} <{}>'.format(user, role))
            embed.add_field(name='Name', value=name)
            for i in achievements.split(', '):
                embed.add_field(name='Achievement', value=i)
            embed.add_field(name='Class', value=classs)
            embed.add_field(name='Exp', value='{}/{}'.format(exp, int(1000 * 1.2 ** (level+1))))
            embed.add_field(name='Gold', value="{}G".format(gold))
            embed.add_field(name='Level', value=level)
            embed.add_field(name='Reputation', value=reputation)
            embed.add_field(name='Current quest', value=quest)

            await bot.say(embed=embed)

    @bot.command(pass_context=True)
    async def create(ctx):
        """Creates a character if the user doesn't already have one"""
        try:
            name, classs = ctx.message.content.split(' ')[1:]
        except IndexError:
            name = None
            classs = None
        s = check(cursor, 'characters', 'ID', userid)
        if name is None or classs is None:
            await bot.say('You have to enter a name and a class for the character eg:\n ```make_character Viktor Warrior```')
        elif classs.lower() != 'rogue' and classs.lower() != 'warrior' and classs.lower() != 'wizard':
            await bot.say('You can only choose one of the three classes: warrior, wizard or rogue')
        elif ctx.message.author.bot:
            await bot.say('Bots cannot make characters')
        elif s == []:  # Checks if the user already has a character
            extra = 'None'
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


    @bot.command()
    async def inventory():
        word = check(cursor, 'characters', 'ID', userid)
        if word == []:  # Checks if the user has a character
            await bot.say('You do not have a character made please make a character by using the command make_character {name} {class}.')
        else:
            extra, name = cursor.execute('SELECT extra, name FROM characters WHERE ID = {}'.format(userid)).fetchall()[0]
            embed = discord.Embed(  # Creates the character profile embed
                title='Character inventory:',
                colour=discord.Colour.orange(),
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
            cursor.execute('SELECT name FROM quests WHERE level = {} ORDER BY level, requirement, time, name, exp, gold, description'.format(n))
            lines = cursor.fetchall()
            s = 'Details: \nQuest names:\n'
            s += ('``Level {} quests``\n'.format(n))
            for name in lines:
                s += '```{}```'.format(*name)  # Adding the quests with indent style
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
            desc, time, exp, gold, level, requirement, achievement, reputation = lines[1:]
            embed = discord.Embed(              # Creates quest embed
                title=name,
                description=desc,
                colour=discord.Colour.red()
            )
            embed.add_field(name='Time', value='{}min'.format(time))
            embed.add_field(name='Exp', value=exp)
            embed.add_field(name='Gold', value='{}G'.format(gold))
            embed.add_field(name='Achievement', value=achievement)
            embed.add_field(name='Reputation', value=reputation)
            if requirement.find(', ') != -1:            # If there is multiple requirements do it a special way
                embed.add_field(name='Level', value=level, inline=False)
                for i in requirement.split(', '):
                    embed.add_field(name='Requirement', value=i, inline=True)
            else:
                embed.add_field(name='Level', value=level)
                embed.add_field(name='Requirement', value=requirement)

            await bot.say(embed=embed)

    @bot.command()
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

            elif qr.lower() not in [x.lower() for x in cr] and qr.lower() != 'none':     # Checks if user has requirement for quest
                await bot.say('You do not have the requirements to do this.')

            else:
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
                    failure -= int((cl-ql) * 10)
                if failure > 100:
                    failure = 100
                elif failure < 0:
                    failure = 0
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
    async def collect(ctx):
        userid = ctx.message.author.id
        """Finishes logged quest"""
        cursor.execute('SELECT time, duration, exp, gold, name, failure FROM logs WHERE ID = ?', (userid,))
        lines = cursor.fetchall()
        if lines == []:  # Checks if there are currenlty any pending quests
            await bot.say('You do not currently have a pending request.')
        else:
            tim, duration, exp, gold, name, failure = lines[0]
            achievement, qrep = cursor.execute('SELECT achievement, reputation FROM quests WHERE name = "{}"'.format(name)).fetchall()[0]
            end = int(tim + (duration * 60))
            if time.time() < end:  # Checks if the quest duraation has finished
                until = (end - time.time())
                await bot.say('Your quest is not done yet there is still {} mins and {} seconds.'
                              .format(int(until / 60), int(until % 60)))
            elif not choices([False, True], weights=[failure, 100]):
                await bot.say('You have failed this quest. Good luck next time!')
            else:
                cursor.execute('SELECT exp, gold, level, achievements, reputation FROM characters WHERE ID = {}'.format(userid))
                uexp, ugold, level, achievements, urep = cursor.fetchall()[0]
                exp += uexp  # Updates values
                gold += ugold
                urep += qrep
                if exp > int(1000 * 1.2 ** (level+1)):  # Checks if the user has leveled up
                    exp = exp % int(1000 * 1.2 ** (level + 1))  # Calculates leftover xp
                    level += 1
                    await bot.say('Congratulations you have reached level {}'.format(level))  # Prints level up message

                if achievement == 'None':
                    pass
                elif achievement in achievements.split(', '):
                    pass
                else:
                    if achievements == 'None':
                        achievements = achievement.capitalize()
                    else:
                        achievements += ', {}'.format(achievement)
                cursor.execute('UPDATE characters SET exp=?, gold=?, level =?, achievements=?, reputation=? WHERE ID = ?', (exp, gold, level, achievements,
                                                                                                                            urep, userid))
                db.commit()
                # Updates character stats
                await bot.say('"{}" quest collected.'.format(name))
            cursor.execute('DELETE FROM logs WHERE ID = {}'.format(userid))  # Deletes quest from logs
            db.commit()

    @bot.command()
    async def shop():
        """Displays all the shop items"""
        lines = cursor.execute('SELECT name FROM shop ORDER BY name, price, description').fetchall()      # Gets all items from shop
        s = 'Details: \nItems:\n'
        for l in lines:
            s += '```{}```'.format(*l)          # Adds items with indent style
        await bot.say(s)

    @bot.command()
    async def identify(*args):
        """Displays all informations about supplied quest"""
        name = ' '.join(args).capitalize()
        c = check(cursor, 'shop', 'name', name)
        if c == []:             # Checks if the item exists
            bot.say("The item you want to insepct does not exist.")
        else:
            desc, price, classs, req = cursor.execute('SELECT description, price, class, requirement FROM shop WHERE name = "{}"'.
                                                      format(name)).fetchall()[0]  # Gets item details

            embed = discord.Embed(          # Creates item embed
                title=name,
                description=desc,
                colour=discord.Colour.green()
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
            elif ic != 'None' and ic != uc:
                await bot.say('This is item is locked off only for the {} class.'.format(ic))
            elif ir != 'None' and ir not in ue.split(', '):
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
        details = cursor.execute('SELECT name, level, exp FROM characters ORDER BY level DESC, exp DESC, name ASC, ID, achievements, gold').fetchall()
        embed = discord.Embed(
            title='Leader Board',
            colour=discord.Colour.lighter_grey()
        )
        for name, level, exp in details:
            embed.add_field(name=name, value="Level:{}, exp:{}/{}".format(level, exp, int(1000 * 1.2 ** level+1)), inline=False)

        await bot.say(embed=embed)

    @bot.command()
    async def role(person, *args):
        person = person.capitalize()
        name = " ".join(args).capitalize()
        global msg
        if msg.author.id == 235810944981139456:
            cursor.execute('UPDATE characters SET role = ? WHERE name = ?', (name, person))
            db.commit()
            await bot.say('The person {} has now been dubbed <{}>'.format(person, name))
        else:
            await bot.say('You do not have permission to give people roles.')


if __name__ == '__main__':
    bot.run('NDQ4OTA4NjYxNjQxNzA3NTUw.DedAYg.E7rKIVT8dn5ufjuDBHVtxIMTR5g')
