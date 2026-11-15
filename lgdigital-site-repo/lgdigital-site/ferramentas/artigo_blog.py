"""Transforma o texto de um artigo (como o Lourenço o escreve) na página do blog.

Uso:  python3 ferramentas/artigo_blog.py <slug> <ficheiro.txt>
O .txt: 1.ª linha = título; o resto = o texto, uma linha por parágrafo.
  - linhas começadas por "* " viram uma lista; "1. ", "2. "... uma lista numerada
    ("1) " fica como parágrafo normal);
  - [imagem: ficheiro.jpg | texto alternativo] mete uma imagem de assets/img/blog/;
  - links para lgdigital.pt passam a links internos;
  - "responde a este email" passa a link para o email do Lourenço.
Sai:  src/blog-<slug>/01-conteudo.html  (depois: capa, lista BLOG, sitemap, build)."""
import html, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
EMAIL = "lourenco@lgdigital.pt"


def links(t):
    t = re.sub(r"https?://(?:www\.)?lgdigital\.pt((?:/[^\s<]*)?)", troca_m, t)
    return t.replace("responde a este email", '<a href="mailto:%s">responde a este email</a>' % EMAIL)


def troca_m(m):
    bruto = m.group(1)
    fim = ""
    while bruto and bruto[-1] in ".,;:!?)":      # pontuação no fim da frase fica fora do link
        fim = bruto[-1] + fim; bruto = bruto[:-1]
    caminho = bruto.strip("/")
    href = "{{base}}" + (caminho + "/" if caminho else "")
    return '<a href="%s">https://lgdigital.pt/%s</a>%s' % (href, bruto.lstrip("/"), fim)


def gera(slug, titulo, linhas):
    corpo, lista, tipo = [], [], ["ul"]
    def fecha_lista():
        if lista:
            corpo.append('      <%s class="bl-lista">\n' % tipo[0] + "\n".join("        <li>%s</li>" % i for i in lista)
                         + "\n      </%s>" % tipo[0])
            lista.clear()
    for l in linhas:
        l = l.strip()
        if not l:
            continue
        m = re.match(r"\[imagem:\s*([^|\]]+?)\s*\|\s*([^\]]+?)\s*\]$", l)
        if m:
            fecha_lista()
            dim, classe = "", "bl-art-fig"
            f = ROOT / "assets/img/blog" / m.group(1)
            if f.exists():
                from PIL import Image
                larg, alt = Image.open(f).size
                dim = ' width="%d" height="%d"' % (larg, alt)
                if larg > alt:                     # imagem deitada (ex.: print de um site)
                    classe += " bl-art-fig--larga"
            corpo.append('      <figure class="%s"><img src="{{base}}assets/img/blog/%s"%s alt="%s" loading="lazy"></figure>'
                         % (classe, m.group(1), dim, html.escape(m.group(2))))
            continue
        num = re.match(r"\d+\.\s+(.*)", l)
        if l.startswith("* ") or num:
            novo = "ol" if num else "ul"
            if lista and tipo[0] != novo:
                fecha_lista()
            tipo[0] = novo
            lista.append(links(html.escape(num.group(1) if num else l[2:], quote=False)))
            continue
        fecha_lista()
        corpo.append("      <p>%s</p>" % links(html.escape(l, quote=False)))
    fecha_lista()
    t = html.escape(titulo)
    src = f'''<!-- ==================== /blog/{slug}/ ==================== -->
<!-- Artigo do blog, como os da profresults.com/blog: título, capa, texto numa
     coluna de 800px, redes sociais e o bloco "Grátis". Texto do Lourenço, tal
     como foi escrito (gerado com ferramentas/artigo_blog.py). -->
@include _partials/lp-cab-blog.html

<main class="lp" id="conteudo">
  <article class="lp-art bl-art">
    <h1 class="lp-art-h1">{t}</h1>
    <div class="bl-art-capa">
      <img src="{{{{base}}}}assets/img/blog/{slug}.jpg" width="1440" height="1044" alt="{t}: artigo de Lourenço Gaspar, da LGDigital">
    </div>

    <div class="lp-art-txt bl-art-txt">
{chr(10).join(corpo)}
    </div>
  </article>

@include _partials/lp-redes.html

@include _partials/lp-gratis.html

</main>

@include _partials/lp-rodape.html
'''
    d = ROOT / "src" / ("blog-" + slug)
    d.mkdir(exist_ok=True)
    (d / "01-conteudo.html").write_text(src, encoding="utf-8")
    print("artigo:", d.relative_to(ROOT) / "01-conteudo.html", "(%d parágrafos)" % src.count("<p>"))


if __name__ == "__main__":
    texto = pathlib.Path(sys.argv[2]).read_text(encoding="utf-8").splitlines()
    gera(sys.argv[1], texto[0].strip(), texto[1:])
