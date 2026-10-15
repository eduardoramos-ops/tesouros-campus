from contextlib import asynccontextmanager
from html import escape

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine, get_db
from app.models import Inscricao
from app.schemas import InscricaoCreate, InscricaoResponse


# ==========================================
# INICIALIZAÇÃO
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria as tabelas que ainda não existem
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Tesouros do Campus",
    description="Tesouros e grimório de inscrições.",
    version="1.0.0",
    lifespan=lifespan,
)

BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

# ==========================================
# TESOUROS FIXOS
# ==========================================

tesouros = {
    "TES-001": {
        "titulo": "O Primeiro Tesouro",
        "mensagem": "Toda jornada começa com o primeiro passo.",
        "raridade": "Comum",
    },
    "TES-002": {
        "titulo": "O Conhecimento Oculto",
        "mensagem": "O conhecimento floresce quando é compartilhado.",
        "raridade": "Raro",
    },
}


# ==========================================
# PÁGINA INICIAL
# ==========================================

@app.get("/", response_class=HTMLResponse)
def pagina_inicial():
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport"
              content="width=device-width, initial-scale=1.0">
        <title>Tesouros do Campus</title>
    </head>
    <body>
        <h1>Tesouros do Campus</h1>
        <p>Explore os tesouros espalhados pelo campus.</p>
        <a href="/grimorio">Visitar o grimório</a>
    </body>
    </html>
    """


# ==========================================
# PÁGINA DE UM TESOURO
# ==========================================

@app.get("/tesouro/{codigo}")
def consultar_tesouro(codigo: str):
    tesouro = tesouros.get(codigo.upper())

    if tesouro is None:
        raise HTTPException(
            status_code=404,
            detail="Tesouro não encontrado."
        )

    return FileResponse(
        BASE_DIR / "static" / "tesouros" / "tesouro.html"
    )

# ==========================================
# PÁGINA DO GRIMÓRIO
# ==========================================

@app.get("/grimorio")
def pagina_grimorio():
    return FileResponse(BASE_DIR / "static" / "index.html")

# ==========================================
# LISTAR INSCRIÇÕES
# ==========================================
@app.get("/api/tesouros/{codigo}")
def obter_tesouro(codigo: str):
    tesouro = tesouros.get(codigo.upper())

    if tesouro is None:
        raise HTTPException(
            status_code=404,
            detail="Tesouro não encontrado."
        )

    return tesouro

@app.get(
    "/api/inscricoes",
    response_model=list[InscricaoResponse],
)
def listar_inscricoes(db: Session = Depends(get_db)):
    return (
        db.query(Inscricao)
        .order_by(Inscricao.criado_em.desc())
        .all()
    )


# ==========================================
# CRIAR INSCRIÇÃO
# ==========================================

@app.post(
    "/api/inscricoes",
    response_model=InscricaoResponse,
    status_code=201,
)
def criar_inscricao(
    dados: InscricaoCreate,
    db: Session = Depends(get_db),
):
    nome = dados.nome.strip()
    mensagem = dados.mensagem.strip()

    if not nome:
        raise HTTPException(
            status_code=422,
            detail="O nome não pode ficar vazio.",
        )

    if not mensagem:
        raise HTTPException(
            status_code=422,
            detail="A mensagem não pode ficar vazia.",
        )

    if len(mensagem) > 100:
        raise HTTPException(
            status_code=422,
            detail="A mensagem deve ter no máximo 100 caracteres.",
        )

    nova_inscricao = Inscricao(
        nome=nome,
        mensagem=mensagem,
    )

    try:
        db.add(nova_inscricao)
        db.commit()
        db.refresh(nova_inscricao)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Não foi possível salvar a inscrição.",
        )

    return nova_inscricao


# ==========================================
# VERIFICAR A APLICAÇÃO
# ==========================================

@app.get("/health")
def verificar_saude():
    return {
        "status": "ok",
        "aplicacao": "Tesouros do Campus",
    }
