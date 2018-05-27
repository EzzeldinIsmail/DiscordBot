from sqlite3 import *
from sys import argv, stdin, stdout
argv = argv[1:]


def intify(s: str):
    try:
        s = int(s)
        return s
    except (ValueError, TypeError):
        if s.lower() == 'none':
            s = "None"
        return s.capitalize().replace("'", "\'")


with connect('main.db') as db:
    cursor = db.cursor()
    if argv[0] == 'add':
        if argv[1] == 'quest':
            print('Enter values:')
            s = []
            for i in ['name', 'description', 'time', 'exp', 'gold', 'level', 'requirement', 'achievement', 'reputation']:
                n = input('{}: '.format(i.capitalize()))
                s.append(intify(n))
            cursor.execute(
                'INSERT INTO quests(name, description, time, exp, gold, level, requirement, achievement, reputation) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', s)
            db.commit()
        elif argv[1] == 'item':
            print('Enter values:')
            s = []
            for i in ['name', 'description', 'price', 'class', 'requirement']:
                n = input('{}: '.format(i.capitalize()))
                s.append(intify(n))
            cursor.execute('INSERT INTO shop(name, description, price, class, requirement) VALUES (?, ?, ?, ?, ?)', s)
            db.commit()
    if argv[0] == 'display':
        if argv[1] == 'quests':
            data = cursor.execute('SELECT * FROM quests ORDER BY level, name, exp').fetchall()
            data.insert(0, ('name', 'description', 'time', 'exp', 'gold', 'level', 'requirement', 'achievement', 'reputation'))
            for i in data:
                print('{:<30} {:<75} {:<10} {:<10} {:<10} {:<10} {:<20} {:<20} {:<10}'.format(*i))

        elif argv[1] == 'items':
            data = cursor.execute('SELECT * FROM shop ORDER BY price, class, name').fetchall()
            data.insert(0, ('name', 'description', 'price', 'class', 'requirement'))
            for i in data:
                print('{:<30} {:<75} {:<10} {:<20} {:<20}'.format(*i))
