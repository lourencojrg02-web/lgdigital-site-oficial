#!/usr/bin/env python3
"""
LGDigital — gerador do site estático.

    python3 build.py                 gera as páginas do site (para publicar)
    python3 build.py --standalone    gera também preview/*.html num ficheiro só

Fontes:
    src/<pagina>/*.html    secções, por ordem alfabética do nome
    src/_partials/*.html   pedaços partilhados, incluídos com "@include"
    assets/css/styles.css  folha de estilos partilhada
    assets/img/            imagens

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
PIXEL_ID = "878850018571511"

# ---------------------------------------------------------------- Meta Pixel
# Sai em todas as páginas. Para desativar, põe PIXEL_ID = "".
PIXEL = """<!-- Meta Pixel Code -->
<script>
!function(f,b,e,v,n,t,s)
{if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};
if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];
s.parentNode.insertBefore(t,s)}(window, document,'script',
'https://connect.facebook.net/en_US/fbevents.js');
fbq('init', '%s');
fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id=%s&ev=PageView&noscript=1"
/></noscript>
<!-- End Meta Pixel Code -->""" % (PIXEL_ID, PIXEL_ID)

# ------------------------------------------------------------------- Páginas
PAGES = [
    dict(out="index.html", src="home", base="", home="", body="tema-home",
         title="LGDigital — SEO local, Google Ads, Meta Ads e websites para negócios locais",
         desc="Agência de marketing digital para negócios locais em Portugal. SEO local no Google Maps, campanhas no Google e na Meta, e websites feitos para converter."),

    dict(out="hvac/index.html", src="hvac", base="../", home="../",
         title="LGDigital — Mais clientes para a tua empresa de AVAC. Só pagas por lead.",
         desc="Google Ads e Meta Ads para empresas de AVAC. Configuração gratuita, primeiras leads em 48 horas, 25€ por lead da Meta e 35€ por chamada do Google. Sem mensalidade, sem contrato."),

    dict(out="gbp/index.html", src="gbp", base="../", home="../", body="tema-gbp",
         title="LGDigital — Top 3 no Google em 90 dias, garantido.",
         desc="Colocamos o teu negócio local no top 3 do Google Maps em 90 dias. Garantido ou não pagas. Sem anúncios: posicionamento 100% orgânico."),

    dict(out="ads/index.html", src="ads", base="../", home="../", body="tema-home",
         title="LGDigital — Google Ads e Meta Ads para negócios locais",
         desc="Criamos e gerimos as tuas campanhas no Google e na Meta. Primeiras leads em 48 horas, chamadas rastreadas e contas em teu nome. Pagamento por lead ou avença."),

    dict(out="websites/index.html", src="websites", base="../", home="../", body="tema-home",
         title="LGDigital — Websites e landing pages que geram contactos",
         desc="Sites rápidos e landing pages feitas para converter visitas em chamadas e pedidos de orçamento. Prontos em 2 a 4 semanas, com medição incluída."),

    dict(out="hvac-obrigado/index.html", src="hvac-obrigado", base="../", home="../",
         title="Chamada marcada — LGDigital",
         desc="A tua chamada de qualificação está marcada.",
         noindex=True,
         # Conversão: dispara depois do PageView, quando o fbq já existe.
         head="<script>window.fbq && fbq('track', 'Schedule');</script>"),

    dict(out="404.html", src="404", base="/", home="/", body="tema-home", noindex=True,
         title="Página não encontrada — LGDigital",
         desc="A página que procuras não existe."),

    dict(out="pp/index.html", src="pp", base="../", home="../",
         title="Política de Privacidade — LGDigital",
         desc="Que dados pessoais a LGDigital recolhe, para que os usa, com quem os partilha e quais são os teus direitos."),

    dict(out="tc/index.html", src="tc", base="../", home="../",
         title="Termos e Condições — LGDigital",
         desc="Condições de utilização do site lgdigital.pt e da prestação dos serviços de gestão de campanhas Google Ads e Meta Ads."),
]

HEAD = """<!DOCTYPE html>
<html lang="pt-PT">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{robots}<link rel="canonical" href="{canonical}">
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
{pixel}
{extra}</head>
<body{bodyclass}>
"""
FOOT = "\n</body>\n</html>\n"

INCLUDE = re.compile(r"^[ \t]*@include[ \t]+(\S+)[ \t]*$", re.M)


def read(p):
    """Lê uma secção, resolvendo linhas '@include _partials/ficheiro.html'."""
    t = p.read_text(encoding="utf-8")
    return INCLUDE.sub(lambda m: (ROOT / "src" / m.group(1)).read_text(encoding="utf-8").strip(), t)


def has_content(t):
    return bool(re.sub(r"<!--.*?-->", "", t, flags=re.S).strip())


def sections(folder):
    return [p for p in sorted((ROOT / "src" / folder).glob("*.html")) if has_content(read(p))]


def render(folder, base, home):
    body = "\n\n".join(read(p).strip() for p in sections(folder))
    return body.replace("{{base}}", base).replace("{{home}}", home or "./")


def head_for(pg, styles, base):
    canonical = SITE + "/" + pg["out"].replace("index.html", "")
    extra = pg.get("head", "")
    return HEAD.format(
        title=pg["title"], desc=pg["desc"], canonical=canonical, site=SITE, base=base,
        robots='<meta name="robots" content="noindex, nofollow">\n' if pg.get("noindex") else "",
        styles=styles, pixel=PIXEL if PIXEL_ID else "",
        extra=(extra + "\n") if extra else "",
        bodyclass=(' class="%s"' % pg["body"]) if pg.get("body") else "")


def build_site():
    for pg in PAGES:
        styles = '<link rel="stylesheet" href="%sassets/css/styles.css">' % pg["base"]
        p = ROOT / pg["out"]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(head_for(pg, styles, pg["base"]) + render(pg["src"], pg["base"], pg["home"]) + FOOT,
                     encoding="utf-8")
        print("  %-24s %2d secções  %5.0f KB" % (pg["out"], len(sections(pg["src"])), p.stat().st_size / 1024))


def inline_data(path):
    f = ROOT / path
    mime = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
    return "data:%s;base64,%s" % (mime, base64.b64encode(f.read_bytes()).decode())


def build_standalone():
    """Um ficheiro só, com CSS e imagens embutidos. Para enviar ou pré-visualizar."""
    css = (ROOT / "assets/css/styles.css").read_text(encoding="utf-8")
    css = re.sub(r'url\("\.\./img/([^"]+)"\)',
                 lambda m: 'url("%s")' % inline_data("assets/img/" + m.group(1)), css)
    outdir = ROOT / "preview"; outdir.mkdir(exist_ok=True)
    for pg in PAGES:
        html = render(pg["src"], "", "#")
        html = re.sub(r'src="assets/img/([^"]+)"',
                      lambda m: 'src="%s"' % inline_data("assets/img/" + m.group(1)), html)
        html = re.sub(r'href="(hvac|pp|tc|hvac-obrigado)/"', 'href="#"', html)
        head = head_for(pg, "<style>\n%s\n</style>" % css, "")
        name = pg["src"] + ".html"
        (outdir / name).write_text(head + html + FOOT, encoding="utf-8")
        print("  preview/%-20s %5.0f KB" % (name, (outdir / name).stat().st_size / 1024))


if __name__ == "__main__":
    print("A gerar o site:")
    build_site()
    if "--standalone" in sys.argv:
        print("A gerar as versões num ficheiro só:")
        build_standalone()
