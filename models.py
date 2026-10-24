from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Training(Base):
    __tablename__ = "training"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )
    user: Mapped["User"] = relationship(back_populates="trainings")
    date: Mapped[str] = mapped_column(Text, nullable=False)
    shots: Mapped[int] = mapped_column(Integer, nullable=False)
    made: Mapped[int] = mapped_column(Integer, nullable=False)

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )
    trainings: Mapped[list["Training"]] = relationship(
        back_populates="user"
    )