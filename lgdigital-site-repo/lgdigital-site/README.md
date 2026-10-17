# lgdigital.pt

Site estático da LGDigital. Sem dependências, sem build tools — só HTML, CSS e
um script Python que junta as secções.

## Estrutura

```
.
├─ index.html                  página inicial                      → lgdigital.pt/
├─ casos-estudo/               casos de estudo                     → lgdigital.pt/casos-estudo
├─ pp/  tc/                    política de privacidade, termos     → lgdigital.pt/pp, /tc
├─ 404.html
│
├─ meta/                       landing da campanha Meta (noindex)  → lgdigital.pt/meta
├─ meta-book-a-call/           marcação + evento Lead (noindex)
├─ instant-form-book-a-call/   marcação sem evento Lead (noindex)
│
├─ seo/ ads/ websites/ hvac/ hvac-obrigado/ gbp/
│  melhor-web-designer-lisboa/ contactos/
│                              páginas apagadas: só redirecionam (ver abaixo)
│
├─ assets/
│  ├─ css/site.css             sistema de desenho do site principal
│  ├─ css/styles.css           estilos das landings /meta…
│  ├─ fonts/                   Cal Sans + Cal Sans UI (licença OFL)
│  └─ img/                     logótipos, ícones, clientes, capturas de resultados
├─ src/                        ← ONDE SE EDITA
│  ├─ _partials/               header-site.html e rodape.html
│  ├─ home/                    secções da página inicial
│  ├─ casos-estudo/  404/  pp/  tc/
│  └─ meta/  meta-book-a-call/  instant-form-book-a-call/
├─ build.py
├─ sitemap.xml  robots.txt  site.webmanifest  favicon.ico
├─ CNAME                       lgdigital.pt
└─ .nojekyll                   impede o GitHub Pages de processar com Jekyll
```

**Os `index.html` são gerados. Não se editam à mão** — edita-se `src/` e
corre-se o build.

## Como trabalhar

```bash
python3 build.py                # gera as páginas e os redirecionamentos
python3 build.py --standalone   # gera também preview/*.html num ficheiro só
```

Para ver localmente (os caminhos relativos precisam de um servidor):

```bash
python3 -m http.server 8000
# depois abre http://localhost:8000
```

Depois é só `git add . && git commit && git push`. O GitHub Pages publica sozinho.

**Ao apagar ou renomear ficheiros em `src/` pelo site do GitHub**, apaga-os
também lá: o upload por arrastar não apaga nada, e um ficheiro antigo que
fique em `src/home/` volta a entrar no próximo build.

### Página inicial

Cada secção é um ficheiro em `src/home/`, por ordem alfabética:

| ficheiro | secção | âncora |
|---|---|---|
| `01-header.html` | cabeçalho (inclui `_partials/header-site.html`) | |
| `02-hero.html` | fundador, título, botões, grelha de logótipos | `#inicio` |
| `04-beneficios.html` | "O que muda" — seis benefícios | `#beneficios` |
| `05-como-funciona.html` | quatro passos com maquetes de interface | `#processo` |
| `06-calculadora.html` | calculadora de retorno | `#calculadora` |
| `07-resultados.html` | caso em destaque + um cartão por cliente | `#resultados` |
| `08-encaixe.html` | bom encaixe / mau encaixe | `#para-quem` |
| `09-comparacao.html` | tabela LGDigital vs agência vs sozinho | `#comparacao` |
| `10-faq.html` | perguntas frequentes | `#faq` |
| `11-agendar.html` | secção escura com o calendário | `#agendar` |
| `12-rodape.html` | rodapé (inclui `_partials/rodape.html`) | |

O `<main>` abre em `02-hero.html` e fecha em `11-agendar.html`.

Secções que só tenham comentários são ignoradas pelo build. **Nos comentários
não escrevas tags HTML literais** (por exemplo `<div class="lg-faq">`): o build
lê-as como se fossem a sério.

### Navegação

Todas as páginas do site principal partilham `_partials/header-site.html`:
barra preta de anúncio + navegação, ambas fixas no topo, ao estilo do
leadarc.io. Os links são secções da página inicial (`{{home}}#processo`,
`#calculadora`, …); "Casos de estudo" é a única página à parte.

O script do cabeçalho:
- abre e fecha o menu do telemóvel (`Esc`, clique fora, clique num link);
- troca os botões `data-agendar` para `#agendar` quando a página tem o seu
  próprio calendário (senão levam ao calendário da página inicial);
- põe o cabeçalho escuro por cima de secções com o atributo `data-escuro`
  (a secção de marcação e o rodapé).

Corre só no `DOMContentLoaded`. Tem de ser assim: o script vem no cabeçalho,
e nessa altura as secções da página ainda não existem.

As landings `/meta…` têm cabeçalho próprio e sem menu, de propósito: não se
dão saídas a quem chegou por um anúncio.

### Rodapé

`_partials/rodape.html`, escuro, com a estrutura do do leadarc: logótipo e
botão, colunas Empresa (agendar, resultados, casos de estudo), Contactos (email
e LinkedIn) e Legal, e por baixo o copyright e o aviso de não afiliação com o
YouTube, a Google e o Facebook. O site não mostra telefone nem WhatsApp, de
propósito: o único caminho é marcar a chamada.

### Redirecionamentos

As páginas apagadas continuam a existir como redirecionamentos, para não
partir anúncios antigos, favoritos nem resultados do Google. Estão no
dicionário `REDIRECIONAR` do `build.py`:

```python
REDIRECIONAR = {
    "seo/": "", ...,
    "contactos/": "#agendar",
}
```

O GitHub Pages não faz redirecionamentos de servidor, por isso cada caminho
leva uma página mínima com `meta refresh`, `canonical` para a inicial e
`noindex`. O Google trata um refresh imediato como um redirecionamento.
Depois de uns meses, quando o Search Console deixar de mostrar esses
endereços, podem sair.

### SEO

O `build.py` trata de tudo o que é automático:

- `<title>`, `description`, canonical e `hreflang` por página, definidos em `PAGES`
- Open Graph e Twitter Card, com `assets/img/og.png` (1200×630)
- `robots`: `index, follow, max-image-preview:large` nas páginas normais,
  `noindex` nas que têm `noindex=True`
- **Dados estruturados JSON-LD**, gerados a partir do conteúdo:
  `ProfessionalService` + `WebSite` na inicial, `BreadcrumbList` nas outras, e
  `FAQPage` onde houver FAQ — as perguntas são lidas dos `<details>` dentro de
  `.lg-faq` (ou `.hm-faq`, `.gbp-faq`, `.faq`)

`sitemap.xml` e `robots.txt` são mantidos à mão na raiz.

**Depois de publicar:** submete o sitemap no Google Search Console e valida os
dados estruturados em `search.google.com/test/rich-results`.

### Píxel da Meta

O píxel sai em todas as páginas, injetado pelo `build.py`. O ID está na
constante `PIXEL_ID` no topo do ficheiro. Para desativar, `PIXEL_ID = ""`.

A única conversão é o evento `Lead`, que dispara em `/meta-book-a-call`
(campo `head` da página em `PAGES`). A `/instant-form-book-a-call` é igual mas
**sem** o evento, porque quem vem do Instant Form já foi contado pela Meta.

### Caminhos

Nas secções escreve-se `{{base}}` para a raiz do site e `{{home}}` para a página
inicial. O build substitui conforme a profundidade da página:

```html
<img src="{{base}}assets/img/logo.png">   <!-- em /pp/ vira ../assets/img/logo.png -->
```

Nunca uses caminhos absolutos (`/assets/...`) — partem se o site for servido
numa subpasta, como em `utilizador.github.io/repo/`. A exceção é a `404.html`,
que é servida em qualquer caminho e por isso usa `base="/"`.

### Folhas de estilo, cores e letra

| páginas | folha | letra |
|---|---|---|
| `/`, `/casos-estudo`, `/pp`, `/tc`, `404` (`body="tema-home"`) | `site.css` | Cal Sans / Cal Sans UI |
| `/meta`, `/meta-book-a-call`, `/instant-form-book-a-call` (`tema-meta`) | `styles.css` | Roboto (Google Fonts) |

O `site.css` é autossuficiente — tem o próprio reset — e usa classes `lg-*`.
Os valores (raios, sombras, botões, cabeçalho) foram medidos no leadarc.io.

**Azuis:** `#0091FF` só em texto grande (palavras destacadas nos títulos).
Botões e links usam `#0076D1`: texto branco sobre `#0091FF` dá 3,2:1 de
contraste e chumba a norma (mínimo 4,5:1); sobre `#0076D1` dá 4,65:1.

**Letra:** Cal Sans (títulos) e Cal Sans UI (texto), as mesmas do leadarc.
São de código aberto e estão alojadas no próprio site — não passam pelo
Google, por isso nenhum IP de visitante vai para terceiros só por abrir uma
página. A Cal Sans é um ficheiro de peso único declarado com
`font-weight: 100 900`, para o browser não inventar um negrito falso.

**Cuidado ao editar o CSS com scripts.** Procura por seletores, não por
títulos de bloco: já duplicou o ficheiro inteiro uma vez.

### Trocar o favicon

Substitui `favicon.ico` e `assets/img/favicon-32.png`, `apple-touch-icon.png`
(180×180), `icon-192.png` e `icon-512.png`. São gerados a partir de um PNG
quadrado — o ícone preto com o G branco e a seta azul.

## Publicar

### GitHub Pages

1. **Settings → Pages → Source: Deploy from a branch**, branch `main`, pasta `/ (root)`
2. **Custom domain:** `lgdigital.pt` (o ficheiro `CNAME` já está no repo)
3. Espera pelo certificado e liga **Enforce HTTPS**

### DNS na Cloudflare

| Tipo | Nome | Conteúdo |
|---|---|---|
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |
| CNAME | `www` | `<utilizador>.github.io` |

- **SSL/TLS → Overview: põe em `Full` (ou `Full (strict)`).** Em `Flexible` dá
  ciclo de redirecionamentos infinito com o GitHub Pages.
- Ao adicionar o domínio no GitHub Pages, **desliga o proxy da Cloudflare
  (nuvem cinzenta)** até o certificado ser emitido.

## Por fazer

- [ ] **Preencher os campos entre `[ ]` em `src/pp/` e `src/tc/`** — denominação
      social, NIF, morada, comarca, prazo de pagamento e a questão do IVA
- [ ] Mandar rever as duas páginas legais por alguém com formação jurídica
- [ ] **Banner de consentimento de cookies.** O píxel da Meta é um cookie de
      publicidade e, na UE, precisa de consentimento prévio. A frase do rodapé
      informa, mas não substitui o banner.
- [ ] Confirmar a quota de mercado da HCA: 85% no site, 76,95% numa captura antiga
- [ ] Alinhar os Termos com a promessa da `/meta` ("Top 3 em 90 dias ou
      pagamos-te 500€"): que pesquisa, que área, quando começa a contar
- [ ] Daqui a uns meses, tirar os redirecionamentos que já não recebam visitas
