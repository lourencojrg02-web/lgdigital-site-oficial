# lgdigital.pt

Site estático da LGDigital. Sem dependências, sem build tools — só HTML, CSS e
um script Python que junta as secções.

## Estrutura

```
.
├─ index.html          página inicial                           → lgdigital.pt/
├─ hvac/index.html     landing de AVAC                          → lgdigital.pt/hvac
├─ seo/index.html      SEO local                                → lgdigital.pt/seo
├─ gbp/index.html      landing: Top 3 garantido (oferta)        → lgdigital.pt/gbp
├─ ads/index.html      Google Ads & Meta Ads                    → lgdigital.pt/ads
├─ websites/index.html Websites e landing pages                 → lgdigital.pt/websites
├─ contactos/          contactos + calendário                   → lgdigital.pt/contactos
├─ hvac-obrigado/      página de agradecimento (noindex)        → lgdigital.pt/hvac-obrigado
├─ pp/index.html       política de privacidade                  → lgdigital.pt/pp
├─ tc/index.html       termos e condições                       → lgdigital.pt/tc
├─ 404.html
├─ favicon.ico        ícone do site (o browser procura-o sempre na raiz)
├─ site.webmanifest   ícones para Android e "adicionar ao ecrã inicial"
├─ assets/
│  ├─ css/styles.css   folha de estilos partilhada (é aqui que se mexe no design)
│  └─ img/             logo, ícones, logos de clientes, capturas de resultados
├─ src/                ← ONDE SE EDITA
│  ├─ _partials/       cabeçalho e rodapé partilhados por várias páginas
│  ├─ 404/             página de erro
│  ├─ home/            secções da página inicial
│  ├─ hvac/            secções da landing de AVAC
│  ├─ seo/             secções da página de SEO local
│  ├─ gbp/             secções da landing "Top 3 garantido"
│  ├─ ads/             secções da página de anúncios
│  ├─ websites/        secções da página de websites
│  ├─ contactos/       página de contactos
│  ├─ pp/              política de privacidade
│  └─ tc/              termos e condições
├─ build.py
├─ CNAME               lgdigital.pt
└─ .nojekyll           impede o GitHub Pages de processar com Jekyll
```

**Os ficheiros `index.html` e `hvac/index.html` são gerados. Não se editam à mão** —
edita-se `src/` e corre-se o build.

## Como trabalhar

```bash
python3 build.py                # gera index.html e hvac/index.html
python3 build.py --standalone   # gera também preview/*.html num ficheiro só
```

Para ver localmente (os caminhos relativos precisam de um servidor):

```bash
python3 -m http.server 8000
# depois abre http://localhost:8000
```

Depois é só `git add . && git commit && git push`. O GitHub Pages publica sozinho.

### Editar a landing de AVAC

Cada secção é um ficheiro em `src/hvac/`, por ordem:

| ficheiro | secção |
|---|---|
| `01-header.html` | cabeçalho fixo e navegação |
| `02-hero.html` | título, subtítulo e mock da pesquisa do Google |
| `03-logos.html` | faixa de logos de clientes |
| `04-selos.html` | *(vazio — certificações removidas)* |
| `05-problema.html` | secção escura com os quatro pontos negativos |
| `06-sistema.html` | o sistema da LGDigital, três cartões |
| `07-intencao.html` | Google 35€ vs Meta 25€ |
| `08-como-funciona.html` | os quatro passos |
| `09-incluido.html` | o que está incluído |
| `10-precos.html` | cartão de preço |
| `11-banner-cta.html` | banner âmbar |
| `12-garantia.html` | "Só pagas por chamadas reais" |
| `13-resultados.html` | capturas de prova social |
| `14-encaixe.html` | "Isto é para ti?" |
| `15-faq.html` | perguntas frequentes |
| `16-candidatura.html` | CTA e widget de agendamento |
| `17-rodape.html` | rodapé |

Secções que só tenham comentários são ignoradas pelo build — é assim que a
`04-selos.html` está desativada sem se apagar o ficheiro.

### SEO

O `build.py` trata de tudo o que é automático:

- `<title>`, `description`, canonical e `hreflang` por página, definidos em `PAGES`
- Open Graph e Twitter Card, com `assets/img/og.png` (1200×630) gerada à parte
- `robots`: `index, follow, max-image-preview:large` nas páginas normais,
  `noindex` nas que têm `noindex=True`
- **Dados estruturados JSON-LD**, gerados a partir do próprio conteúdo:
  `ProfessionalService` + `WebSite` na homepage, `BreadcrumbList` nas restantes,
  e `FAQPage` em todas as páginas com um bloco de FAQ — as perguntas são lidas
  dos `<details>` dentro de `.hm-faq`, `.gbp-faq` ou `.faq`, por isso basta
  escrever a FAQ que a marcação aparece sozinha

`sitemap.xml` e `robots.txt` são mantidos à mão na raiz. Ao criar uma página
nova, acrescenta-a ao sitemap.

**Depois de publicar:** submete o sitemap no Google Search Console e valida os
dados estruturados em `search.google.com/test/rich-results`.

### Rodapé

`_partials/rodape.html` é um cartão branco com o logótipo, redes sociais, três
colunas de links e a assinatura ao centro. É igual em todas as páginas,
incluindo as landings.

### Navegação

As páginas do site principal (`/`, `/casos-estudo`, `/seo`, `/ads`,
`/websites`, `/contactos`, `/melhor-web-designer-lisboa`) partilham
`_partials/header-site.html`: barra preta de anúncio + navegação, ambas fixas
no topo, ao estilo do leadarc.io. Os links são secções da página inicial
(`{{home}}#processo`, `#calculadora`, …); "Casos de estudo" é a única página
à parte. Os serviços já não estão no menu — continuam no rodapé.

O script do cabeçalho:
- abre e fecha o menu do telemóvel (`Esc`, clique fora, clique num link);
- troca os botões `data-agendar` para `#agendar` quando a página tem o seu
  próprio calendário (senão levam ao calendário da página inicial);
- põe o cabeçalho escuro por cima de secções com o atributo `data-escuro`.

Corre só no `DOMContentLoaded`. Tem de ser assim: o script vem no cabeçalho,
e nessa altura as secções da página ainda não existem.

As landings (`/gbp`, `/hvac`, `/meta…`) têm cabeçalho próprio e sem menu, de
propósito: não se dão saídas a quem chegou por um anúncio.

### Partes partilhadas

Uma secção que contenha apenas a linha `@include _partials/rodape.html` é
substituída pelo conteúdo desse ficheiro. É assim que o rodapé e o cabeçalho
simples são iguais em todas as páginas sem estarem copiados quatro vezes.

### Criar uma nova landing

1. `mkdir src/dentistas` e mete lá as secções
2. acrescenta uma entrada à lista `PAGES` no `build.py`
3. `python3 build.py`

Cada entrada de `PAGES` aceita `noindex=True` (para páginas que não devem ir
para o Google), `head="..."` (código extra no `<head>` só dessa página) e
`body="classe"` (classe no `<body>`, para dar um tema diferente à página —
é assim que a `/gbp` fica bege com acento azul, via `.tema-gbp` no CSS).

### Píxel da Meta

O píxel sai em todas as páginas, injetado pelo `build.py`. O ID está na
constante `PIXEL_ID` no topo do ficheiro — muda-se aí e vale para o site todo.
Para desativar, põe `PIXEL_ID = ""`.

A página `/hvac-obrigado` dispara o evento padrão `Schedule` além do
`PageView`, e é essa a conversão a otimizar nas campanhas da Meta.

### Caminhos

Nas secções escreve-se `{{base}}` para a raiz do site e `{{home}}` para a página
inicial. O build substitui conforme a profundidade da página:

```html
<img src="{{base}}assets/img/logo.png">   <!-- em /hvac/ vira ../assets/img/logo.png -->
```

Nunca uses caminhos absolutos (`/assets/...`) — partem se o site for servido
numa subpasta, como acontece no endereço `utilizador.github.io/repo/`. Os
ícones e o manifest também são relativos, por isso funcionam nos dois sítios.

### Trocar o favicon

Substitui `favicon.ico` e os ficheiros `assets/img/favicon-32.png`,
`apple-touch-icon.png` (180×180), `icon-192.png` e `icon-512.png`. São gerados a
partir de um PNG quadrado — o ícone preto com o G branco e a seta azul.

### Mobile

O CSS é *mobile-first*: o que está fora de `@media` é o layout do telemóvel, e
os `@media(min-width: …)` só acrescentam colunas à medida que há espaço. No fim
do ficheiro há um bloco de afinação para ecrãs pequenos (640, 430 e 360px).

**Cuidado ao editar o CSS com scripts.** Vários blocos têm o mesmo nome nos dois
temas (`Hero`, `Cabeçalho`, `Passos`, `FAQ`). Um `s.index("/* ---------- Passos")`
apanha o primeiro, não o do tema que querias — já duplicou o ficheiro inteiro uma
vez. Edita à mão ou procura por seletores, não por títulos de bloco.

### Cores, temas e as duas folhas de estilo

Há **duas folhas de estilo**:

- `assets/css/styles.css` — a base antiga. Serve as landings (`/hvac`, `/gbp`,
  `/meta…`), as páginas legais e os blocos `.hm-*` que ainda existem em `/seo`,
  `/ads`, `/websites` e `/contactos`.
- `assets/css/site.css` — o sistema de desenho novo (classes `lg-*`), inspirado
  no leadarc.io. Só é carregado nas páginas com `body="tema-home"`, depois do
  `styles.css`. Não acrescentes camadas de "correções" ao `styles.css` para a
  página inicial: é no `site.css` que isso vive.

| tema | páginas | folhas | letra |
|---|---|---|---|
| `tema-home` | `/`, `/casos-estudo`, `/seo`, `/ads`, `/websites`, `/contactos`, `/melhor-web-designer-lisboa`, `404` | styles + site | Cal Sans / Cal Sans UI |
| `tema-gbp` | `/gbp` | styles | Roboto |
| `tema-meta` | `/meta`, `/meta-book-a-call`, `/instant-form-book-a-call` | styles | Roboto |
| *(nenhum)* | `/hvac`, `/pp`, `/tc` | styles | Roboto |

**Azuis:** `#0091FF` só em texto grande (palavras destacadas nos títulos).
Botões e links usam `#0076D1`: texto branco sobre `#0091FF` dá 3,2:1 de
contraste e chumba a norma (mínimo 4,5:1); sobre `#0076D1` dá 4,65:1.

### Fontes

Cal Sans (títulos) e Cal Sans UI (texto), as mesmas do leadarc. São de código
aberto (licença OFL, ver `assets/fonts/OFL-*.txt`) e estão alojadas no próprio
site em `assets/fonts/` — não passam pelo Google, por isso nenhum IP de
visitante é enviado a terceiros só por abrir uma página do site principal.
As landings continuam a usar Roboto do Google Fonts.

A Cal Sans é um ficheiro de peso único declarado com `font-weight: 100 900`,
para o browser não inventar um negrito falso quando se pede peso 600.

## Redirect após a marcação

Duas camadas, por esta ordem:

1. **No HighLevel** (recomendado): Calendars → o calendário → Settings →
   Forms & Payment → *On Submit* → **Redirect to URL** →
   `https://lgdigital.pt/hvac-obrigado/`. Se houver opção de redirecionar a
   janela-mãe em vez do iframe, ativa-a.
2. **Rede de segurança no site**: `src/hvac/16-candidatura.html` tem um script
   que fica à escuta das mensagens do iframe e redireciona quando detecta a
   marcação. Se não estiver a funcionar, abre
   `https://lgdigital.pt/hvac/?debug-agenda`, marca uma chamada de teste e vê
   na consola do browser que mensagens o iframe envia — o padrão a detetar
   está na constante `SINAIS` desse ficheiro.

## Publicar

### GitHub Pages

1. **Settings → Pages → Source: Deploy from a branch**, branch `main`, pasta `/ (root)`
2. **Custom domain:** `lgdigital.pt` (o ficheiro `CNAME` já está no repo)
3. Espera pelo certificado e liga **Enforce HTTPS**

### DNS na Cloudflare

Na zona `lgdigital.pt`, para o apex:

| Tipo | Nome | Conteúdo |
|---|---|---|
| A | `@` | `185.199.108.153` |
| A | `@` | `185.199.109.153` |
| A | `@` | `185.199.110.153` |
| A | `@` | `185.199.111.153` |
| CNAME | `www` | `<utilizador>.github.io` |

Três avisos que poupam uma tarde:

- **SSL/TLS → Overview: põe em `Full` (ou `Full (strict)`).** Em `Flexible` dá
  ciclo de redirecionamentos infinito com o GitHub Pages.
- Ao adicionar o domínio no GitHub Pages, **desliga o proxy da Cloudflare
  (nuvem cinzenta)** até o certificado ser emitido. Depois podes voltar a ligar.
- Não mexas no registo `email.lgdigital.pt` — é ele que serve o widget de
  agendamento na landing.

## Por fazer

- [ ] **Preencher os campos entre `[ ]` em `src/pp/` e `src/tc/`** — denominação
      social, NIF, morada, comarca, prazo de pagamento e a questão do IVA
- [ ] Mandar rever as duas páginas legais por alguém com formação jurídica
- [ ] Configurar o redirect para `/hvac-obrigado` nas definições do calendário
      no HighLevel (ver secção abaixo)
- [ ] **Banner de cookies** — o Píxel da Meta é um cookie de publicidade e, na
      UE, exige consentimento prévio
- [ ] Confirmar os números nas legendas de `src/hvac/13-resultados.html`
- [ ] Decidir se `/hvac` (âmbar) e `/gbp` (bege) passam para a paleta das
      restantes páginas — branco, azul `#0091FF` e preto
- [ ] **Confirmar a secção "Como cobramos"** em `src/ads/07-modelos.html` —
      descreve os dois modelos sem valores concretos, de propósito
- [ ] Confirmar prazos e condições nas FAQ de `/seo`, `/ads` e `/websites`
- [ ] **Confirmar preços e a redação da garantia** em `src/gbp/08-pacotes.html`
- [ ] Os botões "Começar" da `/gbp` apontam para `#contacto` — ligar a um
      formulário ou calendário a sério
- [ ] Prova social de campanhas pagas — as capturas atuais são de posicionamento
      local, e o serviço vendido é Google Ads + Meta Ads
