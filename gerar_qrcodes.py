
import qrcode
from pathlib import Path

# Enquanto estiver desenvolvendo no próprio computador:
URL_BASE = "https://tesouros-campus.onrender.com"

PASTA_QRCODES = Path("qrcodes")

TESOUROS = [
    "TES-001",
    "TES-002",
    "TES-003",
    "TES-004",
    "TES-005",
    "TES-006",
    "TES-007",
]


def gerar_qrcode(url: str, nome_arquivo: str):
    imagem = qrcode.make(url)

    caminho = PASTA_QRCODES / nome_arquivo
    imagem.save(caminho)

    print(f"QR code gerado: {caminho} -> {url}")


def main():
    PASTA_QRCODES.mkdir(parents=True, exist_ok=True)

    gerar_qrcode(
        f"{URL_BASE}/grimorio",
        "grimorio.png"
    )

    for codigo in TESOUROS:
        gerar_qrcode(
            f"{URL_BASE}/tesouro/{codigo}",
            f"{codigo.lower()}.png"
        )

    print("\nTodos os QR codes foram gerados!")


if __name__ == "__main__":
    main()
