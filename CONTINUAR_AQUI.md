# Continuar aqui

Atualizado em 2026-09-22 (sessão 1).

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

## Falta para ir ao ar (Bruno)

1. **Preencher `negocio.toml`**: whatsapp, whatsapp_legivel, email,
   endereco, cep, horarios. Enquanto vazio, o site mostra "[a preencher]" em
   amarelo e o botão de WhatsApp aponta para /contato.
2. **Revisar o texto com a sua voz.** Escrevi em primeira pessoa a partir da
   proposta. Conferir em especial:
   - `atendimento.md`: a ordem e a descrição das 7 etapas e da "análise
     geométrica" — descrevi pelo que o nome indica, não pela sua prática.
   - `agendar.md`: "receita de preferência com menos de um ano" e o prazo.
   - `sobre.md`: a menção aos livros e à protanomalia — o tom é seu?
   - `inicio.md`: a frase em destaque ("Quem entende o que está usando…").
3. **Uma foto boa** (armação na bancada ou o ateliê). Hoje o herói usa o
   desenho da lente; a proposta pede foto. Soltar em `casca/` e pedir a troca.
4. Hospedagem: GitHub Pages ou Cloudflare Pages servindo `site/`, domínio
   apontado. Rodar `python gerar.py --publicar` antes — ele recusa se faltar
   algo. Ainda não é repositório git.
5. Perfil da Empresa no Google (fora do site, mas é parte do aceite).

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
