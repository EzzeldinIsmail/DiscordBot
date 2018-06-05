# Made by Ezzeldin Ismail
"""
This is the library for my discord bot 315zizx and
its currently in design mmorpg game.
"""
from sqlite3 import connect
from typing import Union
from discord import User


def check(cursor, db: str, field: str, req: Union[str, int]):
    """Used to check if req exists in the database"""
    if type(req) == str:
        cursor.execute('SELECT * FROM {} WHERE {} = "{}"'.format(db, field, req.replace("'", "\'")))  # Query for strings
    else:
        cursor.execute('SELECT * FROM {} WHERE {} = {}'.format(db, field, req))    # Query for numbers
    return cursor.fetchall() == []


class Character:
    def __init__(self, author: Union[User]):
        """"""
        db = connect('main.db')
        cursor = db.cursor()

        self.id = author.id
        self.username = author.name
        self.avatar = author.avatar_url

        if not check(cursor, 'characters', 'ID', self.id):
            self.char = True
            self.charname, self.classs, self.exp, self.gold, self.lvl, self.extra, self.ach, self.role, self.rep = \
                cursor.execute('SELECT name, class, exp, gold, level, extra, achievements, role, reputation FROM characters WHERE ID = ?',
                               (self.id,)).fetchall()[0]

            try:
                self.curquest = cursor.execute('SELECT name FROM logs WHERE ID = {}'.format(self.id)).fetchall()[0][0]
            except IndexError:
                self.curquest = 'Currently no pending quests'

            self.lextra = len(self.extra.split(', '))
            self.limit = int(1000*1.5**(self.lvl-1))

            self.colour = 'FFFFFF'
            if self.lvl < 10: self.colour = int('0xFF0000', 16)
            elif self.lvl < 20: self.colour = int('0xFF7F00', 16)
            elif self.lvl < 30: self.colour = int('0xFFFF00', 16)
            elif self.lvl < 40: self.colour = int('0x00FF00', 16)
            elif self.lvl < 50: self.colour = int('0x0000FF', 16)
            elif self.lvl < 60: self.colour = int('0x4B0082', 16)
            elif self.lvl < 70: self.colour = int('0x9400D3', 16)

            """ At lvl 20, 20 items
                    Armour  Damage  Dodge
            Warrior 3.63M   732K    26
            Wizard  3.32M   831K    39
            Rogue   3.02M   665K    66
            """
            if self.classs == 'Warrior':
                self.armour = int(300 * (1.6 ** self.lvl))
                self.damage = int((110 * self.lextra) * (1.5 ** self.lvl))
                self.health = int((110 * self.lextra) * (1.5 ** self.lvl))
                self.dodge = int(10 * (1.05 ** self.lextra))
            elif self.classs == 'Wizard':
                self.armour = int(275 * (1.6 ** self.lvl))
                self.damage = int((125 * self.lextra) * (1.5 ** self.lvl))
                self.health = int((125 * self.lextra) * (1.5 ** self.lvl))
                self.dodge = int(15 * (1.05 ** self.lextra))
            elif self.classs == 'Rogue':
                self.armour = int(250 * (1.6 ** self.lvl))
                self.damage = int((100 * self.lextra) * (1.5 ** self.lvl))
                self.health = int((100 * self.lextra) * (1.5 ** self.lvl))
                self.dodge = int(20 * (1.05 ** self.lextra))
        else:
            self.char = False
