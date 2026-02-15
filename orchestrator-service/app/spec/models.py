import uuid

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from app.core.database import Base
from app.spec.enums import SpecStatus


class Spec(Base):
    __tablename__ = "specs"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(String, index=True, nullable=False)

    original_content: Mapped[str] = mapped_column(Text, nullable=False)

    parsed_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    status: Mapped[str] = mapped_column(
        String, default=SpecStatus.PENDING, nullable=False
    )

    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    results: Mapped[list["SpecResult"]] = relationship(
        back_populates="spec", cascade="all, delete-orphan"
    )


class SpecResult(Base):
    __tablename__ = "spec_results"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    spec_id: Mapped[str] = mapped_column(
        String, ForeignKey("specs.id", ondelete="CASCADE"), index=True, nullable=False
    )

    agent_type: Mapped[str] = mapped_column(String, nullable=False)

    content: Mapped[dict] = mapped_column(JSONB, nullable=False)

    spec: Mapped["Spec"] = relationship(back_populates="results")