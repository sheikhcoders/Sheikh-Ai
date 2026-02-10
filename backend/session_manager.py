import json
import os

class SessionManager:
    def __init__(self, storage_dir="sessions", db_type="file"):
        self.db_type = db_type
        self.storage_dir = storage_dir
        if self.db_type == "file" and not os.path.exists(storage_dir):
            os.makedirs(storage_dir)

        # In a real scenario, initialize MongoDB/Redis here
        # self.db = self._init_db()

    def _init_db(self):
        if self.db_type == "mongodb":
            # import pymongo
            # return pymongo.MongoClient(os.getenv("MONGODB_URI"))
            pass
        elif self.db_type == "redis":
            # import redis
            # return redis.Redis.from_url(os.getenv("REDIS_URL"))
            pass
        return None

    def _get_session_path(self, session_id):
        return os.path.join(self.storage_dir, f"{session_id}.json")

    def save_event(self, session_id, event):
        if self.db_type == "file":
            path = self._get_session_path(session_id)
            events = self.get_events(session_id)
            events.append(event)
            with open(path, "w") as f:
                json.dump(events, f)
        # elif self.db_type == "mongodb":
        #     self.db.sessions.events.insert_one({"session_id": session_id, **event})

    def get_events(self, session_id):
        if self.db_type == "file":
            path = self._get_session_path(session_id)
            if os.path.exists(path):
                with open(path, "r") as f:
                    return json.load(f)
        return []

session_manager = SessionManager(db_type=os.getenv("SESSION_DB_TYPE", "file"))
