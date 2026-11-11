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
import pathlib, re, sys, base64, mimetypes, json, hashlib

mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("image/svg+xml", ".svg")

ROOT = pathlib.Path(__file__).parent
SITE = "https://lgdigital.pt"
PIXEL_ID = "1705934707134389"

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

SOCIAIS = [
    "https://www.instagram.com/lgdigital.pt/",
    "https://www.facebook.com/profile.php?id=61586758513095",
    "https://www.linkedin.com/company/lgdigital1",
]

# ----------------------------------------------------------------- Artigos
AUTOR = {"@type": "Person", "name": "Lourenço Gaspar",
         "@id": SITE + "/lourenco-gaspar/#pessoa",
         "url": SITE + "/lourenco-gaspar/",
         "sameAs": ["https://www.youtube.com/@lourencorg",
                    "https://x.com/lourenco_rg",
                    "https://www.linkedin.com/in/louren%C3%A7o-gaspar-785353308/"]}
EDITOR = {"@type": "Organization", "name": "LGDigital", "@id": SITE + "/#organizacao",
          "logo": {"@type": "ImageObject", "url": SITE + "/assets/img/logo.png"}}


def artigo_ld(caminho, titulo, descricao, data):
    """JSON-LD Article para um artigo ou caso de estudo."""
    return '<script type="application/ld+json">%s</script>' % json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": titulo, "description": descricao,
        "datePublished": data, "dateModified": data, "inLanguage": "pt-PT",
        "image": SITE + "/assets/img/og.png",
        "mainEntityOfPage": SITE + "/" + caminho,
        "author": AUTOR, "publisher": EDITOR,
    }, ensure_ascii=False, separators=(",", ":"))


# Página pessoal /lourenco-gaspar/ (como a profresults.com/arno-wingen):
# dados Person para o Google ligar o nome às redes e à LGDigital.
# Person schema do Lourenço (quem é, o que faz e onde): vai na página pessoal
# (dentro de ProfilePage), na página "especialista de SEO" e na página inicial.
PESSOA = {
    "@type": "Person", "@id": SITE + "/lourenco-gaspar/#pessoa",
    "name": "Lourenço Gaspar", "url": SITE + "/lourenco-gaspar/",
    "image": SITE + "/assets/img/especialista-de-seo-mais-dedicado-lisboa.jpg",
    "jobTitle": ["Especialista de SEO", "Fundador da LGDigital"],
    "description": "Lourenço Gaspar é especialista de SEO e fundador da LGDigital, uma agência de marketing "
                   "digital em Lisboa que ajuda empresas de serviços e negócios locais a conseguir mais clientes.",
    "address": {"@type": "PostalAddress", "addressLocality": "Lisboa", "addressCountry": "PT"},
    "worksFor": {"@id": SITE + "/#organizacao"},
    "knowsAbout": ["SEO", "SEO Local", "Google Ads", "Meta Ads", "AI SEO", "Geração de leads"],
    "sameAs": AUTOR["sameAs"],
}
PESSOA_LD = '<script type="application/ld+json">%s</script>' % json.dumps(
    {"@context": "https://schema.org", "@type": "ProfilePage", "mainEntity": PESSOA},
    ensure_ascii=False, separators=(",", ":"))
PESSOA_SO_LD = '<script type="application/ld+json">%s</script>' % json.dumps(
    dict({"@context": "https://schema.org"}, **PESSOA), ensure_ascii=False, separators=(",", ":"))



# A antiga inicial vive em /landing-page/. Links antigos para as suas secções
# (emails, bios, anúncios: lgdigital.pt/#agendar) seguem para lá, com os
# utm_ do link, antes de a página nova aparecer.
ANCORAS_ANTIGAS = """<script>(function(){var h=location.hash.slice(1);
if(['agendar','calculadora','calc','comparacao','resultados','faq','beneficios','processo','para-quem','transparencia','painel'].indexOf(h)>-1)
location.replace('/landing-page/'+location.search+'#'+h);})();</script>"""

# ------------------------------------------------------------------- Páginas
# Landing de captação (/landing-page): Inter, como a profresults.com
FONTES_INTER = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">"""
# /gbp/: como a profresults.com/gbp, com Poppins e Cormorant Garamond em itálico
FONTES_GBP = FONTES_INTER.replace(
    "family=Inter:wght@400;500;600;700",
    "family=Inter:wght@400;500;600;700&family=Poppins:wght@400;500;600;700"
    "&family=Cormorant+Garamond:ital,wght@1,700&family=Source+Serif+4:ital,wght@1,500")
# /obrigado/: Inter + Source Serif 4 em itálico (a parte em serifa do título)
FONTES_INTER_SERIF = FONTES_INTER.replace(
    "family=Inter:wght@400;500;600;700", "family=Inter:wght@400;500;600;700&family=Source+Serif+4:ital,wght@1,500")

PAGES = [
    # Antiga página inicial (anúncios + chamada). Vive em /landing-page/ desde
    # 06/11/2026 (com uma volta à raiz entre 09/11 e 11/11). A inicial é a
    # página de captação de emails ao estilo da Prof Results.
    # home="" porque as âncoras (#agendar, #calculadora...) são desta página.
    dict(out="landing-page/index.html", src="home", base="../", home="", body="tema-home",
         nome="Pedidos de orçamento qualificados",
         title="LGDigital | Pedidos de orçamento qualificados para empresas de serviços",
         desc="Montamos e gerimos anúncios para empresas de serviços. Pedidos de orçamento qualificados diretamente no teu telemóvel, sem fidelização."),

    dict(out="casos-estudo/index.html", src="casos-estudo", nome="Casos de estudo",
         base="../", home="../landing-page/", body="tema-home",
         title="Casos de estudo | LGDigital",
         desc="Casos de estudo das nossas campanhas de anúncios: 74.100 € em contratos fechados a partir de 2.906 € investidos, 24 leads e 3 clientes. Só números medidos."),

    dict(out="artigos/index.html", src="artigos", nome="Artigos",
         base="../", home="../landing-page/", body="tema-home",
         title="Artigos | LGDigital",
         desc="Artigos da LGDigital sobre anúncios e aquisição de clientes para empresas de serviços, com números de campanhas reais."),

    dict(out="artigos/anuncios-online/index.html", src="artigo-anuncios-online",
         nome="Tudo o que precisas de saber sobre anúncios online",
         pai=("Artigos", "artigos/"),
         base="../../", home="../../landing-page/", body="tema-home",
         title="Tudo o que precisas de saber sobre anúncios online | LGDigital",
         desc="Como funcionam os anúncios online, quanto investir, o que medir e os erros mais comuns. Um guia sem jargão para empresas de serviços.",
         head=artigo_ld("artigos/anuncios-online/",
                        "Tudo o que precisas de saber sobre anúncios online",
                        "Como funcionam os anúncios online, quanto investir, o que medir e os erros mais comuns.",
                        "2026-10-20")),

    dict(out="artigos/conseguir-mais-clientes-empresa-servicos/index.html", src="artigo-mais-clientes",
         nome="Como conseguir mais clientes numa empresa de serviços",
         pai=("Artigos", "artigos/"),
         base="../../", home="../../landing-page/", body="tema-home",
         title="Como conseguir mais clientes numa empresa de serviços | LGDigital",
         desc="Antes de pagar por mais pedidos, vê quantos já perdes. Guia para empresas de serviços: Google, recomendações, anúncios e por onde começar.",
         head=artigo_ld("artigos/conseguir-mais-clientes-empresa-servicos/",
                        "Como conseguir mais clientes numa empresa de serviços (e por onde começar)",
                        "Antes de pagar por mais pedidos, vê quantos já perdes. Guia para empresas de serviços: Google, recomendações, anúncios e por onde começar.",
                        "2026-10-27")),

    # Casos de estudo: uma página por cliente, dentro de /casos-estudo/
    dict(out="casos-estudo/ortofirst/index.html", src="caso-ortofirst",
         nome="OrtoFirst", pai=("Casos de estudo", "casos-estudo/"),
         base="../../", home="../../landing-page/", body="tema-home",
         title="Caso de estudo OrtoFirst: 74.100 € em contratos com 2.906 € em anúncios | LGDigital",
         desc="Como a OrtoFirst transformou 2.906,75 € em anúncios em 74.100 € em contratos fechados: 24 leads, 3 clientes e 25,5x de retorno em valor contratual.",
         head=artigo_ld("casos-estudo/ortofirst/",
                        "Como a OrtoFirst transformou 2.906 € em anúncios em 74.100 € em contratos fechados",
                        "2.906,75 € investidos em Meta Ads, 24 leads, 3 clientes e 74.100 € em contratos fechados.",
                        "2026-10-20")),

    # Página inicial: captação de emails (isca: vídeo com 3 dicas), copiada da
    # profresults.com. Tem folha e letra próprias.
    dict(out="index.html", src="landing-page", base="", home="landing-page/",
         body="tema-landing", css="landing.css", fontes=FONTES_INTER, cor="#EFEBE5",
         nome="Início", head=ANCORAS_ANTIGAS + "\n" + PESSOA_SO_LD,
         title="MELHOR Agência de Marketing em Lisboa | LGDigital | Estás à procura de uma agência de marketing digital para Meta Ads, Google Ads ou SEO local? Pomos a tua empresa no topo do Google",
         desc="A LGDigital é uma agência de marketing digital que se torna o teu departamento de marketing, sempre que precisares."),

    # SEO Local / top 3 no Google Maps (como a profresults.com/gbp). Abre a
    # partir do botão da /obrigado/.
    dict(out="gbp/index.html", src="gbp", base="../", home="../landing-page/",
         body="tema-landing", noindex=True, css="landing.css", fontes=FONTES_GBP, cor="#EFEBE5",
         nome="Top 3 no Google Maps", title="LGDigital | Agência de Marketing Digital em Lisboa",
         desc="A LGDigital é uma agência de marketing digital que se torna o teu departamento de marketing, sempre que precisares."),

    # Vídeo grátis das 3 dicas (como a profresults.com/gbp-three-free). É o
    # link do email que o Make envia a quem se inscreve.
    dict(out="3-dicas/index.html", src="3-dicas", base="../", home="../landing-page/",
         body="tema-landing", noindex=True, css="landing.css", fontes=FONTES_INTER_SERIF, cor="#EFEBE5",
         nome="O Teu Vídeo", title="LGDigital | Agência de Marketing Digital em Lisboa",
         desc="A LGDigital é uma agência de marketing digital que se torna o teu departamento de marketing, sempre que precisares."),

    # Página local de Lisboa (como a profresults.com/amsterdam): é o site do
    # Perfil da Empresa no Google, por isso fica no Google e no sitemap.
    dict(out="lisboa/index.html", src="lisboa", base="../", home="../landing-page/",
         body="tema-landing", css="landing.css", fontes=FONTES_GBP, cor="#EFEBE5",
         nome="Lisboa",
         title="MELHOR Agência de Marketing em Lisboa - à procura de uma agência de marketing digital perto de ti para SEO, SEO local, Google Ads ou Meta Ads? A LGDigital põe a tua empresa no topo do Google",
         desc="A LGDigital é uma agência de marketing digital em Lisboa: SEO, SEO local, Google Ads, Meta Ads e AI SEO. Feito por nós, sem fidelização."),

    # Página-prova de SEO (como a profresults.com/hardest-working-seo-expert-amsterdam)
    dict(out="especialista-de-seo-mais-dedicado-lisboa/index.html", src="especialista-seo-lisboa",
         base="../", home="../landing-page/",
         body="tema-landing", css="landing.css", fontes=FONTES_INTER, cor="#EFEBE5",
         nome="O especialista de SEO mais dedicado em Lisboa",
         title="O especialista de SEO mais dedicado em Lisboa | Lourenço Gaspar",
         desc="Lourenço Gaspar foi apelidado de “o especialista de SEO mais dedicado em Lisboa”. Aqui está a prova.",
         head=PESSOA_SO_LD + "\n" + artigo_ld("especialista-de-seo-mais-dedicado-lisboa/",
                        "O especialista de SEO mais dedicado em Lisboa",
                        "Lourenço Gaspar foi apelidado de “o especialista de SEO mais dedicado em Lisboa”. Aqui está a prova.",
                        "2026-11-11")),

    # Agradecimento depois de deixar o email (como a profresults.com/main-ty)
    dict(out="obrigado/index.html", src="obrigado", base="../", home="../landing-page/",
         body="tema-landing", noindex=True, css="landing.css", fontes=FONTES_INTER_SERIF, cor="#EFEBE5",
         nome="Obrigado", title="LGDigital | Agência de Marketing Digital em Lisboa",
         desc="A LGDigital é uma agência de marketing digital que se torna o teu departamento de marketing, sempre que precisares."),

    # Página pessoal (abre a partir do cartão da equipa na /landing-page).
    # Fica no Google: serve para quem pesquisa o nome do Lourenço.
    dict(out="lourenco-gaspar/index.html", src="lourenco-gaspar", base="../", home="../landing-page/",
         body="tema-landing", css="landing.css", fontes=FONTES_INTER, cor="#EFEBE5",
         nome="Lourenço Gaspar", head=PESSOA_LD,
         title="Lourenço Gaspar | Fundador da LGDigital, Agência de Marketing Digital em Lisboa",
         desc="Lourenço Gaspar é o fundador da LGDigital, uma agência de marketing digital em Lisboa. Ajuda empresas de serviços e negócios locais a conseguir mais clientes com Google Ads, Meta Ads e SEO."),

    # Páginas de serviço ligadas a partir da /landing-page (estilo profresults.com)
    dict(out="servicos/google-ads/index.html", src="servico-google-ads", base="../../", home="../../landing-page/",
         body="tema-landing", noindex=True, css="landing.css", fontes=FONTES_INTER, cor="#EFEBE5",
         nome="Google Ads", title="MELHOR Agência de Google Ads em Lisboa - se procuras gestão de Google Ads perto de mim - a LGDigital cria anúncios que te trazem clientes",
         desc="Google Ads que te trazem clientes. A LGDigital, agência de marketing em Lisboa, trata de tudo por ti. A partir de 1.000 € por mês."),
    dict(out="servicos/meta-ads/index.html", src="servico-meta-ads", base="../../", home="../../landing-page/",
         body="tema-landing", noindex=True, css="landing.css", fontes=FONTES_INTER, cor="#EFEBE5",
         nome="Meta Ads", title="MELHOR Agência de Meta Ads em Lisboa - se procuras gestão de Meta Ads perto de mim - a LGDigital cria anúncios no Facebook e no Instagram que te trazem clientes",
         desc="Anúncios no Facebook e no Instagram que te trazem clientes. Feito por nós. Sem fidelização. A partir de 1.000 € por mês."),
    dict(out="servicos/seo/index.html", src="servico-seo", base="../../", home="../../landing-page/",
         body="tema-landing", noindex=True, css="landing.css", fontes=FONTES_INTER, cor="#EFEBE5",
         nome="SEO", title="MELHOR Agência de SEO em Lisboa - se procuras SEO perto de mim - a LGDigital põe a tua empresa no Google sem pagares por cada clique",
         desc="Aparece no Google sem pagar por cada clique. SEO feito por nós. Sem fidelização."),
    dict(out="servicos/seo-local/index.html", src="servico-seo-local", base="../../", home="../../landing-page/",
         body="tema-landing", noindex=True, css="landing.css", fontes=FONTES_INTER, cor="#EFEBE5",
         nome="SEO Local", title="MELHOR Agência de SEO Local em Lisboa - se procuras SEO local ou subir no Google Maps perto de mim - a LGDigital põe a tua empresa no top 3 do Google Maps",
         desc="Quando alguém na tua zona procura aquilo que tu fazes, deve encontrar-te a ti. SEO local feito pela LGDigital, em Lisboa. Sem fidelização."),
    dict(out="servicos/ai-seo/index.html", src="servico-ai-seo", base="../../", home="../../landing-page/",
         body="tema-landing", noindex=True, css="landing.css", fontes=FONTES_INTER, cor="#EFEBE5",
         nome="AI SEO", title="MELHOR Agência de AI SEO em Lisboa - se procuras AI SEO perto de mim - a LGDigital põe a tua empresa nas respostas do ChatGPT",
         desc="Os teus clientes já perguntam ao ChatGPT. Ele fala de ti? AI SEO feito por nós. Sem fidelização."),

    # Landings de campanha Meta: tráfego pago, fora do índice do Google
    dict(out="meta/index.html", src="meta", base="../", home="../landing-page/", body="tema-meta", noindex=True,
         title="Top 3 no Google em 90 dias, garantido | LGDigital",
         desc="Colocamos negócios locais de serviços no top 3 do Google Maps em 90 dias. Se não chegarmos lá, pagamos-te 500€. Vê se a tua empresa se qualifica."),

    dict(out="meta-book-a-call/index.html", src="meta-book-a-call", base="../", home="../landing-page/",
         body="tema-meta", noindex=True,
         title="Marca a tua chamada | LGDigital",
         desc="Recebemos o teu pedido. Escolhe uma hora para falarmos.",
         # Única conversão do site. Dispara a seguir ao PageView, já com o fbq definido.
         head="<script>window.fbq && fbq('track', 'Lead');</script>"),

    # Mesma página, para quem vem do Instant Form do Meta. Sem `head`, de
    # propósito: esse tráfego já foi contado como lead pelo próprio Meta,
    # e disparar o evento outra vez duplicava a conversão.
    dict(out="instant-form-book-a-call/index.html", src="instant-form-book-a-call",
         base="../", home="../landing-page/", body="tema-meta", noindex=True,
         title="Marca a tua chamada | LGDigital",
         desc="Recebemos o teu pedido. Escolhe uma hora para falarmos."),

    dict(out="404.html", src="404", base="/", home="/landing-page/", body="tema-home", noindex=True,
         title="Página não encontrada — LGDigital",
         desc="A página que procuras não existe."),

    dict(out="pp/index.html", src="pp", nome="Política de Privacidade", base="../", home="../landing-page/",
         body="tema-home",
         title="Política de Privacidade — LGDigital",
         desc="Que dados pessoais a LGDigital recolhe, para que os usa, com quem os partilha e quais são os teus direitos."),

    dict(out="tc/index.html", src="tc", nome="Termos e Condições", base="../", home="../landing-page/",
         body="tema-home",
         title="Termos e Condições — LGDigital",
         desc="Condições de utilização do site lgdigital.pt e da prestação dos serviços da LGDigital."),
]

# ---------------------------------------------------------------- Lisboa
# Páginas locais à volta da /lisboa/ (como a profresults.com/amsterdam):
# uma por concelho (/lisboa/<zona>/) e uma por serviço (/lisboa/<serviço>/).
# Todas ficam no Google e no sitemap, com "Lisboa" como página-mãe.
# (endereço, nome, "em" e "de" com o artigo certo: na Amadora, no Seixal)
ZONAS_LISBOA = [("oeiras", "Oeiras", "em", "de"), ("cascais", "Cascais", "em", "de"),
                ("sintra", "Sintra", "em", "de"), ("amadora", "Amadora", "na", "da"),
                ("loures", "Loures", "em", "de"), ("odivelas", "Odivelas", "em", "de"),
                ("almada", "Almada", "em", "de"), ("seixal", "Seixal", "no", "do")]
for _slug, _nome, _em, _de in ZONAS_LISBOA:
    PAGES.append(dict(
        out="lisboa/%s/index.html" % _slug, src="lisboa-" + _slug, base="../../", home="../../landing-page/",
        body="tema-landing", css="landing.css", fontes=FONTES_GBP, cor="#EFEBE5",
        nome=_nome, pai=("Lisboa", "lisboa/"),
        title="MELHOR Agência de Marketing Digital %s %s - à procura de uma agência de marketing perto de ti para SEO, SEO local, Google Ads ou Meta Ads? A LGDigital põe a tua empresa no topo do Google" % (_em, _nome),
        desc="A LGDigital é uma agência de marketing digital para empresas %s %s: SEO, SEO local, Google Ads, Meta Ads e AI SEO. Feito por nós, sem fidelização." % (_de, _nome)))

SERVICOS_LISBOA = [
    ("google-ads", "Google Ads em Lisboa",
     "MELHOR Agência de Google Ads em Lisboa - se procuras gestão de Google Ads em Lisboa - a LGDigital cria anúncios que te trazem clientes",
     "Google Ads em Lisboa: anúncios no Google que te trazem clientes. Feito por nós, sem fidelização. A partir de 1.000 € por mês."),
    ("meta-ads", "Meta Ads em Lisboa",
     "MELHOR Agência de Meta Ads em Lisboa - se procuras gestão de Meta Ads em Lisboa - a LGDigital cria anúncios no Facebook e no Instagram que te trazem clientes",
     "Meta Ads em Lisboa: anúncios no Facebook e no Instagram que te trazem clientes. Feito por nós, sem fidelização. A partir de 1.000 € por mês."),
    ("seo", "SEO em Lisboa",
     "MELHOR Agência de SEO em Lisboa - se procuras uma empresa de SEO em Lisboa - a LGDigital põe a tua empresa no Google sem pagares por cada clique",
     "SEO em Lisboa: aparece no Google sem pagar por cada clique. Feito por nós, sem fidelização."),
    ("seo-local", "SEO Local em Lisboa",
     "MELHOR Agência de SEO Local em Lisboa - se procuras SEO local ou subir no Google Maps em Lisboa - a LGDigital põe a tua empresa no top 3 do Google Maps",
     "SEO local em Lisboa: quando alguém na tua zona procura aquilo que tu fazes, deve encontrar-te a ti. Feito por nós, sem fidelização."),
    ("ai-seo", "AI SEO em Lisboa",
     "MELHOR Agência de AI SEO em Lisboa - se procuras AI SEO em Lisboa - a LGDigital põe a tua empresa nas respostas do ChatGPT",
     "AI SEO em Lisboa: os teus clientes já perguntam ao ChatGPT. Ele fala de ti? Feito por nós, sem fidelização."),
]
for _slug, _nome, _title, _desc in SERVICOS_LISBOA:
    PAGES.append(dict(
        out="lisboa/%s/index.html" % _slug, src="lisboa-servico-" + _slug, base="../../", home="../../landing-page/",
        body="tema-landing", css="landing.css", fontes=FONTES_INTER, cor="#EFEBE5",
        nome=_nome, pai=("Lisboa", "lisboa/"), title=_title, desc=_desc))

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
<meta property="og:image:alt" content="LGDigital — anúncios que trazem clientes">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{site}/assets/img/og.png">
<meta name="theme-color" content="{tema_cor}">
<link rel="icon" href="{base}favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="{base}assets/img/favicon-32.png">
<link rel="apple-touch-icon" href="{base}assets/img/apple-touch-icon.png">
<link rel="manifest" href="{base}site.webmanifest">
{fontes}
{styles}
{pixel}
{jsonld}{extra}</head>
<body{bodyclass}>
"""
# ---------------------------------------------------------- Redirecionamentos
# Páginas que existiram e foram apagadas. Cada caminho fica com uma página
# mínima que reencaminha para o destino: assim anúncios antigos, favoritos e
# resultados do Google não dão erro 404. O GitHub Pages não faz
# redirecionamentos de servidor, por isso usa-se meta refresh + canonical
# (o Google trata um refresh imediato como um redirecionamento).
REDIRECIONAR = {
    "seo/": "",
    "websites/": "",
    "melhor-web-designer-lisboa/": "",
    "hvac/": "",
    "hvac-obrigado/": "",
    "contactos/": "landing-page/#agendar",
    # 09/11 a 11/11/2026 as páginas ao estilo da Prof Results estiveram em /ads/
    "ads/": "",
    "ads/obrigado/": "obrigado/",
    "ads/3-dicas/": "3-dicas/",
    "ads/gbp/": "gbp/",
    "ads/servicos/google-ads/": "servicos/google-ads/",
    "ads/servicos/meta-ads/": "servicos/meta-ads/",
    "ads/servicos/seo/": "servicos/seo/",
    "ads/servicos/seo-local/": "servicos/seo-local/",
    "ads/servicos/ai-seo/": "servicos/ai-seo/",
    # o caso da OrtoFirst esteve uns dias publicado como artigo
    "artigos/anuncios-74100-euros-faturados/": "casos-estudo/ortofirst/",
}

REDIRECT = """<!DOCTYPE html>
<html lang="pt-PT">
<head>
<meta charset="utf-8">
<title>LGDigital</title>
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="{absoluto}">
<meta http-equiv="refresh" content="0; url={relativo}">
<script>var d={relativo_js};if(d.indexOf("#")<0)d+=location.search+location.hash;location.replace(d);</script>
</head>
<body>
<p>Esta página mudou. <a href="{relativo}">Continua para a LGDigital</a>.</p>
</body>
</html>
"""


# ------------------------------------------------------------------- Fontes
# Site principal (tema-home): Cal Sans + Cal Sans UI, alojadas em assets/fonts
# (licença OFL, ver os .txt na mesma pasta). Não passam pelo Google: nenhum
# IP de visitante vai para terceiros só por carregar a página.
# Landings antigas (hvac, gbp, meta…): continuam com Roboto do Google Fonts.
FONTES_SITE = """<link rel="preload" href="{base}assets/fonts/cal-sans-400.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{base}assets/fonts/cal-sans-ui-var.woff2" as="font" type="font/woff2" crossorigin>"""
FONTES_GOOGLE = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;800;900&display=swap" rel="stylesheet">"""


def e_site(pg):
    """Páginas do site principal: carregam só o site.css (as landings, só o styles.css)."""
    return pg.get("body") == "tema-home"


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




def _texto(html):
    """Tira tags e devolve texto limpo, para os dados estruturados."""
    # tags de linha (negrito, links) saem sem deixar espaço; as de bloco
    # deixam um espaço, para as frases não colarem umas às outras
    t = re.sub(r"</?(?:strong|b|em|i|a|span)(?:\s[^>]*)?>", "", html)
    t = re.sub(r"<[^>]+>", " ", t)
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
            "priceRange": "€€",
            "areaServed": {"@type": "Country", "name": "Portugal"},
            "address": {"@type": "PostalAddress", "streetAddress": "R. dos Arneiros 133",
                        "postalCode": "1500-057", "addressLocality": "Lisboa",
                        "addressCountry": "PT"},
            "telephone": "+351926289562",
            "hasMap": "https://www.google.com/maps/place//data=!4m2!3m1!1s0x6c31721fe402361b:0x7cd0a64535a7b664",
            "sameAs": SOCIAIS,
            # Sem catálogo de serviços: as páginas /seo, /ads e /websites foram
            # apagadas e o site fala de resultados, não de uma lista de serviços.
            "knowsAbout": ["Publicidade online", "Google Ads", "Meta Ads",
                           "Geração de leads", "Empresas de serviços"],
        })
        blocos.append({"@context": "https://schema.org", "@type": "WebSite",
                       "@id": SITE + "/#site", "url": SITE + "/", "name": "LGDigital",
                       "inLanguage": "pt-PT",
                       "publisher": {"@id": SITE + "/#organizacao"}})
    else:
        trilho = [{"@type": "ListItem", "position": 1, "name": "Início", "item": SITE + "/"}]
        if pg.get("pai"):                       # ex.: ("Artigos", "artigos/")
            trilho.append({"@type": "ListItem", "position": 2, "name": pg["pai"][0],
                           "item": SITE + "/" + pg["pai"][1]})
        trilho.append({"@type": "ListItem", "position": len(trilho) + 1,
                       "name": pg.get("nome", pg["title"]), "item": canonical})
        blocos.append({"@context": "https://schema.org", "@type": "BreadcrumbList",
                       "itemListElement": trilho})

    # só os <details> dentro de um bloco de FAQ; os menus do cabeçalho também
    # são <details> e não podem entrar aqui
    perguntas = []
    for m in re.finditer(r'<div class="(?:hm-faq|gbp-faq|faq|lg-faq)(?: [^"]*)?"[^>]*>', body):
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
        fontes=(pg.get("fontes") or (FONTES_SITE if e_site(pg) else FONTES_GOOGLE)).replace("{base}", base),
        tema_cor=(pg.get("cor") or ("#FCFCFC" if e_site(pg) else "#F5A623")),
        jsonld=jsonld,
        extra=(extra + "\n") if extra else "",
        bodyclass=(' class="%s"' % pg["body"]) if pg.get("body") else "")


def build_site():
    for pg in PAGES:
        # site principal: só o site.css; landings: só o styles.css
        folha = pg.get("css") or ("site.css" if e_site(pg) else "styles.css")
        # ?v= muda sempre que a folha muda: o Cloudflare guarda o CSS 4 horas,
        # e sem isto o HTML novo aparecia com o CSS antigo
        versao = hashlib.md5((ROOT / "assets/css" / folha).read_bytes()).hexdigest()[:8]
        styles = '<link rel="stylesheet" href="%sassets/css/%s?v=%s">' % (pg["base"], folha, versao)
        corpo = render(pg["src"], pg["base"], pg["home"])
        p = ROOT / pg["out"]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(head_for(pg, styles, pg["base"], jsonld_para(pg, corpo)) + corpo + FOOT,
                     encoding="utf-8")
        print("  %-24s %2d secções  %5.0f KB" % (pg["out"], len(sections(pg["src"])), p.stat().st_size / 1024))


def build_redirects():
    for caminho, ancora in REDIRECIONAR.items():
        profundidade = caminho.strip("/").count("/") + 1
        relativo = "../" * profundidade + ancora
        destino = ROOT / caminho / "index.html"
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(REDIRECT.format(
            absoluto=SITE + "/" + ancora.split("#")[0], relativo=relativo,
            relativo_js=json.dumps(relativo)), encoding="utf-8")
        print("  %-30s -> /%s" % (caminho, ancora))


def inline_data(path):
    f = ROOT / path
    mime = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
    return "data:%s;base64,%s" % (mime, base64.b64encode(f.read_bytes()).decode())


def build_standalone():
    """Um ficheiro só, com CSS e imagens embutidos. Para enviar ou pré-visualizar."""
    def embute(texto):
        # imagens e fontes referidas a partir de assets/css/
        return re.sub(r'url\("\.\./(img|fonts)/([^"]+)"\)',
                      lambda m: 'url("%s")' % inline_data("assets/%s/%s" % (m.group(1), m.group(2))),
                      texto)
    css_base = embute((ROOT / "assets/css/styles.css").read_text(encoding="utf-8"))
    css_site = embute((ROOT / "assets/css/site.css").read_text(encoding="utf-8"))
    outdir = ROOT / "preview"; outdir.mkdir(exist_ok=True)
    for pg in PAGES:
        html = render(pg["src"], "", "#")
        html = re.sub(r'src="assets/img/([^"]+)"',
                      lambda m: 'src="%s"' % inline_data("assets/img/" + m.group(1)), html)
        html = re.sub(r'href="(hvac|pp|tc|hvac-obrigado)/"', 'href="#"', html)
        css = (embute((ROOT / "assets/css" / pg["css"]).read_text(encoding="utf-8")) if pg.get("css")
               else css_site if e_site(pg) else css_base)
        head = head_for(pg, "<style>\n%s\n</style>" % css, "")
        # no ficheiro único as fontes já vão embutidas: o preload ficava a apontar para nada
        head = re.sub(r'<link rel="preload"[^>]*as="font"[^>]*>\n?', "", head)
        name = pg["src"] + ".html"
        (outdir / name).write_text(head + html + FOOT, encoding="utf-8")
        print("  preview/%-20s %5.0f KB" % (name, (outdir / name).stat().st_size / 1024))


if __name__ == "__main__":
    print("A gerar o site:")
    build_site()
    print("Redirecionamentos:")
    build_redirects()
    if "--standalone" in sys.argv:
        print("A gerar as versões num ficheiro só:")
        build_standalone()
