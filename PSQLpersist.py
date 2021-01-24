from collections import defaultdict
from copy import deepcopy
from typing import DefaultDict, Dict, Any
from configReader import config

from sqlalchemy import create_engine, Column, Integer, PickleType, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from telegram.ext import DictPersistence

base = declarative_base()


class Storage(base):
    __tablename__ = "storage_beta"
    id = Column(Integer, primary_key=True)
    bot_data = Column(PickleType)
    chat_data = Column(PickleType)
    user_data = Column(PickleType)
    conversations = Column(PickleType)
    bot_data_json = Column(JSON)
    chat_data_json = Column(JSON)
    user_data_json = Column(JSON)


class ChatDataUsers(base):
    __tablename__ = "chat_data_users"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    userdata = Column(String)


class PsqlPersistence(DictPersistence):
    # postgresql+psycopg2://USER:PASS@address:5432/db
    params = config()
    connectionString = "postgresql+psycopg2://" + params["user"] + ":" + params["password"] + "@" + params[
        "host"] + ":" + params["port"] + "/" + params["database"]
    print(connectionString)
    db = create_engine(connectionString, echo=True)
    base.metadata.create_all(db)
    Session = sessionmaker(db)
    session = Session()

    def __repr__(self):
        return "<User(name='%s', fullname='%s', nickname='%s')>" % (self.name, self.fullname, self.nickname)

    def get_user_data(self) -> Dict[Any, Any]:
        query = self.session.query(Storage).first()
        if query:
            self._user_data = query.user_data
        else:
            self._user_data = defaultdict(dict)
        return deepcopy(self.user_data)

    def get_chat_data(self) -> DefaultDict[int, Dict[Any, Any]]:
        print("reading data")
        if self.chat_data:
            pass
        else:
            chat_data_users = self.session.query(ChatDataUsers).all()
            if chat_data_users:
                self._chat_data = defaultdict(dict)
                for entry in chat_data_users:
                    self._chat_data[entry.id] = {"users": {}}
                    self._chat_data[entry.id]["users"].update({"username": entry.username})
                    self._chat_data[entry.id]["users"].update({"userdata": entry.userdata})
        return deepcopy(self.chat_data) # type: ignore[arg-type]

    def get_bot_data(self) -> Dict[Any, Any]:
        query = self.session.query(Storage).first()
        if query:
            self._bot_data = query.bot_data
        else:
            self._bot_data = {}
        return deepcopy(self.bot_data)  # type: ignore[arg-type]

    def update_chat_data(self, chat_id: int, data: Dict) -> None:
        """Will update the chat_data (if changed).

        Args:
            chat_id (:obj:`int`): The chat the data might have been changed for.
            data (:obj:`dict`): The :attr:`telegram.ext.dispatcher.chat_data` [chat_id].
        """
        print("Das sind die Daten: ", data)
        print("Das sind die Daten: ", data["users"])
        chat_data_users = self.session.query(ChatDataUsers).first()
        if not chat_data_users:
            #chat_data_new = ChatDataUsers(id=chat_id, username=data.get(chat_id), userdata)
            #self.session.add(chat_data_new)
            print("lel")
        else:
            storage = chat_data_users
            storage.username = data["users"]["username"]
            storage.userdata = data["users"]["userdata"]
        self.session.commit()
        return

    def flush(self) -> None:
        query = self.session.query(Storage).first()
        if not query:
            storage = Storage(bot_data=self._bot_data, chat_data=self._chat_data, user_data=self._user_data,
                              bot_data_json=self.bot_data_json, user_data_json=self.user_data_json,
                              chat_data_json=self.chat_data_json)
            self.session.add(storage)
        else:
            storage = query
            storage.bot_data = self.bot_data
            storage.chat_data = self.chat_data
            storage.user_data = self.user_data
            storage.bot_data_json = self.bot_data_json
            storage.chat_data_json = self.chat_data_json
            storage.user_data_json = self.user_data_json
        # self.session.flush()
        self.session.commit()
        print("Data saved successfully")

    def __init__(self):
        super().__init__()
