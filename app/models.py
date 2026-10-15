
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Local(Base):
    __tablename__ = "locais"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    codigo: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
    )

    titulo: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    mensagem: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    raridade: Mapped[str] = mapped_column(
        String(30),
        default="Comum",
        nullable=False,
    )

    imagem: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    ativo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )


class Inscricao(Base):
    __tablename__ = "inscricoes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    nome: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    mensagem: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
