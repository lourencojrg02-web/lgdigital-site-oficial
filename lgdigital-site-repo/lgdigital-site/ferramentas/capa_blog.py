"""Gera a capa de um artigo do blog (como as da profresults.com/blog).

Uso:  python3 ferramentas/capa_blog.py <slug> "<título>"
Sai:  assets/img/blog/<slug>.jpg  (1440x1044, a mesma proporção das da Prof)

Fundo escuro com luz azul e, ao centro, um cartão branco com o símbolo da
LGDigital, o nome, o título e um traço vermelho de marcador por baixo.
Por baixo do cartão: lgdigital.pt. Sem fotos (pedido do Lourenço).

Sem pixelização: o fundo, o cartão, o texto e o traço são desenhados a 3x o
tamanho e reduzidos no fim (bordas suaves). Precisa da fonte Poppins (Medium e Bold)."""
import pathlib, sys, math
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
W, H = 1440, 1044                 # tamanho final
S = 3                             # super-amostragem do desenho
K = W / 1200 * S                  # medidas pensadas a 1200 px de largura
FONTES = [pathlib.Path("/usr/share/fonts/truetype/google-fonts"), pathlib.Path("C:/Windows/Fonts")]


def k(v):
    return int(round(v * K))


def fonte(nome, tamanho):
    for pasta in FONTES:
        if (pasta / nome).exists():
            return ImageFont.truetype(str(pasta / nome), tamanho)
    raise SystemExit("Falta a fonte %s" % nome)


def brilho(tam, centro, raio, cor, forca):
    """Luz suave (desenhada pequena e ampliada, sem degraus)."""
    f = 8
    w, h = tam[0] // f, tam[1] // f
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    cx, cy, r0 = centro[0] / f, centro[1] / f, raio / f
    for i in range(100, 0, -1):
        r = r0 * i / 100
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=int(forca * (1 - i / 100) ** 1.6 * 255))
    m = m.filter(ImageFilter.GaussianBlur(r0 / 8)).resize(tam, Image.BICUBIC)
    camada = Image.new("RGBA", tam, cor + (0,))
    camada.putalpha(m)
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


def traco(d, x0, x1, y, grossura, curva, cor):
    """Traço de marcador: mais grosso ao meio, fino nas pontas, ligeiramente curvo."""
    n = 120
    cima, baixo = [], []
    for j in range(n + 1):
        u = j / n
        x = x0 + (x1 - x0) * u
        yc = y - curva * math.sin(u * math.pi) + curva * .35 * u
        g = grossura * (0.25 + 0.75 * math.sin(u * math.pi) ** 0.45)
        cima.append((x, yc - g / 2)); baixo.append((x, yc + g / 2))
    d.polygon(cima + baixo[::-1], fill=cor)
    # pontas arredondadas
    for u in (0, 1):
        x = x0 + (x1 - x0) * u
        yc = y + curva * .35 * u
        r = grossura * 0.125
        d.ellipse((x - r, yc - r, x + r, yc + r), fill=cor)


def capa(slug, titulo):
    GW, GH = W * S, H * S
    fundo = Image.new("RGBA", (GW, GH), (16, 16, 18, 255))
    fundo.alpha_composite(brilho((GW, GH), (GW * .55, k(-120)), k(760), (78, 78, 82), .75))
    fundo.alpha_composite(brilho((GW, GH), (k(120), GH + k(60)), k(900), (39, 72, 220), 1.0))
    fundo.alpha_composite(brilho((GW, GH), (k(230), GH * .72), k(420), (55, 95, 245), .55))
    fundo.alpha_composite(brilho((GW, GH), (GW * .5, GH * .5), k(520), (45, 80, 230), .35))
    fundo.alpha_composite(brilho((GW, GH), (GW + k(80), GH * .55), k(520), (20, 20, 24), .6))

    fundo_final = fundo.resize((W, H), Image.LANCZOS)

    # camada do cartão (desenhada a 3x, por cima do fundo)
    fundo = Image.new("RGBA", (GW, GH), (0, 0, 0, 0))

    # cartão branco
    cx0, cx1 = k(210), k(990)
    pad = k(54)
    medir = ImageDraw.Draw(fundo)
    for max_linhas in (2, 3):     # título no maior tamanho que caiba em 2 linhas (ou 3)
        for t in range(k(84), k(40), -2 * S):
            tit_f = fonte("Poppins-Bold.ttf", t)
            linhas = quebra(medir, titulo, tit_f, (cx1 - cx0) - 2 * pad)
            if len(linhas) <= max_linhas:
                break
        if len(linhas) <= max_linhas:
            break
    alt_linha = int(tit_f.size * 1.14)
    altura = pad + k(64) + k(34) + alt_linha * len(linhas) + k(44) + pad
    cy0 = (GH - altura - k(70)) // 2          # cartão + "lgdigital.pt" ao centro
    cy1 = cy0 + altura
    sombra = Image.new("RGBA", (GW, GH), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).rounded_rectangle((cx0, cy0 + k(16), cx1, cy1 + k(16)), k(30), fill=(0, 0, 0, 120))
    fundo.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(k(24))))
    d = ImageDraw.Draw(fundo)
    d.rounded_rectangle((cx0, cy0, cx1, cy1), k(30), fill=(255, 255, 255, 255))

    # símbolo da LGDigital num círculo preto + nome
    ax, ay, av = cx0 + pad, cy0 + pad, k(64)
    d.ellipse((ax, ay, ax + av, ay + av), fill=(0, 0, 0, 255))
    simb = Image.open(ROOT / "assets/img/simbolo-claro.png").convert("RGBA")
    lado = k(36)
    simb = simb.resize((lado, int(simb.height * lado / simb.width)), Image.LANCZOS)
    fundo.alpha_composite(simb, (ax + av // 2 - simb.width // 2, ay + av // 2 - simb.height // 2))
    d.text((ax + av + k(16), ay + av // 2), "Lourenço Gaspar", font=fonte("Poppins-Medium.ttf", k(30)),
           fill=(17, 17, 17), anchor="lm")

    # título e traço vermelho por baixo do início da última linha
    ty = ay + av + k(34)
    for i, linha in enumerate(linhas):
        d.text((ax, ty + i * alt_linha), linha, font=tit_f, fill=(0, 0, 0), anchor="la")
    ult = linhas[-1]
    largura = d.textlength(ult, font=tit_f)
    base_y = ty + (len(linhas) - 1) * alt_linha + tit_f.getbbox(ult)[3] + k(18)
    x0 = ax - k(8)
    x1 = ax + max(k(170), min(largura * .55, k(320)))
    traco(d, x0, x1, base_y, k(9), k(4), (226, 30, 45, 255))
    traco(d, x0 + k(18), x1 - k(10), base_y + k(9), k(5), k(3), (226, 30, 45, 235))

    # site
    d.text(((cx0 + cx1) // 2, cy1 + k(58)), "lgdigital.pt", font=fonte("Poppins-Medium.ttf", k(26)),
           fill=(235, 235, 240), anchor="mm")

    # reduz a camada do cartão e põe-na por cima do fundo
    final = fundo_final
    final.alpha_composite(fundo.resize((W, H), Image.LANCZOS))

    destino = ROOT / "assets/img/blog" / (slug + ".jpg")
    destino.parent.mkdir(parents=True, exist_ok=True)
    final.convert("RGB").save(destino, quality=93, subsampling=0, optimize=True, progressive=True)
    print("capa:", destino.relative_to(ROOT), "(%d KB)" % (destino.stat().st_size // 1024))


if __name__ == "__main__":
    capa(sys.argv[1], sys.argv[2])
