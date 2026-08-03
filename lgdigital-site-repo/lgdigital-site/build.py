#!/usr/bin/env python3
"""
LGDigital — gerador do site estático.

    python3 build.py                 gera as páginas do site (para publicar)
    python3 build.py --standalone    gera também preview/*.html num ficheiro só

Fontes:
    src/<pagina>/*.html   secções, por ordem alfabética do nome
    assets/css/styles.css folha de estilos partilhada
    assets/img/           imagens

Nas secções usa-se {{base}} (raiz do site) e {{home}} (link para a página
inicial). O build substitui conforme a profundidade da página, para o site
funcionar tanto em lgdigital.pt como em qualquer subpasta.
Secções só com comentários são ignoradas.
"""
import pathlib, re, sys, base64, mimetypes

mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("image/svg+xml", ".svg")

ROOT = pathlib.Path(__file__).parent
SITE = "https://lgdigital.pt"

PAGES = [
    # saída,             pasta em src/, base,  título,                                  descrição
    ("index.html", "home", "", "",
     "LGDigital — Google Ads e Meta Ads para empresas de serviços",
     "Geramos chamadas e pedidos de orçamento para empresas de serviços através de Google Ads e Meta Ads. Só pagas por lead."),
    ("hvac/index.html", "hvac", "../", "../",
     "LGDigital — Mais clientes para a tua empresa de AVAC. Só pagas por lead.",
     "Google Ads e Meta Ads para empresas de AVAC. Configuração gratuita, primeiras leads em 48 horas, 25€ por lead da Meta e 35€ por chamada do Google. Sem mensalidade, sem contrato."),
]

HEAD = """<!DOCTYPE html>
<html lang="pt-PT">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="LGDigital">
<meta property="og:locale" content="pt_PT">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{site}/assets/img/logo.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#F5A623">
<link rel="icon" href="{base}favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="{base}assets/img/favicon-32.png">
<link rel="apple-touch-icon" href="{base}assets/img/apple-touch-icon.png">
<link rel="manifest" href="{base}site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;800;900&display=swap" rel="stylesheet">
{styles}
</head>
<body>
"""
FOOT = "\n</body>\n</html>\n"

def has_content(t):
    return bool(re.sub(r"<!--.*?-->", "", t, flags=re.S).strip())

def sections(folder):
    d = ROOT / "src" / folder
    return [p for p in sorted(d.glob("*.html")) if has_content(p.read_text(encoding="utf-8"))]

def render(folder, base, home):
    body = "\n\n".join(p.read_text(encoding="utf-8").strip() for p in sections(folder))
    return body.replace("{{base}}", base).replace("{{home}}", home or "./")

def inline_data(path):
    f = ROOT / path
    mime = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
    return "data:%s;base64,%s" % (mime, base64.b64encode(f.read_bytes()).decode())

def build_site():
    for out, folder, base, home, title, desc in PAGES:
        canonical = SITE + "/" + out.replace("index.html", "")
        head = HEAD.format(title=title, desc=desc, canonical=canonical, site=SITE, base=base,
                           styles='<link rel="stylesheet" href="%sassets/css/styles.css">' % base)
        p = ROOT / out
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(head + render(folder, base, home) + FOOT, encoding="utf-8")
        print("  %-18s %2d secções  %5.0f KB" % (out, len(sections(folder)), p.stat().st_size/1024))

def build_404():
    """Reaproveita a homepage. Como pode ser servida em qualquer caminho, usa
    caminhos absolutos a partir da raiz."""
    s = (ROOT/"index.html").read_text(encoding="utf-8")
    s = s.replace("<title>%s</title>" % PAGES[0][4], "<title>Página não encontrada — LGDigital</title>")
    s = s.replace("Geramos chamadas e pedidos de orçamento para empresas de serviços.</h1>",
                  "Esta página não existe.</h1>")
    s = s.replace("Estamos a preparar o site. Entretanto, podes ver como trabalhamos com\n      empresas de AVAC &mdash; ou falar connosco diretamente.",
                  "O link pode estar errado ou a página pode ter mudado de sítio.")
    s = s.replace('href="assets/', 'href="/assets/').replace('src="assets/', 'src="/assets/')
    s = s.replace('href="hvac/"', 'href="/hvac/"').replace('href="./"', 'href="/"')
    (ROOT/"404.html").write_text(s, encoding="utf-8")
    print("  %-18s" % "404.html")


def build_standalone():
    """Um ficheiro só, com CSS e imagens embutidos. Para enviar ou pré-visualizar."""
    css = (ROOT/"assets/css/styles.css").read_text(encoding="utf-8")
    css = re.sub(r'url\("\.\./img/([^"]+)"\)',
                 lambda m: 'url("%s")' % inline_data("assets/img/"+m.group(1)), css)
    outdir = ROOT/"preview"; outdir.mkdir(exist_ok=True)
    for out, folder, base, home, title, desc in PAGES:
        html = render(folder, "", "#")
        html = re.sub(r'src="assets/img/([^"]+)"',
                      lambda m: 'src="%s"' % inline_data("assets/img/"+m.group(1)), html)
        html = html.replace('href="hvac/"', 'href="#"')
        head = HEAD.format(title=title, desc=desc, canonical=SITE, site=SITE, base="",
                           styles="<style>\n%s\n</style>" % css)
        name = (folder or "index") + ".html"
        (outdir/name).write_text(head + html + FOOT, encoding="utf-8")
        print("  preview/%-14s %5.0f KB" % (name, (outdir/name).stat().st_size/1024))

if __name__ == "__main__":
    print("A gerar o site:")
    build_site()
    build_404()
    if "--standalone" in sys.argv:
        print("A gerar as versões num ficheiro só:")
        build_standalone()
