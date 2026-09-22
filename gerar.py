#!/usr/bin/env python3
"""gerar.py — constrói ateliedeotica.com.br.

    python gerar.py              # gera site/ e lista as pendências
    python gerar.py --publicar   # idem, mas FALHA se houver pendência

A verdade mora em três lugares, e esta pasta não guarda uma quarta:
  conteudo/*.md          o texto de cada página (front matter + Markdown)
  negocio.toml           endereço, WhatsApp, horários — um lugar só
  app-leitura/src/styles.css   os nove temas, lidos token a token

O site/ é DERIVADO. Nunca editar à mão: a próxima geração sobrescreve.
Sem dependência: biblioteca padrão do Python 3.11+.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
import tomllib
from datetime import date
from pathlib import Path
from urllib.parse import quote

RAIZ = Path(__file__).resolve().parent
CONTEUDO = RAIZ / "conteudo"
CASCA = RAIZ / "casca"
SAIDA = RAIZ / "site"
APP_LEITURA = RAIZ.parent / "app-leitura"
STYLES = APP_LEITURA / "src" / "styles.css"
FONTES_ORIGEM = APP_LEITURA / "public" / "fonts"

# Espelha o que casca/base.css declara. Se mudar lá, muda aqui — é o que a
# página /acessibilidade afirma, e ela não pode mentir.
ESPEC = {
    "corpo_base": "18 pixels (112,5% da letra do aparelho)",
    "entrelinha": "1,6",
    "medida": "cerca de 70 caracteres",
}


# --------------------------------------------------------------------------
# Os nove temas — lidos, nunca redigitados (mesmo método do Pórtico)
# --------------------------------------------------------------------------

TEMAS = [
    ("sepia", "Sépia", "padrão"),
    ("claro", "Preto sobre branco", None),
    ("escuro", "Branco sobre preto", None),
    ("amarelo", "Amarelo sobre preto", None),
    ("verde", "Verde sobre preto", None),
    ("azul-noite", "Azul-noite", "pensado para protanomalia"),
    ("azul-petroleo", "Azul-petróleo", None),
    ("pergaminho", "Pergaminho", None),
    ("amarelo-azul", "Amarelo sobre azul", None),
]

TOKEN = re.compile(
    r"^\s*(--color-[\w-]+|--hl-[\w-]+|--shadow-color|--ui-foco|color-scheme)\s*:\s*([^;]+);"
)


def extrair_bloco(css: str, seletor: str) -> str:
    idx = css.find(seletor)
    if idx == -1:
        return ""
    ini = css.find("{", idx)
    return css[ini + 1:css.find("}", ini)]


def tokens(bloco: str) -> dict[str, str]:
    saida = {}
    for linha in bloco.split("\n"):
        m = TOKEN.match(linha)
        if m:
            saida[m.group(1)] = m.group(2).strip()
    return saida


def ler_temas() -> dict[str, dict[str, str]]:
    if not STYLES.exists():
        sys.exit(f"ERRO: não achei {STYLES} — os temas vêm de lá.")
    css = STYLES.read_text(encoding="utf-8")
    temas = {"sepia": tokens(extrair_bloco(css, ":root {"))}
    for chave, _, _ in TEMAS[1:]:
        t = tokens(extrair_bloco(css, f"[data-theme='{chave}'] {{"))
        if not t:
            print(f"AVISO: tema '{chave}' não encontrado no styles.css", file=sys.stderr)
            continue
        temas[chave] = {**temas["sepia"], **t}
    temas["_manchas"] = extrair_bloco(css, "[data-theme='pergaminho'] body {")
    return temas


def css_dos_temas(temas) -> str:
    def decl(d):
        return "\n".join(f"  {k}: {v};" for k, v in d.items())
    partes = ["/* Os nove temas, lidos de app-leitura/src/styles.css pelo gerar.py. Não editar aqui. */",
              ":root,\n[data-theme='sepia'] {\n" + decl(temas["sepia"]) + "\n}"]
    for chave, _, _ in TEMAS[1:]:
        if chave in temas:
            partes.append(f"[data-theme='{chave}'] {{\n" + decl(temas[chave]) + "\n}")
    if temas["_manchas"].strip():
        partes.append("[data-theme='pergaminho'] body {" + temas["_manchas"] + "}")
    return "\n\n".join(partes)


# --------------------------------------------------------------------------
# Contraste — medido na geração, publicado em /acessibilidade
# --------------------------------------------------------------------------

def hex_rgb(valor: str):
    v = valor.strip().lstrip("#")
    if not re.fullmatch(r"[0-9a-fA-F]{3}|[0-9a-fA-F]{6}", v):
        return None
    if len(v) == 3:
        v = "".join(c * 2 for c in v)
    return tuple(int(v[i:i + 2], 16) / 255 for i in (0, 2, 4))


def linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def srgb(c):
    c = min(1.0, max(0.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


# Machado, Oliveira & Fernandes (2009), severidade 1,0, em RGB linear.
SIMULACOES = {
    "protanopia": ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998)),
    "deuteranopia": ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881)),
    "tritanopia": ((1.255528, -0.076749, -0.178779), (-0.078411, 0.930809, 0.147602), (0.004733, 0.691367, 0.303900)),
}


def simular(rgb, matriz):
    lin = [linear(c) for c in rgb]
    return tuple(srgb(sum(m * c for m, c in zip(linha, lin))) for linha in matriz)


def luminancia(rgb):
    r, g, b = (linear(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def razao(a, b):
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def pior_razao(frente: str, fundos: list[str]):
    """Menor razão entre a cor e cada fundo, na visão típica e nas três simulações."""
    f = hex_rgb(frente)
    fs = [hex_rgb(x) for x in fundos]
    if f is None or any(x is None for x in fs):
        return None
    valores = []
    for fundo in fs:
        valores.append(razao(f, fundo))
        for m in SIMULACOES.values():
            valores.append(razao(simular(f, m), simular(fundo, m)))
    return min(valores)


PARES = [
    # rótulo, token de frente, fundos onde aparece, meta
    ("Texto", "--color-text", ["--color-bg", "--color-surface"], 7.0),
    ("Destaque", "--color-accent", ["--color-bg", "--color-surface"], 7.0),
    ("Contorno", "--color-borda-ui", ["--color-bg", "--color-surface"], 3.0),
]


def medir_temas(temas):
    linhas = []
    for chave, nome, _ in TEMAS:
        t = temas.get(chave)
        if not t:
            continue
        medidas = []
        for rotulo, frente, fundos, meta in PARES:
            r = pior_razao(t.get(frente, ""), [t.get(f, "") for f in fundos])
            medidas.append((rotulo, r, meta))
        linhas.append((chave, nome, medidas))
    return linhas


def fmt_razao(r):
    return "—" if r is None else f"{r:.1f}:1".replace(".", ",")


def tabela_contraste(medicoes) -> str:
    cab = "".join(f"<th scope=\"col\">{p[0]} <span class=\"opcao-dica\">meta {fmt_razao(p[3])}</span></th>" for p in PARES)
    corpo = []
    for chave, nome, medidas in medicoes:
        celulas = []
        for _, r, meta in medidas:
            ok = r is not None and r >= meta
            selo = "atinge" if ok else '<span class="selo-abaixo">abaixo</span>'
            celulas.append(f'<td class="num">{fmt_razao(r)} · {selo}</td>')
        corpo.append(
            f'<tr><th scope="row"><span class="amostra-tema" data-theme="{chave}" aria-hidden="true">'
            f'A<b>a</b></span>{html.escape(nome)}</th>{"".join(celulas)}</tr>'
        )
    return (
        '<div class="rolagem-tabela"><table>'
        '<caption class="chapeu" style="text-align:left;padding:.8rem .8rem 0">'
        'Pior contraste de cada par, na visão típica e sob as três simulações</caption>'
        f'<thead><tr><th scope="col">Tema</th>{cab}</tr></thead>'
        f'<tbody>{"".join(corpo)}</tbody></table></div>'
    )


# --------------------------------------------------------------------------
# Fontes — LEI 3: nenhuma vem da rede
# --------------------------------------------------------------------------

FONTES = [
    ("Atkinson Hyperlegible", "normal", 400, "atkinson-hyperlegible-400.woff2"),
    ("Atkinson Hyperlegible", "italic", 400, "atkinson-hyperlegible-400i.woff2"),
    ("Atkinson Hyperlegible", "normal", 700, "atkinson-hyperlegible-700.woff2"),
    ("Atkinson Hyperlegible", "italic", 700, "atkinson-hyperlegible-700i.woff2"),
    ("Cardo", "normal", 400, "cardo-regular.woff2"),
    ("Cardo", "italic", 400, "cardo-italic.woff2"),
    ("Cardo", "normal", 700, "cardo-bold.woff2"),
    ("OpenDyslexic", "normal", 400, "opendyslexic-400.woff"),
    ("OpenDyslexic", "normal", 700, "opendyslexic-700.woff"),
    ("OpenDyslexic", "italic", 400, "opendyslexic-400i.woff"),
    ("Marca Angular", "normal", 400, "marca-angular.woff2"),
]
LICENCAS = ["Atkinson-OFL.txt", "Cardo-OFL.txt", "OpenDyslexic-OFL.txt", "MarcaAngular-GFSDidot-OFL.txt"]


def css_das_fontes() -> str:
    regras = []
    for familia, estilo, peso, arquivo in FONTES:
        formato = "woff2" if arquivo.endswith(".woff2") else "woff"
        exibicao = "block" if familia == "Marca Angular" else "swap"
        regras.append(
            f"@font-face{{font-family:'{familia}';font-style:{estilo};font-weight:{peso};"
            f"font-display:{exibicao};src:url('fontes/{arquivo}') format('{formato}')}}"
        )
    return "\n".join(regras)


def copiar_fontes(destino: Path):
    destino.mkdir(parents=True, exist_ok=True)
    for _, _, _, arquivo in FONTES:
        origem = FONTES_ORIGEM / arquivo
        if origem.exists():
            shutil.copy2(origem, destino / arquivo)
        else:
            print(f"AVISO: fonte ausente: {arquivo}", file=sys.stderr)
    for lic in LICENCAS:
        if (FONTES_ORIGEM / lic).exists():
            shutil.copy2(FONTES_ORIGEM / lic, destino / lic)


# --------------------------------------------------------------------------
# Páginas: front matter + Markdown
# --------------------------------------------------------------------------

def ler_pagina(caminho: Path) -> dict:
    return interpretar_pagina(caminho.read_text(encoding="utf-8"), caminho.name)


def interpretar_pagina(texto: str, nome: str) -> dict:
    meta = {}
    if texto.startswith("---"):
        fim = texto.find("\n---", 3)
        for linha in texto[3:fim].strip().splitlines():
            if ":" in linha:
                k, v = linha.split(":", 1)
                meta[k.strip()] = v.strip()
        texto = texto[fim + 4:]
    meta["corpo_md"] = texto
    meta["arquivo"] = nome
    meta["ordem"] = int(meta.get("ordem", 99))
    return meta


def caminho_de_saida(rota: str) -> Path:
    return SAIDA / "index.html" if rota == "/" else SAIDA / rota.strip("/") / "index.html"


def prefixo(rota: str) -> str:
    """Caminho relativo da página até a raiz do site."""
    if rota == "/404":
        return "/"
    profundidade = 0 if rota == "/" else rota.strip("/").count("/") + 1
    return "../" * profundidade or "./"


def slug(texto: str) -> str:
    import unicodedata
    t = unicodedata.normalize("NFKD", texto)
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def rua(endereco: str) -> str:
    """Só a rua e o número: o bairro atrapalha busca de mapa e campo de endereço."""
    return re.split(r"\s+[—–-]\s+", endereco)[0].strip()


class Contexto:
    def __init__(self, negocio, pagina, blocos, pendencias):
        self.negocio = negocio
        self.pagina = pagina
        self.pre = prefixo(pagina["rota"])
        self.blocos = blocos
        self.pendencias = pendencias
        self.ids = set()

    def pendente(self, campo):
        self.pendencias.setdefault(campo, set()).add(self.pagina["arquivo"])
        return f'<mark class="pendente">[a preencher: {html.escape(campo)}]</mark>'

    def campo(self, nome):
        if nome == "mapa":
            end = self.negocio.get("endereco", "")
            if not end:
                return ""
            q = quote(f"{rua(end)}, {self.negocio['cidade']} - {self.negocio['uf']}, "
                      f"{self.negocio.get('cep', '')}".strip(", "))
            return f'<a href="https://www.google.com/maps/search/?api=1&amp;query={q}">Abrir no mapa</a>'
        if nome == "whatsapp_legivel" and self.negocio.get("whatsapp_legivel"):
            return self.link_whatsapp_simples(self.negocio["whatsapp_legivel"])
        if nome == "instagram" and self.negocio.get("instagram"):
            u = html.escape(self.negocio["instagram"].lstrip("@"))
            return f'<a href="https://www.instagram.com/{u}/" rel="noopener">@{u}</a>'
        if nome == "email" and self.negocio.get("email"):
            e = html.escape(self.negocio["email"])
            return f'<a href="mailto:{e}">{e}</a>'
        valor = self.negocio.get(nome)
        if valor is None:
            valor = ESPEC.get(nome)
        if valor is None:
            print(f"AVISO: {self.pagina['arquivo']}: marcador desconhecido {{{{{nome}}}}}", file=sys.stderr)
            return f"{{{{{html.escape(nome)}}}}}"
        if valor == "":
            return self.pendente(nome)
        return html.escape(str(valor))

    def link_whatsapp_simples(self, rotulo):
        return f'<a href="{self.href_whatsapp("agendar")}">{html.escape(rotulo)}</a>'

    def href_whatsapp(self, chave):
        numero = self.negocio.get("whatsapp", "")
        if not numero:
            self.pendente("whatsapp")
            return f"{self.pre}contato/"
        msg = self.negocio.get(f"mensagem_{chave}", chave)
        return f"https://wa.me/{numero}?text={quote(msg)}"

    def href(self, destino):
        if destino.startswith("whatsapp:"):
            return self.href_whatsapp(destino.split(":", 1)[1])
        if destino.startswith("/"):
            caminho, _, ancora = destino.partition("#")
            rel = "" if caminho == "/" else caminho.strip("/") + "/"
            alvo = (self.pre + rel) if rel or self.pre != "./" else "./"
            return alvo + (f"#{ancora}" if ancora else "")
        return destino


ICONE_CONVERSA = (
    '<svg class="icone-conversa" viewBox="0 0 24 24" aria-hidden="true" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M21 11.5a8.4 8.4 0 0 1-9 8.4 8.6 8.6 0 0 1-3.9-.9L3 20.5l1.5-4.6A8.4 8.4 0 1 1 21 11.5z"/></svg>'
)


def inline(texto: str, ctx: Contexto) -> str:
    codigos = []

    def guardar(m):
        codigos.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00{len(codigos) - 1}\x00"

    t = re.sub(r"`([^`]+)`", guardar, texto)
    t = html.escape(t, quote=False).replace("&lt;br&gt;", "<br>")
    t = re.sub(r"\{\{(\w+)\}\}", lambda m: ctx.campo(m.group(1)), t)

    def link(m):
        rotulo, destino, classe = m.group(1), html.unescape(m.group(2)), m.group(3)
        href = html.escape(ctx.href(destino))
        attrs = f' class="{classe}"' if classe else ""
        if destino.startswith("whatsapp:") and classe == "botao":
            rotulo = ICONE_CONVERSA + rotulo
        if href.startswith("http"):
            attrs += ' rel="noopener"'
        return f'<a href="{href}"{attrs}>{rotulo}</a>'

    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)(?:\{\.([\w-]+)\})?", link, t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", t)
    return re.sub(r"\x00(\d+)\x00", lambda m: codigos[int(m.group(1))], t)


ITEM = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.*)$")
TITULO = re.compile(r"^(#{1,4})\s+(.*?)(?:\s+\{#([\w-]+)\})?\s*$")


def md_para_html(texto: str, ctx: Contexto) -> str:
    linhas = texto.split("\n")
    saida, i, n = [], 0, len(linhas)

    def comeca_bloco(s):
        return (not s or s.startswith(":::") or s.startswith("#") or s.startswith("<")
                or s.startswith(">") or ITEM.match(s) is not None)

    while i < n:
        s = linhas[i].strip()
        if not s:
            i += 1
            continue
        if s.startswith(":::"):
            nome = s[3:].strip()
            saida.append(f'<div class="{html.escape(nome)}">' if nome else "</div>")
            i += 1
            continue
        m = TITULO.match(s)
        if m:
            nivel = len(m.group(1))
            titulo = m.group(2)
            ident = m.group(3) or slug(re.sub(r"[*`]", "", titulo))
            base, k = ident, 2
            while ident in ctx.ids:
                ident, k = f"{base}-{k}", k + 1
            ctx.ids.add(ident)
            saida.append(f'<h{nivel} id="{ident}">{inline(titulo, ctx)}</h{nivel}>')
            i += 1
            continue
        mb = re.fullmatch(r"\{\{(\w+)\}\}", s)
        if mb and mb.group(1) in ctx.blocos:
            saida.append(ctx.blocos[mb.group(1)])
            i += 1
            continue
        if s.startswith("<"):
            bloco = []
            while i < n and linhas[i].strip():
                bloco.append(linhas[i])
                i += 1
            html_cru = "\n".join(bloco)
            html_cru = re.sub(r"\{\{(\w+)\}\}", lambda m: ctx.campo(m.group(1)), html_cru)
            saida.append(html_cru)
            continue
        if s.startswith(">"):
            bloco = []
            while i < n and linhas[i].strip().startswith(">"):
                bloco.append(linhas[i].strip()[1:].strip())
                i += 1
            saida.append(f"<blockquote><p>{inline(' '.join(bloco), ctx)}</p></blockquote>")
            continue
        mi = ITEM.match(linhas[i])
        if mi:
            ordenada = mi.group(2)[0].isdigit()
            itens = []
            while i < n:
                l = linhas[i]
                mi = ITEM.match(l)
                if mi and len(mi.group(1)) < 2:
                    itens.append([mi.group(3)])
                    i += 1
                elif l.strip() and itens and l.startswith((" ", "\t")):
                    itens[-1].append(l.strip())
                    i += 1
                elif not l.strip():
                    j = i
                    while j < n and not linhas[j].strip():
                        j += 1
                    if j < n and ITEM.match(linhas[j]) and len(ITEM.match(linhas[j]).group(1)) < 2:
                        i = j
                    else:
                        break
                else:
                    break
            tag = "ol" if ordenada else "ul"
            lis = "".join(f"<li>{inline(' '.join(it), ctx)}</li>" for it in itens)
            saida.append(f"<{tag}>{lis}</{tag}>")
            continue
        bloco = []
        while i < n and not comeca_bloco(linhas[i].strip()):
            bloco.append(linhas[i].strip())
            i += 1
        if not bloco:  # linha que parecia bloco mas não casou com nenhum
            bloco.append(linhas[i].strip())
            i += 1
        saida.append(f"<p>{inline(' '.join(bloco), ctx)}</p>")
    return "\n".join(saida)


# --------------------------------------------------------------------------
# Peças fixas
# --------------------------------------------------------------------------

FIGURA_LENTE = """<figure class="figura-lente">
<svg viewBox="0 0 480 330" role="img" aria-labelledby="fig-lente-tit">
<title id="fig-lente-tit">Cinco raios de luz paralelos atravessam uma lente convergente e se encontram no foco.</title>
<line class="eixo" x1="10" y1="165" x2="470" y2="165"/>
<path class="lente" d="M220 45 Q180 165 220 285 Q260 165 220 45 Z"/>
<g class="raios">
<path class="raio" d="M14 85 L208 85 L392 165"/>
<path class="raio" d="M14 125 L203 125 L392 165"/>
<path class="raio" d="M14 165 L392 165"/>
<path class="raio" d="M14 205 L203 205 L392 165"/>
<path class="raio" d="M14 245 L208 245 L392 165"/>
</g>
<g class="raio alem">
<path d="M392 165 L466 197"/><path d="M392 165 L466 182"/><path d="M392 165 L466 148"/><path d="M392 165 L466 133"/>
</g>
<circle class="foco" cx="392" cy="165" r="5.5"/>
<text class="rotulo-svg" x="384" y="146">F′</text>
<text class="rotulo-miudo" x="14" y="310">LUZ</text>
<text class="rotulo-miudo" x="196" y="310">LENTE</text>
<text class="rotulo-miudo" x="378" y="310">FOCO</text>
</svg>
<figcaption>Raios paralelos, uma lente convergente, um foco. É disso que o seu óculos é feito.</figcaption>
</figure>"""


def barra_e_cabecalho(pagina, paginas, ctx) -> str:
    pre = ctx.pre
    nav = "".join(
        f'<a href="{ctx.href(p["rota"])}"{" aria-current=\"page\"" if p["rota"] == pagina["rota"] else ""}>'
        f'{html.escape(p["menu"])}</a>'
        for p in paginas if p["rota"] not in ("/", "/agendar")
    )
    return f"""<a class="pular" href="#conteudo">Pular para o conteúdo</a>
<header class="barra">
  <div class="fila">
    <a id="btn-phi" class="ui-botao-barra ui-botao-barra--grego" href="#mapa"
       aria-label="Mapa do site" aria-haspopup="dialog" aria-expanded="false">Φ</a>
    <span class="espaco"></span>
    <button id="btn-menos" class="ui-botao-barra so-com-js" type="button" aria-label="Diminuir letra">A&minus;</button>
    <button id="btn-mais" class="ui-botao-barra so-com-js" type="button" aria-label="Aumentar letra">A+</button>
    <button id="btn-tema" class="ui-botao-barra so-com-js" type="button" aria-label="Tema e fonte"
            aria-haspopup="dialog" aria-expanded="false"><span aria-hidden="true">◐</span><span class="rotulo">Tema</span></button>
    <span class="espaco"></span>
    <button id="btn-xi" class="ui-botao-barra ui-botao-barra--grego so-com-js" type="button"
            aria-label="Sumário desta página" aria-haspopup="dialog" aria-expanded="false">Ξ</button>
  </div>
</header>
<div class="cabecalho">
  <div class="fila">
    <a class="marca" href="{ctx.href('/')}"><em>Ateliê</em> de Ótica</a>
    <nav class="nav-principal" aria-label="Principal">{nav}</nav>
    <a class="botao" href="{html.escape(ctx.href('whatsapp:agendar'))}">Agendar</a>
  </div>
</div>
<p id="aviso-corpo" class="pular" role="status" aria-live="polite" style="left:-999rem"></p>"""


def rodape(paginas, pagina, ctx, hoje) -> str:
    itens = "".join(
        f'<li><a href="{ctx.href(p["rota"])}"{" aria-current=\"page\"" if p["rota"] == pagina["rota"] else ""}>'
        f'{html.escape(p["menu"])}</a></li>' for p in paginas
    )
    neg = ctx.negocio
    return f"""<footer class="rodape">
  <div class="rodape-grade">
    <div>
      <a class="marca" href="{ctx.href('/')}"><em>Ateliê</em> de Ótica</a>
      <p>Ótica com hora marcada em {html.escape(neg['cidade'])}.<br>Critério no lugar da marca.</p>
    </div>
    <nav id="mapa" aria-label="Mapa do site">
      <h2 class="rodape-tit">O site</h2>
      <ul>{itens}</ul>
    </nav>
    <div>
      <h2 class="rodape-tit">Contato</h2>
      <p>{ctx.campo('whatsapp_legivel')}</p>
      <p>{ctx.campo('email')}</p>
      <p>{ctx.campo('endereco')}<br>{html.escape(neg['cidade'])}/{html.escape(neg['uf'])}</p>
      <p>{ctx.campo('instagram')}</p>
    </div>
  </div>
  <p class="colofao">Composto em Atkinson Hyperlegible e Cardo · nove temas de alto contraste ·
    letra ajustável em A− / A+ · <a href="{ctx.href('/acessibilidade')}">como este site foi feito</a> ·
    gerado em {hoje}</p>
</footer>"""


def paineis(paginas, pagina, ctx) -> str:
    mapa = "".join(
        f'<li><a href="{ctx.href(p["rota"])}"{" aria-current=\"page\"" if p["rota"] == pagina["rota"] else ""}>'
        f'{html.escape(p["menu"])}</a></li>' for p in paginas
    )
    temas = "".join(
        f'<button class="opcao" type="button" data-escolha-tema="{c}" aria-pressed="false">'
        f'<span class="amostra" data-theme="{c}" aria-hidden="true">Φ</span>'
        f'<span>{html.escape(nome)}' + (f'<span class="opcao-dica">{html.escape(d)}</span>' if d else "")
        + "</span></button>"
        for c, nome, d in TEMAS
    )
    fontes = "".join(
        f'<button class="opcao" type="button" data-escolha-fonte="{c}" aria-pressed="false">'
        f'<span class="amostra" style="font-family:{fam}" aria-hidden="true">Aa</span>'
        f'<span>{nome}<span class="opcao-dica">{dica}</span></span></button>'
        for c, nome, dica, fam in [
            ("atkinson", "Atkinson Hyperlegible", "padrão · letras que não se confundem", "'Atkinson Hyperlegible'"),
            ("cardo", "Cardo", "serifada, de livro", "'Cardo'"),
            ("opendyslexic", "OpenDyslexic", "base pesada, contra troca de b/d", "'OpenDyslexic'"),
        ]
    )

    def painel(ident, titulo, corpo):
        return (f'<dialog class="painel" id="{ident}" aria-labelledby="tit-{ident}">'
                f'<div class="painel-topo"><h2 id="tit-{ident}">{titulo}</h2>'
                f'<button class="ui-botao-barra" type="button" data-fechar aria-label="Fechar">✕</button></div>'
                f'<div class="painel-corpo">{corpo}</div></dialog>')

    return "\n".join([
        painel("painel-mapa", "Φ · Mapa do site", f'<ul class="painel-lista">{mapa}</ul>'),
        painel("painel-sumario", "Ξ · Nesta página", '<ul class="painel-lista" id="lista-sumario"></ul>'),
        painel("painel-tema", "Tema e fonte",
               f'<p class="painel-grupo">Cores</p><div class="opcoes">{temas}</div>'
               f'<p class="painel-grupo">Fonte do texto</p><div class="opcoes">{fontes}</div>'
               '<button class="botao-2" type="button" id="btn-restaurar">Restaurar o padrão</button>'),
    ])


def dados_estruturados(neg) -> str:
    d = {
        "@context": "https://schema.org",
        "@type": "Optician",
        "name": neg["nome"],
        "url": f"https://{neg['dominio']}/",
        "areaServed": f"{neg['cidade']}, {neg['uf']}",
        "description": "Ótica com hora marcada. Armações e lentes escolhidas por critério técnico, não por marca.",
    }
    if neg.get("whatsapp"):
        d["telephone"] = "+" + neg["whatsapp"]
    if neg.get("email"):
        d["email"] = neg["email"]
    if neg.get("instagram"):
        d["sameAs"] = [f"https://www.instagram.com/{neg['instagram'].lstrip('@')}/"]
    if neg.get("endereco"):
        d["address"] = {"@type": "PostalAddress", "streetAddress": rua(neg["endereco"]),
                        "addressLocality": neg["cidade"], "addressRegion": neg["uf"],
                        "postalCode": neg.get("cep", ""), "addressCountry": "BR"}
    return '<script type="application/ld+json">' + json.dumps(d, ensure_ascii=False) + "</script>"


CABECA_JS = ("(function(){var r=document.documentElement;r.classList.add('js');try{"
             "var t=localStorage.getItem('ao:tema');if(t)r.setAttribute('data-theme',t);"
             "var f=localStorage.getItem('ao:fonte');if(f)r.setAttribute('data-fonte',f);"
             "var e=localStorage.getItem('ao:escala');if(e)r.style.setProperty('--escala',e);"
             "}catch(x){}})();")


def montar_pagina(pagina, paginas, negocio, blocos, pendencias, hoje) -> str:
    ctx = Contexto(negocio, pagina, blocos, pendencias)
    corpo = md_para_html(pagina["corpo_md"], ctx)
    pre = ctx.pre
    titulo_aba = pagina.get("titulo_aba") or f'{pagina["titulo"]} · {negocio["nome"]}'
    canonica = f"https://{negocio['dominio']}{'/' if pagina['rota'] == '/' else pagina['rota'] + '/'}"
    desc = html.escape(pagina.get("descricao", ""))
    ld = dados_estruturados(negocio) if pagina["rota"] in ("/", "/contato") else ""
    return f"""<!doctype html>
<html lang="pt-BR" data-theme="sepia" data-fonte="atkinson">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(titulo_aba)}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonica}">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="{html.escape(negocio['nome'])}">
<meta property="og:title" content="{html.escape(titulo_aba)}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonica}">
<meta name="theme-color" content="#faf7f2">
<link rel="icon" href="{pre}icone.svg" type="image/svg+xml">
<link rel="preload" href="{pre}fontes/atkinson-hyperlegible-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{pre}fontes/cardo-regular.woff2" as="font" type="font/woff2" crossorigin>
<script>{CABECA_JS}</script>
<link rel="stylesheet" href="{pre}estilo.css">
{ld}
</head>
<body>
{barra_e_cabecalho(pagina, paginas, ctx)}
<main id="conteudo">
{corpo}
</main>
{rodape(paginas, pagina, ctx, hoje)}
{paineis(paginas, pagina, ctx)}
<script src="{pre}casca.js" defer></script>
</body>
</html>
"""


ICONE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="12" fill="#faf7f2"/>
<path d="M32 8 Q18 32 32 56 Q46 32 32 8 Z" fill="#6b3e15" fill-opacity=".12" stroke="#6b3e15" stroke-width="3"/>
<path d="M4 22 L29 22 L52 32 M4 42 L29 42 L52 32 M4 32 L52 32" fill="none" stroke="#6b3e15" stroke-width="2.4" stroke-linecap="round"/>
<circle cx="52" cy="32" r="3.5" fill="#6b3e15"/>
</svg>"""

PAGINA_404 = """---
titulo: Página não encontrada
rota: /404
menu: —
---

<p class="chapeu">Erro 404</p>

# Esta página não está aqui.

Talvez o endereço tenha mudado, ou tenha um erro de digitação. Mas o ateliê
continua no mesmo lugar.

::: botoes
[Voltar ao início](/){.botao}
[Agendar pelo WhatsApp](whatsapp:agendar){.botao-2}
:::
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--publicar", action="store_true",
                    help="falha se houver pendência em negocio.toml")
    ap.add_argument("--app-leitura", type=Path, default=APP_LEITURA,
                    help="onde está o app-leitura (de lá vêm os temas e as fontes)")
    args = ap.parse_args()

    global STYLES, FONTES_ORIGEM
    STYLES = args.app_leitura / "src" / "styles.css"
    FONTES_ORIGEM = args.app_leitura / "public" / "fonts"

    negocio = tomllib.loads((RAIZ / "negocio.toml").read_text(encoding="utf-8"))
    paginas = sorted((ler_pagina(p) for p in CONTEUDO.glob("*.md")), key=lambda p: p["ordem"])
    for p in paginas:
        for campo in ("titulo", "rota", "menu"):
            if campo not in p:
                sys.exit(f"ERRO: {p['arquivo']} sem '{campo}' no front matter.")

    temas = ler_temas()
    medicoes = medir_temas(temas)
    hoje = date.today().strftime("%d/%m/%Y")
    blocos = {"figura_lente": FIGURA_LENTE, "tabela_contraste": tabela_contraste(medicoes)}

    # Limpa o CONTEÚDO, não a pasta: no Windows um servidor de preview segurando
    # site/ faz o rmtree da própria pasta falhar, e gerar durante o preview é o
    # caso normal de trabalho.
    SAIDA.mkdir(exist_ok=True)
    for item in SAIDA.iterdir():
        shutil.rmtree(item) if item.is_dir() else item.unlink()
    copiar_fontes(SAIDA / "fontes")
    (SAIDA / "estilo.css").write_text(
        css_das_fontes() + "\n\n" + css_dos_temas(temas) + "\n\n"
        + (CASCA / "base.css").read_text(encoding="utf-8"), encoding="utf-8")
    shutil.copy2(CASCA / "casca.js", SAIDA / "casca.js")
    (SAIDA / "icone.svg").write_text(ICONE, encoding="utf-8")

    pendencias: dict[str, set] = {}
    ESPEC["data_geracao"] = hoje
    for p in paginas:
        destino = caminho_de_saida(p["rota"])
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(montar_pagina(p, paginas, negocio, blocos, pendencias, hoje), encoding="utf-8")

    p404 = interpretar_pagina(PAGINA_404, "404")
    (SAIDA / "404.html").write_text(montar_pagina(p404, paginas, negocio, blocos, {}, hoje), encoding="utf-8")

    dom = negocio["dominio"]
    (SAIDA / "CNAME").write_text(dom + "\n", encoding="utf-8")
    (SAIDA / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: https://{dom}/sitemap.xml\n", encoding="utf-8")
    urls = "".join(
        f"<url><loc>https://{dom}{'/' if p['rota'] == '/' else p['rota'] + '/'}</loc></url>" for p in paginas)
    (SAIDA / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n',
        encoding="utf-8")

    # ---- relatório ----
    print(f"Gerado: {len(paginas)} páginas + 404 em {SAIDA}")
    print("\nContraste (pior caso: visão típica + protanopia, deuteranopia, tritanopia):")
    print(f"  {'tema':<16}" + "".join(f"{r:>18}" for r, *_ in PARES))
    abaixo = 0
    for chave, _, medidas in medicoes:
        cel = []
        for _, r, meta in medidas:
            ok = r is not None and r >= meta
            abaixo += not ok
            cel.append(f"{fmt_razao(r):>12} {'ok' if ok else 'ABAIXO':>5}")
        print(f"  {chave:<16}" + "".join(cel))
    if abaixo:
        print(f"  → {abaixo} par(es) abaixo da meta — declarados em /acessibilidade.")

    if pendencias:
        print("\nPENDÊNCIAS (campos vazios em negocio.toml):")
        for campo, onde in sorted(pendencias.items()):
            print(f"  - {campo:<18} usado em: {', '.join(sorted(onde))}")
        if args.publicar:
            sys.exit("\n--publicar recusado: preencha o negocio.toml primeiro.")
    else:
        print("\nSem pendências.")


if __name__ == "__main__":
    main()
