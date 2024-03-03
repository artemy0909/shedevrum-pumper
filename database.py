import datetime

from peewee import *

db = SqliteDatabase("database.sqlite")


def select_all(tab_name) -> list:
    return db.execute_sql(f'SELECT * FROM {tab_name}').fetchall()


class Fish(Model):
    href = CharField()
    dead_href = BooleanField(default=False)
    subscribes = IntegerField()
    followers = IntegerField()
    likes = IntegerField()
    update_datetime = DateTimeField(default=datetime.datetime.now)
    hooked = DateTimeField()

    class Meta:
        database = db


class Bubble(Model):
    fish = ForeignKeyField(Fish)
    update_datetime = DateTimeField(default=datetime.datetime.now)
    hooked = DateTimeField()

    class Meta:
        database = db
