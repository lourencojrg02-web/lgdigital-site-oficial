# lgdigital.pt

Site estático da LGDigital. Sem dependências, sem build tools — só HTML, CSS e
um script Python que junta as secções.

## Estrutura

```
.
├─ index.html          página inicial (placeholder por agora)   → lgdigital.pt/
├─ hvac/index.html     landing de AVAC                          → lgdigital.pt/hvac
├─ 404.html
├─ favicon.ico        ícone do site (o browser procura-o sempre na raiz)
├─ site.webmanifest   ícones para Android e "adicionar ao ecrã inicial"
├─ assets/
│  ├─ css/styles.css   folha de estilos partilhada (é aqui que se mexe no design)
│  └─ img/             logo, ícones, logos de clientes, capturas de resultados
├─ src/                ← ONDE SE EDITA
│  ├─ home/            secções da página inicial
│  └─ hvac/            secções da landing de AVAC
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

### Criar uma nova landing

1. `mkdir src/dentistas` e mete lá as secções
2. acrescenta uma linha à lista `PAGES` no `build.py`
3. `python3 build.py`

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

### Cores e tipografia

Tudo no bloco `:root` no topo de `assets/css/styles.css`. Mudar `--amber`
muda o acento do site inteiro.

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

- [ ] Página inicial a sério (agora é um placeholder em `src/home/`)
- [ ] Páginas de Política de Privacidade e Termos (os links no rodapé são `#`)
- [ ] Confirmar os números nas legendas de `13-resultados.html`
- [ ] Prova social de campanhas pagas — as capturas atuais são de posicionamento
      local, e o serviço vendido é Google Ads + Meta Ads
