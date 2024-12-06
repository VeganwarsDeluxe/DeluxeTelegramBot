from aiogram.types import Update

from db.User import User
from db.startup import SessionLocal, Base, engine


class Database:
    def __init__(self):
        Base.metadata.create_all(bind=engine)

        self.__sl: SessionLocal = SessionLocal()

    def commit(self):
        self.__sl.commit()

    def get_top_players_by_tickets(self, limit=10):
        return self.__sl.query(User).order_by(User.tickets.desc()).limit(limit).all()

    def create_user(self, user_id: int, name: str):
        new_user = User(id=user_id, name=name)
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

    async def process_event(self, event: Update):
        if event.message:
            await self.process_message_event(event)

    async def process_message_event(self, event: Update):
        if event.message.from_user:
            await self.process_user(event.message.from_user)

    async def process_user(self, tg_user: User):
        user = self.get_user(tg_user.id)
        if not user:
            user = self.create_user(tg_user.id, tg_user.full_name)
        return user


db = Database()
