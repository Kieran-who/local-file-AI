from .db_client import weav_setup


class DBClient:
    _instance = None

    async def __new__(cls):
        if cls._instance is None:
            cls._instance = await weav_setup()

        return cls._instance
