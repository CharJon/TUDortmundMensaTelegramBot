import peewee as p

sqlite_db = p.SqliteDatabase('chats.db', pragmas={'journal_mode': 'wal'})


class BaseModel(p.Model):
    class Meta:
        database = sqlite_db


class DailyUpdates(BaseModel):
    chat_id = p.TextField()
    time = p.TimeField()
    mensa = p.TextField()


class ChatManager:

    def __init__(self):
        self.daily_updates = DailyUpdates(sqlite_db)
        sqlite_db.connect()
        sqlite_db.create_tables([DailyUpdates])
        sqlite_db.close()

    def get_update_chats(self):
        sqlite_db.connect()
        result = [(update.chat_id, update.time, update.mensa) for update in DailyUpdates.select()]
        sqlite_db.close()
        return result

    def add_update(self, chat_id, time, mensa):
        sqlite_db.connect()
        DailyUpdates.create(chat_id=chat_id, time=time, mensa=mensa)
        sqlite_db.close()


chat_manager = ChatManager()
