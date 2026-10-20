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
from app.schemas import InscricaoCreate, InscricaoResponse, TesouroResponse


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
        "titulo": "Você encontrou jóias",
        "mensagem": "Toda jornada começa com o primeiro passo.",
        "raridade": "Comum",
        "imagem": "https://i.pinimg.com/236x/12/60/7b/12607b2033808e03af17d718937c9058.jpg",
    },

    "TES-002": {
            "titulo": "Você encontrou um personagem raro!",
            "mensagem": "Capitão anti-social que gosta de poesias",
            "raridade": "Raro",
            "imagem": "https://i.pinimg.com/736x/5a/04/c5/5a04c55de6fd635fcea6164e34c6a21a.jpg",
        },

    "TES-003": {
            "titulo": "Você encontrou um personagem lendário!",
            "mensagem": "Um cogumelo que não está para brincadeiras! ",
            "raridade": "Lendário",
            "imagem": "https://i.pinimg.com/736x/00/55/24/005524b2a2165c126bb0cdea222c251a.jpg",
        },
    "TES-004": {
            "titulo": "Você encontrou um personagem lendário!",
            "mensagem": "Um cogumelo que não está para brincadeiras! ",
            "raridade": "Lendário",
            "imagem": "https://i.pinimg.com/736x/00/55/24/005524b2a2165c126bb0cdea222c251a.jpg",
        },

    "TES-005": {
                "titulo": "Você encontrou uma carta de debuff mítico!",
                "mensagem": "Qualquer um que a encontra passa a ficar desonline para sempre!",
                "raridade": "Mítico",
                "imagem": "https://i.pinimg.com/736x/f8/0f/7c/f80f7cba99d293d1f003c6d19809d571.jpg",
            },
    "TES-006": {
                "titulo": "Você caiu em uma armadilha!",
                "mensagem": "O pedrin do free fire expandiu o seu domínio e te prendeu nele, onde o capa é absoluto!",
                "raridade": "xxxxxx",
                "imagem": "https://i.pinimg.com/736x/89/0d/45/890d45e57c7a58c31af6fd8f692787d0.jpg ",
                },

    "TES-007": {
                    "titulo": "Você encontrou uma carta mítica!",
                    "mensagem": "+1000 aura e -999 ego",
                    "raridade": "Mítico",
                    "imagem": "https://i.pinimg.com/736x/35/a4/0b/35a40b06bea33951093e8c2ce8178cb2.jpg",
                    "video": "blob:https://br.pinterest.com/2f3c8403-1286-48db-a093-1b8a77b308af"
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
@app.get("/api/tesouros/{codigo}", response_model=TesouroResponse)
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
