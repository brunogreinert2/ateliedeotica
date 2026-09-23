# Continuar aqui

Atualizado em 2026-09-22 (sessão 2).

**No ar:** https://brunogreinert2.github.io/ateliedeotica/ — repo público
`brunogreinert2/ateliedeotica`, branch `master`, publicado por Actions a cada
push (`.github/workflows/deploy.yml`). `site/` NÃO vai no git: nasce no build.

**Marco A feito (2026-09-22):** este repositório é agora só o CANTEIRO. A
ferramenta virou `brunogreinert2/atelie-gerador` (`C:\Claudetelie-gerador`)
e o build clona ela e o app-leitura. Gerar aqui:
`python ../atelie-gerador/gerar.py --sitio .`

## Onde estamos

**Marco 1 construído, falta preencher e publicar.** Marco 2 adiantado.

Feito e verificado no navegador (desktop e celular 375 px):

- `/`, `/atendimento`, `/agendar`, `/sobre`, `/contato` (Marco 1) e
  `/acessibilidade` (do Marco 2), mais `404.html`, `sitemap.xml`,
  `robots.txt`, `CNAME` e dados estruturados `schema.org/Optician`.
- Nove temas lidos do app-leitura; A−/A+ como multiplicador sobre a letra do
  aparelho (padrão 18 px); Barra Angular; painel de tema e fonte; Ξ monta o
  sumário dos `h2`. Φ é `<a href="#mapa">` — sem JS leva ao mapa do rodapé.
- Contraste medido na geração, pior caso entre visão típica e simulações de
  protanopia/deuteranopia/tritanopia (Machado 2009): **os nove temas passam**
  em texto (7:1), destaque (7:1) e contorno (3:1). Aceite do Marco 2 cumprido.
  O alerta antigo da auditoria ("sete de nove fracos") não vale mais para os
  tokens `--color-*` atuais.
- Botão de agendar acima da dobra no celular. Herói: desenho de raios
  atravessando uma lente convergente até o foco (as "duas luzes").

## Falta (Bruno)

1. **Apontar o domínio.** O DNS do ateliedeotica.com.br está no registro.br
   (a.auto.dns.br) e ainda não tem registro A. No painel do registro.br,
   adicionar quatro A do domínio raiz para 185.199.108.153, 185.199.109.153,
   185.199.110.153 e 185.199.111.153, e um CNAME de `www` para
   `brunogreinert2.github.io`. Quando resolver, fechar com:
   `gh api -X PUT repos/brunogreinert2/ateliedeotica/pages -f cname=ateliedeotica.com.br -F https_enforced=true`
   O domínio custom NÃO foi configurado ainda de propósito: configurar antes do
   DNS faria o endereço github.io redirecionar para um domínio que não resolve,
   derrubando o que já está no ar.
2. **Revisar o texto com a sua voz.** Escrevi em primeira pessoa a partir da
   proposta. Conferir em especial:
   - `atendimento.md`: a ordem e a descrição das 7 etapas e da "análise
     geométrica" — descrevi pelo que o nome indica, não pela sua prática.
   - `agendar.md`: "receita de preferência com menos de um ano" e o prazo.
   - `sobre.md`: a menção aos livros e à protanomalia — o tom é seu?
   - `inicio.md`: a frase em destaque ("Quem entende o que está usando…").
3. **Fotos.** Não há foto boa de armação ainda; o que existe é ANTES e DEPOIS
   de polimento e de remoção de antirreflexo. Isso é melhor do que foto de
   vitrine: é prova de serviço e é conteúdo. Pendente decidir se vira uma
   página `/polimento` (serviço + galeria antes/depois) ou uma seção. Precisa
   de um componente de comparação e de um lugar para as imagens (`imagens/`,
   copiadas pelo gerar.py).
4. Perfil da Empresa no Google (fora do site, mas é parte do aceite do Marco 1).

## Próximos marcos

- **Marco 3** — `/guia/` (cinco primeiros assuntos da seção 9 da proposta) e
  `/precos` com a tabela explicada. Preciso da tabela real de preços.
- **Marco 4** — `/armacoes/<slug>` (schema Product, botão consultar) e
  `/remontagem` com formulário. Formulário em site estático precisa de um
  serviço (ex.: Formspree) — decidir.
- **Marco 5** — `/livros` e `/notas/`.

Aceite do Marco 1 ainda não testado: "uma pessoa que nunca te viu marca hora
pelo celular em menos de dois minutos" — só com WhatsApp preenchido e uma
pessoa de verdade.
