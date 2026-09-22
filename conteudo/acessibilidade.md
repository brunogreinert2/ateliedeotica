---
titulo: Como este site foi feito
descricao: A especificação tipográfica e de acessibilidade do site do Ateliê de Ótica — fontes, corpo, entrelinha, nove temas de alto contraste e as medições de contraste de cada um.
rota: /acessibilidade
menu: Acessibilidade
ordem: 5
---

<p class="chapeu">Colofão</p>

# Como este site foi feito

Um óptico que tem protanomalia faz um site para quem enxerga mal. Esta página
declara, como o colofão de um livro, a especificação da própria página — para
que você possa conferir cada afirmação.

## A composição

Texto composto em **Atkinson Hyperlegible**, desenhada pelo Braille Institute
para que letras parecidas — como *I*, *l* e *1* — nunca se confundam. Títulos
em **Cardo**, uma serifada de tradição renascentista.

- Corpo base de **{{corpo_base}}**, a partir da letra configurada no seu
  aparelho — se você já aumentou a letra no sistema, o site respeita.
- Entrelinha de **{{entrelinha}}**.
- Medida máxima de **{{medida}}** por linha, a extensão confortável para o
  olho voltar ao começo da linha seguinte sem se perder.
- Alinhado à esquerda, **sem justificação**: o espaço entre as palavras é
  sempre o mesmo, e não se abrem "rios" brancos no meio do texto.
- Todas as fontes vêm do próprio site. Nenhuma é buscada em serviço de
  terceiros, e nada do que você faz aqui é enviado a ninguém.

## Os controles

No topo de toda página há uma barra com quatro controles, sempre na mesma
ordem e no mesmo lugar:

- **Φ** abre o mapa do site inteiro.
- **A−** e **A+** diminuem e aumentam a letra de verdade — o texto se
  recompõe, não é um zoom da tela. A escolha fica guardada no seu navegador.
- **Ξ** abre o sumário da página que você está lendo.

Ao lado deles, **Tema** abre as nove combinações de cor e as três fontes de
leitura. Tudo navegável pelo teclado, com o foco sempre visível.

## Nove temas, medidos

Cada tema abaixo foi medido automaticamente quando o site foi gerado, pela
fórmula de contraste do WCAG. A tabela mostra três pares:

- **Texto** — letra comum sobre o fundo. Meta: **7:1** (nível AAA).
- **Destaque** — links e botões sobre o fundo. Meta: **7:1**, porque link
  também é texto.
- **Contorno** — bordas de botões e campos. Meta: **3:1** (WCAG 1.4.11).

E cada par foi medido de novo sob simulação de **protanopia**,
**deuteranopia** e **tritanopia** (modelo de Machado, 2009); a tabela mostra o
pior dos quatro resultados. Onde está escrito "abaixo", o tema não atinge a
meta naquele par — está declarado aqui, não escondido.

{{tabela_contraste}}

## Nada depende só de cor

Botão tem contorno e rótulo escrito. Link é sublinhado. Estado selecionado é
marcado por forma e por texto, não só por mudar de cor. Se você não
distinguir nenhuma cor, o site continua inteiro.

## Legível por pessoas e por máquinas

Todo o texto está no próprio HTML da página. Sem JavaScript, o site funciona
por inteiro — só os controles de conforto somem. Leitores de tela, tradutores
automáticos, buscadores e assistentes de IA leem exatamente o que você lê.

Página gerada em {{data_geracao}}.
