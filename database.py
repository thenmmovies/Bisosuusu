# (c) @AbirHasan2005

import certifi
import motor.motor_asyncio
from configs import Config


class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri, tlsCAFile=certifi.where())
        self.db = self._client[database_name]
        self.col = self.db.users

    def new_doc(self, doc_id):
        return dict(
            doc_id=doc_id,
        )

    async def add_doc(self, doc_id):
        doc = self.new_doc(doc_id)
        await self.col.insert_one(doc)

    async def is_doc_exist(self, doc_id):
        doc = await self.col.find_one({'doc_id': int(doc_id)})
        return bool(doc)

    async def total_docs_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_docs(self):
        return self.col.find({})

    async def delete_doc(self, doc_id: int):
        await self.col.delete_many({'doc_id': doc_id})

    async def get_doc_raw_data(self, doc_id: int):
        doc = await self.col.find_one({'doc_id': doc_id})
        return doc or {}

    async def set_quantity(self, doc_id: int, quantity: int):
        await self.col.update_one({'doc_id': doc_id}, {'$set': {'quantity': quantity}})

    async def get_quantity(self, doc_id: int) -> int:
        doc = await self.col.find_one({'doc_id': doc_id})
        return doc.get('quantity', Config.Defaults.QUANTITY) if doc else Config.Defaults.QUANTITY

    async def set_sleep_time(self, doc_id: int, sleep_time: int):
        await self.col.update_one({'doc_id': doc_id}, {'$set': {'sleep_time': sleep_time}})

    async def get_sleep_time(self, doc_id: int) -> int:
        doc = await self.col.find_one({'doc_id': doc_id})
        return doc.get('sleep_time', Config.Defaults.SLEEP_TIME) if doc else Config.Defaults.SLEEP_TIME


db = Database(Config.MONGO_DB_ACCESS_URI, Config.MONGO_DB_COLLECTION_NAME)
