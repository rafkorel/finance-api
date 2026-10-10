from app.models.base import Base

from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy import String, Identity, CheckConstraint

class Category(Base):
    __tablename__ = "categories"


    category_id: Mapped[int] = mapped_column(
        Identity(),
        primary_key=True
    )


    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )


    type: Mapped[str] = mapped_column(
        String(7),
        CheckConstraint("type IN ('income', 'expense')", name="type_check"),
        nullable=False
    )