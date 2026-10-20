
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
)


# Dados recebidos ao criar uma inscrição
class InscricaoCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=50)
    mensagem: str = Field(min_length=1, max_length=100)

    @field_validator("nome", "mensagem")
    @classmethod
    def remover_espacos(cls, valor: str) -> str:
        return valor.strip()


# Dados devolvidos pela API
class InscricaoResponse(BaseModel):
    id: int
    nome: str
    mensagem: str
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


# Dados devolvidos ao consultar um tesouro
class TesouroResponse(BaseModel):
    titulo: str
    mensagem: str
    raridade: str
    imagem: HttpUrl | None = None
