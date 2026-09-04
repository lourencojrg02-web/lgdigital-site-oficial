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
import pathlib, re, sys, base64, mimetypes, json

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
<noscript><img alt="" height="1" width="1" style="display:none"
src="https://www.facebook.com/tr?id=%s&ev=PageView&noscript=1"
/></noscript>
<!-- End Meta Pixel Code -->""" % (PIXEL_ID, PIXEL_ID)

# ------------------------------------------------------------------- Páginas
PAGES = [
    dict(out="index.html", src="home", base="", home="", body="tema-home", nome="Início",
         title="MELHOR Agência de Marketing Digital em Lisboa | LGDigital | Estás à procura de uma agência de marketing digital perto de mim para SEO, Google Ads ou Meta Ads? nós somos a solução certa",
         desc="Agência de marketing digital em Lisboa: SEO local, Google Ads, Meta Ads e websites para negócios locais. Mais chamadas e mais clientes, de forma previsível."),

    dict(out="hvac/index.html", src="hvac", nome="Google e Meta Ads para AVAC", base="../", home="../",
         title="Google e Meta Ads para empresas de AVAC | LGDigital",
         desc="Google Ads e Meta Ads para empresas de AVAC. Configuração gratuita, primeiras leads em 48 horas e uma taxa fixa por lead. Sem mensalidade e sem contrato."),

    dict(out="gbp/index.html", src="gbp", nome="Top 3 garantido", base="../", home="../", body="tema-gbp",
         title="Top 3 no Google em 90 dias, garantido | LGDigital",
         desc="Colocamos o teu negócio local no top 3 do Google Maps em 90 dias. Garantido ou não pagas. Sem anúncios: posicionamento 100% orgânico."),

    dict(out="seo/index.html", src="seo", nome="SEO Local", base="../", home="../", body="tema-home",
         title="SEO Local em Portugal — Top 3 no Google Maps | LGDigital",
         desc="Levamos o teu perfil de empresa ao top 3 do Google Maps na tua zona. Tráfego orgânico, sem custo por clique, com o mapa de posições medido todas as semanas."),

    dict(out="ads/index.html", src="ads", nome="Google & Meta Ads", base="../", home="../", body="tema-home",
         title="Google Ads e Meta Ads para negócios locais | LGDigital",
         desc="Criamos e gerimos as tuas campanhas no Google e na Meta. Primeiras leads em 48 horas, chamadas rastreadas e contas em teu nome. Pagamento por lead ou avença."),

    dict(out="websites/index.html", src="websites", nome="Websites", base="../", home="../", body="tema-home",
         title="Websites e landing pages que geram contactos | LGDigital",
         desc="Sites rápidos e landing pages feitas para converter visitas em chamadas e pedidos de orçamento. Prontos em 2 a 4 semanas, com medição incluída."),

    dict(out="hvac-obrigado/index.html", src="hvac-obrigado", base="../", home="../",
         title="Chamada marcada — LGDigital",
         desc="A tua chamada de qualificação está marcada.",
         noindex=True,
         # Conversão: dispara depois do PageView, quando o fbq já existe.
         head="<script>window.fbq && fbq('track', 'Schedule');</script>"),

    dict(out="contactos/index.html", src="contactos", nome="Contactos", base="../", home="../", body="tema-home",
         title="Contactos | LGDigital",
         desc="Fala connosco por WhatsApp, telefone ou marca uma chamada de 30 minutos no calendário."),

    dict(out="404.html", src="404", base="/", home="/", body="tema-home", noindex=True,
         title="Página não encontrada — LGDigital",
         desc="A página que procuras não existe."),

    dict(out="pp/index.html", src="pp", nome="Política de Privacidade", base="../", home="../",
         title="Política de Privacidade — LGDigital",
         desc="Que dados pessoais a LGDigital recolhe, para que os usa, com quem os partilha e quais são os teus direitos."),

    dict(out="tc/index.html", src="tc", nome="Termos e Condições", base="../", home="../",
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
<link rel="alternate" hreflang="pt-PT" href="{canonical}">
<link rel="alternate" hreflang="x-default" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="LGDigital">
<meta property="og:locale" content="pt_PT">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{site}/assets/img/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="LGDigital — marketing digital para negócios locais">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{site}/assets/img/og.png">
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
{jsonld}{extra}</head>
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


SOCIAIS = [
    "https://www.instagram.com/lgdigital.pt/",
    "https://www.facebook.com/profile.php?id=61586758513095",
    "https://www.linkedin.com/company/lgdigital1",
]


def _texto(html):
    """Tira tags e devolve texto limpo, para os dados estruturados."""
    t = re.sub(r"<[^>]+>", " ", html)
    t = (t.replace("&mdash;", "—").replace("&ldquo;", "“").replace("&rdquo;", "”")
          .replace("&euro;", "€").replace("&middot;", "·").replace("&hellip;", "…")
          .replace("&amp;", "&").replace("&nbsp;", " ").replace("&rarr;", "→")
          .replace("&darr;", "↓").replace("&larr;", "←").replace("&ndash;", "–"))
    return re.sub(r"\s+", " ", t).strip()


def jsonld_para(pg, body):
    """Organização na homepage, migalhas nas outras, FAQ onde houver <details>."""
    if pg.get("noindex"):
        return ""
    canonical = SITE + "/" + pg["out"].replace("index.html", "")
    blocos = []

    if pg["out"] == "index.html":
        blocos.append({
            "@context": "https://schema.org", "@type": "ProfessionalService",
            "@id": SITE + "/#organizacao", "name": "LGDigital",
            "url": SITE + "/", "logo": SITE + "/assets/img/logo.png",
            "image": SITE + "/assets/img/og.png",
            "description": pg["desc"],
            "telephone": "+351926289562",
            "priceRange": "€€",
            "areaServed": {"@type": "Country", "name": "Portugal"},
            "address": {"@type": "PostalAddress", "addressCountry": "PT",
                        "addressLocality": "Lisboa"},
            "sameAs": SOCIAIS,
            "knowsAbout": ["SEO local", "Google Business Profile", "Google Ads",
                           "Meta Ads", "Criação de websites"],
            "hasOfferCatalog": {
                "@type": "OfferCatalog", "name": "Serviços",
                "itemListElement": [
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "SEO Local",
                     "url": SITE + "/seo/"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Google Ads e Meta Ads",
                     "url": SITE + "/ads/"}},
                    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Criação de websites",
                     "url": SITE + "/websites/"}},
                ]},
        })
        blocos.append({"@context": "https://schema.org", "@type": "WebSite",
                       "@id": SITE + "/#site", "url": SITE + "/", "name": "LGDigital",
                       "inLanguage": "pt-PT",
                       "publisher": {"@id": SITE + "/#organizacao"}})
    else:
        blocos.append({
            "@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Início", "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": pg.get("nome", pg["title"]),
                 "item": canonical},
            ]})

    # só os <details> dentro de um bloco de FAQ; os menus do cabeçalho também
    # são <details> e não podem entrar aqui
    perguntas = []
    for m in re.finditer(r'<div class="(?:hm-faq|gbp-faq|faq)"[^>]*>', body):
        fim = body.find("</section>", m.end())
        zona = body[m.end(): fim if fim != -1 else len(body)]
        perguntas += re.findall(r"<details[^>]*>\s*<summary[^>]*>(.*?)</summary>(.*?)</details>",
                                zona, re.S)
    if perguntas:
        blocos.append({
            "@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": _texto(p),
                 "acceptedAnswer": {"@type": "Answer", "text": _texto(r)}}
                for p, r in perguntas]})

    if not blocos:
        return ""
    return "\n".join('<script type="application/ld+json">%s</script>'
                     % json.dumps(x, ensure_ascii=False, separators=(",", ":")) for x in blocos) + "\n"


def head_for(pg, styles, base, jsonld=""):
    canonical = SITE + "/" + pg["out"].replace("index.html", "")
    extra = pg.get("head", "")
    return HEAD.format(
        title=pg["title"], desc=pg["desc"], canonical=canonical, site=SITE, base=base,
        robots=('<meta name="robots" content="noindex, nofollow">\n' if pg.get("noindex")
                else '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1">\n'),
        styles=styles, pixel=PIXEL if PIXEL_ID else "",
        jsonld=jsonld,
        extra=(extra + "\n") if extra else "",
        bodyclass=(' class="%s"' % pg["body"]) if pg.get("body") else "")


def build_site():
    for pg in PAGES:
        styles = '<link rel="stylesheet" href="%sassets/css/styles.css">' % pg["base"]
        corpo = render(pg["src"], pg["base"], pg["home"])
        p = ROOT / pg["out"]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(head_for(pg, styles, pg["base"], jsonld_para(pg, corpo)) + corpo + FOOT,
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
