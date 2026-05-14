import motor.motor_asyncio
from config import DB_NAME, DB_URI

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.settings_col = self.db.settings  # welcome message settings ke liye

    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            session = None,
        )
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def update_user_name(self, id, name):
        await self.col.update_one({'id': int(id)}, {'$set': {'name': name}})

    async def set_session(self, id, session):
        await self.col.update_one({'id': int(id)}, {'$set': {'session': session}})

    async def get_session(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user['session']

    # ── Welcome message text DB mein save/get karo ──────────────────────
    async def set_welcome_text(self, text: str):
        await self.settings_col.update_one(
            {'_id': 'welcome_text'},
            {'$set': {'value': text}},
            upsert=True
        )

    async def get_welcome_text(self) -> str | None:
        doc = await self.settings_col.find_one({'_id': 'welcome_text'})
        return doc['value'] if doc else None

db = Database(DB_URI, DB_NAME)
