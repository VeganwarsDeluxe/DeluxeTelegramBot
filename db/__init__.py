import datetime

from aiogram.types import Update

from db.Chat import Chat
from db.TournierMatchResult import TournierMatchResult
from db.User import User
from db.startup import SessionLocal, Base, engine


class Database:
    def __init__(self):
        Base.metadata.create_all(bind=engine)

        self.__sl: SessionLocal = SessionLocal()

    def erase_ratings(self):
        self.__sl.query(User).update({User.rating: 1000})
        self.commit()

    def delete_match_result_by_date(self, datestamp: int):
        self.__sl.query(TournierMatchResult).filter(TournierMatchResult.date == datestamp).delete()

    def commit(self):
        self.__sl.commit()

    def get_top_players_by_tickets(self, limit=10):
        return self.__sl.query(User).order_by(User.tickets.desc()).limit(limit).all()

    def get_top_players_by_rating(self):
        return (self.__sl.query(User)
                .join(TournierMatchResult,
                      (User.id == TournierMatchResult.opponent_a_id) | (User.id == TournierMatchResult.opponent_b_id))
                .distinct().order_by(User.rating.desc()).limit(15))

    def get_match_results(self):
        return self.__sl.query(TournierMatchResult).order_by(TournierMatchResult.date.asc()).all()

    def create_user(self, user_id: int, name: str, username: str):
        new_user = User(id=user_id, name=name, username=username)
        self.__sl.add(new_user)
        self.__sl.commit()  # Commit the transaction
        self.__sl.refresh(new_user)  # Reload the instance with the new data from the database

        return new_user

    def change_locale(self, user_id: int, locale: str):
        user = self.__sl.query(User).filter(User.id == user_id).first()
        user.locale = locale
        self.__sl.commit()

        return user

    def get_user_locale(self, user_id: int):
        return self.get_user(user_id).locale

    def get_user(self, user_id):
        return self.__sl.query(User).filter(User.id == user_id).first()

    def get_user_by_username(self, username: str):
        return self.__sl.query(User).filter(User.username == username).first()

    def submit_match_result(self, user_a_id, user_b_id, user_a_score, user_b_score):
        datestamp = int(datetime.datetime.now(datetime.UTC).timestamp())
        result = TournierMatchResult(opponent_a_id=user_a_id,
                                     opponent_b_id=user_b_id,
                                     opponent_a_score=user_a_score,
                                     opponent_b_score=user_b_score,
                                     date=datestamp)
        self.__sl.add(result)
        self.__sl.commit()  # Commit the transaction

        return result, datestamp

    async def process_event(self, event: Update):
        if event.message:
            await self.process_message_event(event)

    async def process_message_event(self, event: Update):
        if event.message.from_user:
            await self.process_user(event.message.from_user)
        if event.message.chat:
            await self.process_chat(event.message.chat)

    async def process_chat(self, tg_chat):
        chat = self.__sl.query(Chat).filter(Chat.id == tg_chat.id).first()
        if not chat:
            chat = Chat(id=tg_chat.id, name=tg_chat.title)
            self.__sl.add(chat)
            self.__sl.commit()  # Commit the transaction
            self.__sl.refresh(chat)  # Reload the instance with the new data from the database
        chat.last_message = int(datetime.datetime.now(datetime.UTC).timestamp())
        chat.name = tg_chat.title
        self.__sl.commit()
        return chat

    async def process_user(self, tg_user: User):
        user = self.get_user(tg_user.id)
        if not user:
            user = self.create_user(tg_user.id, tg_user.full_name, str(tg_user.username))
        elif user.username != str(tg_user.username):
            user.username = str(tg_user.username)
            self.__sl.commit()
        return user


db = Database()
