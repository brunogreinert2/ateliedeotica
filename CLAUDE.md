# ateliedeotica.com.br

O **canteiro** do Ateliê de Ótica: só conteúdo, dados e as peças desta casa.
A ferramenta que constrói mora fora, em `C:\Claude\atelie-gerador` — ler o
`CLAUDE.md` de lá antes de mexer em geração.

Decisões que mandam: `C:\Claude\negocio\PROPOSTA-site-atelie.md` (este site) e
`C:\Claude\negocio\PROPOSTA-duas-frentes.md` (a família).
Estado e próximo passo: `CONTINUAR_AQUI.md`.

## Irmão, não peça

Herda do Pedra Angular a identidade (Atkinson + Cardo, nove temas, A−/A+,
Barra Angular Φ · A− · A+ · Ξ, contraste medido). NÃO herda o registro de
doação: aqui tem botão de agendar na primeira tela.

## Como gerar

```
python ../atelie-gerador/gerar.py --sitio .
python ../atelie-gerador/gerar.py --sitio . --publicar   # falha se houver pendência
```

Preview: config `ateliedeotica` no `C:\Claude\.claude\launch.json`, porta 4187
(serve `site/`).

| Onde | O que é |
| --- | --- |
| `conteudo/*.md` | uma página por arquivo (front matter + Markdown) |
| `negocio.toml` | WhatsApp, e-mail, endereço, horários + a tabela `[marca]`. ÚNICA fonte; campo vazio = pendência |
| `pecas/figura-lente.html` | o desenho dos raios na lente, chamado por `{{figura_lente}}` |
| `pecas/icone.svg` | o ícone da aba |
| `casca/local.css` | CSS só desta casa (hoje: a figura da lente) |
| `site/` | DERIVADO, fora do git. Nasce no build a cada push |

A sintaxe de Markdown aceita, o contrato do `negocio.toml` e o front matter
estão documentados no `CLAUDE.md` da ferramenta — aqui não se duplica.

## Regras que não se rediscutem

- `/armacoes/<slug>` é definitivo; loja futura não muda URL de produto.
- Nada comunica só por cor (protanomalia do Bruno). Nunca rosa/roxo como sinal.
- Texto todo no `<body>`; sem JS o site funciona inteiro (LEI 1/2).
- O que for exceção desta casa mora em `pecas/` ou `casca/local.css` —
  **nunca** vira um `if` dentro da ferramenta.
