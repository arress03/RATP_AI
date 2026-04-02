from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Snapshot(Base):
    __tablename__ = "snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, unique=True, index=True)
    total_calls: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    raw_file_path: Mapped[str] = mapped_column(String, nullable=False)

    calls: Mapped[list["MetroCall"]] = relationship("MetroCall", back_populates="snapshot")


class MetroCall(Base):
    __tablename__ = "metro_calls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    snapshot_id: Mapped[int] = mapped_column(Integer, ForeignKey("snapshots.id"), nullable=False, index=True)
    line: Mapped[str] = mapped_column(String, nullable=False, index=True)
    stop: Mapped[str] = mapped_column(String, nullable=False)
    departure_status: Mapped[str] = mapped_column(String, nullable=False, default="")
    arrival_status: Mapped[str] = mapped_column(String, nullable=False, default="")
    is_delayed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    expected_departure: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    aimed_departure: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    snapshot: Mapped["Snapshot"] = relationship("Snapshot", back_populates="calls")
