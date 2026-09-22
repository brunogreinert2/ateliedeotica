# ateliedeotica.com.br

Vitrine do Ateliê de Ótica. A proposta que decide tudo é
`C:\Claude\negocio\PROPOSTA-site-atelie.md` — ler antes de mexer.
Estado e próximo passo: `CONTINUAR_AQUI.md`.

## Irmão, não peça

Herda do Pedra Angular a identidade (Atkinson + Cardo, nove temas, A−/A+,
Barra Angular Φ · A− · A+ · Ξ, contraste medido). NÃO herda o registro de
doação: aqui tem botão de agendar na primeira tela.

## Como funciona

```
python gerar.py              # gera site/ e lista pendências
python gerar.py --publicar   # recusa se negocio.toml tiver campo vazio
```

| Onde | O que é |
| --- | --- |
| `conteudo/*.md` | uma página por arquivo; front matter: titulo, descricao, rota, menu, ordem |
| `negocio.toml` | WhatsApp, e-mail, endereço, horários — ÚNICA fonte; campo vazio = pendência |
| `casca/base.css`, `casca/casca.js` | a aparência e o conforto; só USAM `--color-*` |
| `app-leitura/src/styles.css` | os nove temas, lidos token a token (nunca redigitar) |
| `app-leitura/public/fonts/` | as fontes, copiadas na geração (LEI 3: zero rede) |
| `site/` | DERIVADO. Nunca editar à mão. É o que vai para a hospedagem |

Markdown aceito (além do básico): `::: classe` … `:::` abre/fecha div
(heroi, cartoes, cartao, passos, chamada, botoes, fichas, ficha, citacao);
`[rótulo](/rota){.botao}` ou `{.botao-2}`; `[..](whatsapp:agendar)` vira link
wa.me com a mensagem de `negocio.toml`; `{{campo}}` lê de `negocio.toml`;
`{{figura_lente}}` e `{{tabela_contraste}}` são blocos gerados;
`## Título {#ancora}` fixa o id.

Preview: config `ateliedeotica` no `C:\Claude\.claude\launch.json`, porta 4187.

## Regras que não se rediscutem

- `/armacoes/<slug>` é definitivo; loja futura não muda URL de produto.
- Nada comunica só por cor (protanomalia do Bruno). Nunca rosa/roxo como sinal.
- Texto todo no `<body>`; sem JS o site funciona inteiro (LEI 1/2).
- A página `/acessibilidade` afirma números: `ESPEC` no gerar.py espelha
  `base.css`. Mudou um, muda o outro — ela não pode mentir.
