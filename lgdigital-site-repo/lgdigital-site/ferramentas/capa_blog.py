"""Gera a capa de um artigo do blog (como as da profresults.com/blog).

Uso:  python3 ferramentas/capa_blog.py <slug> "<título>"
Sai:  assets/img/blog/<slug>.jpg  (1200x870, a mesma proporção das da Prof)

Fundo escuro com luz azul, o Lourenço recortado à esquerda (ferramentas/
lourenco-recorte.png) e um cartão branco com o símbolo da LGDigital, o nome,
o título e um traço vermelho por baixo. Por baixo do cartão: lgdigital.pt.
Precisa da fonte Poppins (Medium e Bold) instalada."""
import pathlib, sys, math
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
W, H = 1200, 870
FONTES = [pathlib.Path("/usr/share/fonts/truetype/google-fonts"), pathlib.Path("C:/Windows/Fonts")]


def fonte(nome, tamanho):
    for pasta in FONTES:
        if (pasta / nome).exists():
            return ImageFont.truetype(str(pasta / nome), tamanho)
    raise SystemExit("Falta a fonte %s" % nome)


def brilho(tamanho, centro, raio, cor, forca):
    camada = Image.new("RGBA", tamanho, cor + (0,))
    mascara = Image.new("L", tamanho, 0)
    d = ImageDraw.Draw(mascara)
    cx, cy = centro
    for i in range(60, 0, -1):
        r = raio * i / 60
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=int(forca * (1 - i / 60) ** 1.6 * 255))
    camada.putalpha(mascara.filter(ImageFilter.GaussianBlur(raio / 12)))
    return camada


def quebra(draw, texto, f, largura):
    linhas, atual = [], ""
    for palavra in texto.split():
        tenta = (atual + " " + palavra).strip()
        if draw.textlength(tenta, font=f) <= largura or not atual:
            atual = tenta
        else:
            linhas.append(atual); atual = palavra
    linhas.append(atual)
    return linhas


def capa(slug, titulo):
    fundo = Image.new("RGBA", (W, H), (16, 16, 18, 255))
    fundo.alpha_composite(brilho((W, H), (W * .55, -120), 760, (78, 78, 82), .75))
    fundo.alpha_composite(brilho((W, H), (120, H + 60), 900, (39, 72, 220), 1.0))
    fundo.alpha_composite(brilho((W, H), (230, H * .72), 420, (55, 95, 245), .55))
    fundo.alpha_composite(brilho((W, H), (W + 80, H * .55), 520, (20, 20, 24), .6))

    # cartão branco
    cx0, cy0, cx1, cy1 = 488, 176, 1132, 0
    pad = 46
    nome_f, tit_f = fonte("Poppins-Medium.ttf", 30), None
    medir = ImageDraw.Draw(fundo)
    # título no maior tamanho que caiba em 2 linhas (ou 3, se for comprido)
    for max_linhas in (2, 3):
        for t in range(66, 38, -2):
            tit_f = fonte("Poppins-Bold.ttf", t)
            linhas = quebra(medir, titulo, tit_f, (1132 - 488) - 2 * pad)
            if len(linhas) <= max_linhas:
                break
        if len(linhas) <= max_linhas:
            break
    alt_linha = int(tit_f.size * 1.14)
    cy1 = cy0 + pad + 64 + 34 + alt_linha * len(linhas) + 44 + pad
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).rounded_rectangle((cx0, cy0 + 16, 1132, cy1 + 16), 30, fill=(0, 0, 0, 120))
    fundo.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(24)))
    d = ImageDraw.Draw(fundo)
    d.rounded_rectangle((cx0, cy0, 1132, cy1), 30, fill=(255, 255, 255, 255))

    # símbolo da LGDigital num círculo preto + nome
    ax, ay = cx0 + pad, cy0 + pad
    d.ellipse((ax, ay, ax + 64, ay + 64), fill=(0, 0, 0, 255))
    simb = Image.open(ROOT / "assets/img/simbolo-claro.png").convert("RGBA")
    simb.thumbnail((36, 36), Image.LANCZOS)
    fundo.alpha_composite(simb, (ax + 32 - simb.width // 2, ay + 32 - simb.height // 2))
    d.text((ax + 80, ay + 32), "Lourenço Gaspar", font=nome_f, fill=(17, 17, 17), anchor="lm")

    # título
    ty = ay + 64 + 34
    for i, linha in enumerate(linhas):
        d.text((ax, ty + i * alt_linha), linha, font=tit_f, fill=(0, 0, 0), anchor="la")
    # traço vermelho (à mão) por baixo do início da última linha
    ult = linhas[-1]
    largura = d.textlength(ult, font=tit_f)
    base_y = ty + (len(linhas) - 1) * alt_linha + tit_f.getbbox(ult)[3] + 16
    x0, x1 = ax - 10, ax + max(150, min(largura * .62, 330))
    for k, (dy, inc, esp) in enumerate([(0, -5, 6), (7, -3, 4), (3, -6, 3)]):
        pts = []
        for j in range(41):
            u = j / 40
            pts.append((x0 + (x1 - x0) * u + (k * 6), base_y + dy + inc * math.sin(u * math.pi) + 3 * u))
        d.line(pts, fill=(225, 29, 46, 255), width=esp, joint="curve")

    # o Lourenço, à esquerda, a sair do fundo
    eu = Image.open(pathlib.Path(__file__).parent / "lourenco-recorte.png").convert("RGBA")
    alt = 660
    eu = eu.resize((int(eu.width * alt / eu.height), alt), Image.LANCZOS)
    fundo.alpha_composite(eu, (-70, H - alt))

    # site
    d = ImageDraw.Draw(fundo)
    d.text((cx0 + pad + 120, cy1 + 58), "lgdigital.pt", font=fonte("Poppins-Medium.ttf", 24),
           fill=(235, 235, 240), anchor="lm")

    destino = ROOT / "assets/img/blog" / (slug + ".jpg")
    destino.parent.mkdir(parents=True, exist_ok=True)
    fundo.convert("RGB").save(destino, quality=86, optimize=True, progressive=True)
    print("capa:", destino.relative_to(ROOT), "(%d KB)" % (destino.stat().st_size // 1024))


if __name__ == "__main__":
    capa(sys.argv[1], sys.argv[2])
