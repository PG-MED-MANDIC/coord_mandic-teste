"""Gera a versão publicável do AMBIENTE DE TESTE do dashboard da coordenação.

Mesmo script do repositório real (`coord_mandic_pgmed/pipeline/publicar.py`),
só que publica em `coord_mandic-teste` (site à parte, com seu próprio link) --
serve pra testar mudanças sem risco de derrubar o site real. Injeta uma
faixa vermelha fixa no topo ("AMBIENTE DE TESTE") pra nunca confundir com
o de produção, mesmo se alguém salvar o link errado.

Fluxo:
    1. salvar o HTML novo em fonte/index_aberto.html (pasta fora do git)
    2. python pipeline/publicar.py        # pede a senha no terminal
    3. git add index.html pagina.enc && git commit && git push

Quando o teste estiver aprovado, o MESMO fonte/index_aberto.html é copiado
pra coord_mandic_pgmed/fonte/index_aberto.html e publicado lá (repositório
real) -- ver README.md deste repositório.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from protecao import cifrar_texto, obter_senha

PIPELINE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = PIPELINE_DIR.parent
FONTE_PATH = PROJECT_DIR / "fonte" / "index_aberto.html"
PAGINA_ENC_PATH = PROJECT_DIR / "pagina.enc"
INDEX_HTML_PATH = PROJECT_DIR / "index.html"

TITULO = "CSAT Pós Med — Coordenação (TESTE)"

FAIXA_TESTE = (
    '<div style="position:fixed;top:0;left:0;right:0;z-index:100000;background:#dc2626;'
    'color:#fff;text-align:center;font:700 12px/1 Arial,sans-serif;padding:6px;'
    'letter-spacing:.5px">🧪 AMBIENTE DE TESTE -- NÃO É O SITE REAL, dados podem estar '
    "incompletos ou quebrados</div>"
)

INDEX_HTML = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>{TITULO} — São Leopoldo Mandic</title>
</head>
<body style="margin:0;background:#f4f6fa">
<noscript>Ative o JavaScript para acessar o dashboard.</noscript>
<script src="protecao.js"></script>
<script>Protecao.iniciar({{ arquivo: 'pagina.enc', modo: 'pagina', titulo: '{TITULO}', chaveSessao: 'coord_teste_chave_v1' }});</script>
</body>
</html>
"""


def remover_tela_senha_antiga(html: str) -> str:
    inicio = html.find('<div id="pw-gate"')
    if inicio == -1:
        return html
    fim_script = html.find("</script>", html.find("window.checkPwGate", inicio))
    if fim_script == -1:
        raise RuntimeError("tela de senha antiga encontrada, mas sem o <script> de fechamento esperado")
    return html[:inicio] + html[fim_script + len("</script>"):]


def esvaziar_const(html: str, nome: str) -> str:
    novo, n = re.subn(rf"^const {nome} = .*$", f"const {nome} = [];  // removido na migração (ver README)", html, count=1, flags=re.M)
    if n == 0 and f"const {nome}" in html:
        raise RuntimeError(f"{nome} existe mas não está no formato esperado (uma linha só)")
    return novo


def inserir_faixa_teste(html: str) -> str:
    marcador = "<body>"
    i = html.find(marcador)
    if i == -1:
        raise RuntimeError("<body> não encontrado -- não consegui inserir a faixa de teste")
    return html[: i + len(marcador)] + "\n" + FAIXA_TESTE + html[i + len(marcador):]


def conferir(html: str) -> list[str]:
    problemas = []
    if "docente321" in html or "checkPwGate" in html:
        problemas.append("sobrou a senha antiga no HTML")
    if re.search(r"^const DATA_\w+ = .*\"aluno\"\s*:\s*\"", html, flags=re.M):
        problemas.append('sobrou campo "aluno" com valor numa base DATA_* (lista de inadimplentes?)')
    n_emails = len(re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", html))
    if n_emails:
        problemas.append(f"{n_emails} endereço(s) de e-mail no HTML")
    return problemas


def main() -> int:
    if not FONTE_PATH.exists():
        print(f"Não achei {FONTE_PATH.relative_to(PROJECT_DIR)} -- salve o HTML aberto lá primeiro.")
        return 1

    html = FONTE_PATH.read_bytes().decode("utf-8")
    html = remover_tela_senha_antiga(html)
    html = esvaziar_const(html, "DATA_INAD")
    html = esvaziar_const(html, "DATA_PDD")

    problemas = conferir(html)
    if problemas:
        print("NÃO publicado -- revise o HTML:")
        for p in problemas:
            print(f"  - {p}")
        return 1

    html = inserir_faixa_teste(html)

    senha = obter_senha(confirmar=True)
    PAGINA_ENC_PATH.write_text(cifrar_texto(html, senha), encoding="ascii")
    INDEX_HTML_PATH.write_text(INDEX_HTML, encoding="utf-8", newline="\n")

    print(f"OK -- {PAGINA_ENC_PATH.name} ({PAGINA_ENC_PATH.stat().st_size / 1e6:.1f} MB) e {INDEX_HTML_PATH.name} gerados.")
    print("Próximos passos:\n  git add index.html pagina.enc\n  git commit -m \"Atualiza dados do dashboard (teste)\"\n  git push")
    return 0


if __name__ == "__main__":
    sys.exit(main())
