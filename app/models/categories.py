from typing import TYPE_CHECKING

from app.models.base import Base
if TYPE_CHECKING:
    from app.models.transactions import Transaction

from sqlalchemy.orm import Mapped, mapped_column, relationship

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


    transactions: Mapped[list[Transaction]] = relationship(
        "Transaction",
        back_populates="category"
    )