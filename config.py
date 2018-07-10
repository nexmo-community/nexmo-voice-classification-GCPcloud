from huey.contrib.sqlitedb import SqliteHuey

huey = SqliteHuey("voice_classifier", filename="huey.db")
