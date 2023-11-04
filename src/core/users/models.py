from src.core.sql.database import SQLModel
from sqlalchemy import Column, String, Integer, DateTime, func
from werkzeug.security import generate_password_hash, check_password_hash


class User(SQLModel):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(128), nullable=True)
    last_name = Column(String(128), nullable=True)
    username = Column(String(128), nullable=False, unique=True, index=True)
    email = Column(String(320), nullable=False, unique=True, index=True)
    joined_date = Column(DateTime(timezone=True), server_default=func.now())
    phone_number = Column(String(16), unique=True, index=True)
    password_hash = Column(String(128))

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password=password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(pwhash=self.password_hash, password=password)
