# Made by Ezzeldin Ismail
"""
This is the library for my discord bot 315zizx and
its currently in design mmorpg game.
"""
from sqlite3 import connect
from typing import Union
from discord import User
import time

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

        def calcstat(self):
            """ At lvl 20, 20 items
                    Armour  Damage  Dodge
            Warrior 3.63M   732K    26
            Wizard  3.32M   831K    39
            Rogue   3.02M   665K    66
            """
            if self.classs == 'Warrior':
                self.armour = int(300 * (1.6 ** self.lvl))
                self.dmg = int((110 * self.lextra) * (1.5 ** self.lvl))
                self.health = int((110 * self.lextra) * (1.5 ** self.lvl))
                self.dodge = int(10 * (1.05 ** self.lextra))
            elif self.classs == 'Wizard':
                self.armour = int(275 * (1.6 ** self.lvl))
                self.dmg = int((125 * self.lextra) * (1.5 ** self.lvl))
                self.health = int((125 * self.lextra) * (1.5 ** self.lvl))
                self.dodge = int(15 * (1.05 ** self.lextra))
            elif self.classs == 'Rogue':
                self.armour = int(250 * (1.6 ** self.lvl))
                self.dmg = int((100 * self.lextra) * (1.5 ** self.lvl))
                self.health = int((100 * self.lextra) * (1.5 ** self.lvl))
                self.dodge = int(20 * (1.05 ** self.lextra))


        def calcpet(self):
            data = cursor.execute('SELECT name, species, exp, level, happiness FROM pets WHERE ID=?', (self.id,)).fetchall()
            pet = cursor.execute('SELECT pet FROM characters WHERE ID=?', (self.id,)).fetchall()[0][0]
            self.curpet = pet
            if self.curpet != 'None':
                self.pettypes = []
                self.pets={}
                for name, species, exp, level, happiness in data:
                    self.pettypes.append(species)
                    heal, dmg, armour = cursor.execute('SELECT heal, damage, armour FROM zoo WHERE species = ?', (species,)).fetchall()[0]
                    self.pets[species] = {'name': name, 'exp':exp, 'lvl':level, 'happiness':happiness, 'limit':int(100*1.5**(level-1)),
                                          'heal':heal*level, 'dmg':dmg*level, 'armour':armour*level, 'health':armour*level}
                self.pet = self.pets[self.curpet]


        def calcship(self):
            try:
                self.ship, self.shipexp, self.shiplvl, self.crew, self.improve\
                    = cursor.execute('SELECT name, exp, level, crew, improvements FROM ships WHERE ID=?', (self.id,)).fetchall()[0]
                self.shiplimit = int(100*1.5**(self.shiplvl-1))
                self.sailing = cursor.execute('SELECT ID FROM shiplogs WHERE ID=?', (self.id,)).fetchall()
                self.limprove = len(self.improve.split(', ')) if self.improve != 'None' else 0
                if self.sailing:
                    self.sailduration= cursor.execute('SELECT duration FROM shiplogs WHERE ID=?', (self.id,)).fetchall()[0][0] * 60
                    self.docktime = \
                        cursor.execute('SELECT time FROM shiplogs WHERE ID=?', (self.id,)).fetchall()[0][0] + self.sailduration
                self.shiparmour = 10 * self.crew
                self.shiphealth = 10 * self.crew
                self.shipdmg = (20* self.limprove) or 1
                self.shipluck = min(self.shiplvl*5, 100)
            except IndexError:
                self.ship = 'None'

        def calcarena(self):
            try:
                self.strength, self.stage = cursor.execute('SELECT str, stage FROM arenalogs WHERE ID=?', (self.id,)).fetchall()[0]
                self.exit = \
                    cursor.execute('SELECT time FROM arenalogs WHERE ID=?', (self.id,)).fetchall()[0][0] + \
                    (cursor.execute('SELECT duration FROM arenalogs WHERE ID=?', (self.id,)).fetchall()[0][0] * 60)

            except IndexError:
                self.stage = 0


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

            calcstat(self)

            calcpet(self)

            calcship(self)

            calcarena(self)

            try:
                self.sub, self.subexp, self.subdmg = cursor.execute('SELECT subclass, exp, level FROM subclasses WHERE ID=?',(self.id,)).fetchall()[0]
            except IndexError:
                self.sub = 'None'

        else:
            self.char = False

    def stats(self):
        return (self.armour, self.dmg, self.dodge)

    def happiness(self):
        self.pet['happiness'] = min(1000, self.pet['happiness'] + 25)
        for i in self.pettypes:
            self.pets[i]['happiness'] -= 5

    def pet_update(self):
        with connect('main.db') as db:
            cursor = db.cursor()
            for i in self.pettypes:
                cursor.execute('UPDATE pets SET exp=?, level=?, happiness=? WHERE ID=? AND species=?',
                               (self.pets[i]['exp'], self.pets[i]['lvl'], self.pets[i]['happiness'],
                                self.id, i))
        db.commit()

    def char_update(self):
        with connect('main.db') as db:
            cursor = db.cursor()
            cursor.execute('UPDATE characters SET exp=?, gold=?, level=?, extra=?, achievements=?, reputation=?, role=?, pet=? WHERE ID=?',
                           (self.exp, self.gold, self.lvl, self.extra, self.ach, self.rep, self.role, self.curpet, self.id))
            db.commit()

    def ship_update(self):
        with connect('main.db') as db:
            cursor = db.cursor()
            cursor.execute('UPDATE ships SET exp=?, level=?, crew=?, improvements=? WHERE ID=?',
                           (self.shipexp, self.shiplvl, self.crew, self.improve, self.id))
            db.commit()

    def arena_update(self):
        with connect('main.db') as db:
            cursor = db.cursor()
            cursor.execute('UPDATE arenalogs SET time=? duration=?, str=?, stage=? WHERE ID=?',
                           (time.time(), self.stage*15, self.strength, self.stage, self.id,))
            db.commit()