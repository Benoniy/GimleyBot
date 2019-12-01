'''
Database setup for Dominatrix Bot (bot2.py)
This file should be run when the bot is first installed onto a system.
'''

import sqlite3 as db

def dbBuild():
    # Connect to Database
    connection = db.connect('bot2.db')
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS servers ("
             "guildID INTEGER NOT NULL,"
             "guildName TEXT,"
             "PRIMARY KEY (guildID)"
             ");")
    connection.commit()
    cursor.execute("CREATE TABLE IF NOT EXISTS roles ("
             "roleID INTEGER NOT NULL,"
             "guildID INTEGER NOT NULL,"
             "roleType INTEGER,"
             "roleRegex TEXT,"
             "roleName TEXT,"
             "PRIMARY KEY (roleID, guildID),"
             "FOREIGN KEY (guildID) REFERENCES servers (guildID)"
             "ON DELETE CASCADE ON UPDATE NO ACTION"
             ");")
    connection.commit()
    cursor.execute("CREATE TABLE IF NOT EXISTS users ("
             "userID INTEGER NOT NULL,"
             "guildID INTEGER NOT NULL,"
             "xp INTEGER,"
             "userLevel INTEGER,"
             "PRIMARY KEY (userID, guildID),"
             "FOREIGN KEY (guildID) REFERENCES servers (guildID)"
             "ON DELETE CASCADE ON UPDATE NO ACTION"
             ");")
    cursor.execute("CREATE TABLE IF NOT EXISTS modpacks ("
             "packName TEXT NOT NULL,"
             "game TEXT,"
             "gameLink TEXT,"
             "guildID INTEGER NOT NULL,"
             "packLink TEXT NOT NULL,"
             "PRIMARY KEY (packName, guildID),"
             "FOREIGN KEY (guildID) REFERENCES servers (guildID)"
             " ON DELETE CASCADE ON UPDATE NO ACTION"
             ");")
    connection.commit()

    # Terminate DB connection and return to main bot
    connection.close()
    return

dbBuild()
