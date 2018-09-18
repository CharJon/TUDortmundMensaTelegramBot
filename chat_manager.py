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

    def get_update_chats(self):
        result = [(update.chat_id, update.time, update.mensa) for update in DailyUpdates.select()]
        return result

    def add_update(self, chat_id, time, mensa):
        DailyUpdates.create(chat_id=chat_id, time=time, mensa=mensa)
        sqlite_db.commit()

    def remove_update(self, chat_id):
        for update in DailyUpdates.select().where(DailyUpdates.chat_id == chat_id):
            update.delete_instance()
        sqlite_db.commit()

    def update_already_scheduled(self, chat_id, mensa):
        already_scheduled = DailyUpdates.select().where(DailyUpdates.chat_id == chat_id,
                                                        DailyUpdates.mensa == mensa)
        if already_scheduled:
            return True
        else:
            return False

    def __del__(self):
        sqlite_db.close()


chat_manager = ChatManager()
