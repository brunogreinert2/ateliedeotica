/* Ateliê de Ótica — o conforto. Sem este arquivo o site continua inteiro:
   texto, links e botões de agendar funcionam; somem só A−/A+, Ξ e o painel
   de tema (e Φ volta a ser um link para o mapa no rodapé). */
(function () {
  'use strict';
  var raiz = document.documentElement;
  raiz.classList.add('js');

  var GUARDA = 'ao:';
  function ler(k, padrao) { try { var v = localStorage.getItem(GUARDA + k); return v === null ? padrao : v; } catch (e) { return padrao; } }
  function gravar(k, v) { try { localStorage.setItem(GUARDA + k, v); } catch (e) {} }
  function marcar(sel, attr, valor) {
    document.querySelectorAll(sel).forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.getAttribute(attr) === valor));
    });
  }

  /* ---- tema e fonte (o <head> já aplicou antes da pintura; aqui só sincroniza) ---- */
  function porTema(t) { raiz.setAttribute('data-theme', t); gravar('tema', t); marcar('[data-escolha-tema]', 'data-escolha-tema', t); }
  function porFonte(f) { raiz.setAttribute('data-fonte', f); gravar('fonte', f); marcar('[data-escolha-fonte]', 'data-escolha-fonte', f); }
  porTema(ler('tema', 'sepia'));
  porFonte(ler('fonte', 'atkinson'));

  /* ---- A− e A+: multiplicador sobre a letra do aparelho, nunca px fixo ---- */
  var MIN = 0.7, MAX = 8, PASSO = 1.125;
  var escala = parseFloat(ler('escala', '1'));
  if (!isFinite(escala)) escala = 1;
  var aviso = document.getElementById('aviso-corpo');
  function porEscala(v, anunciar) {
    escala = Math.min(MAX, Math.max(MIN, Math.round(v * 1000) / 1000));
    raiz.style.setProperty('--escala', String(escala));
    gravar('escala', String(escala));
    if (anunciar && aviso) aviso.textContent = 'Letra em ' + Math.round(escala * 100) + ' por cento';
  }
  porEscala(escala, false);
  document.getElementById('btn-menos').addEventListener('click', function () { porEscala(escala / PASSO, true); });
  document.getElementById('btn-mais').addEventListener('click', function () { porEscala(escala * PASSO, true); });

  /* ---- painéis ---- */
  function abrir(d, botao) {
    if (typeof d.showModal === 'function') d.showModal(); else d.setAttribute('open', '');
    if (botao) botao.setAttribute('aria-expanded', 'true');
    d._botao = botao;
  }
  function fechar(d) { if (typeof d.close === 'function') d.close(); else d.removeAttribute('open'); }
  var dlgMapa = document.getElementById('painel-mapa');
  var dlgSumario = document.getElementById('painel-sumario');
  var dlgTema = document.getElementById('painel-tema');
  [dlgMapa, dlgSumario, dlgTema].forEach(function (d) {
    d.addEventListener('close', function () {
      if (d._botao) { d._botao.setAttribute('aria-expanded', 'false'); d._botao.focus(); }
    });
    d.addEventListener('click', function (e) { if (e.target === d) fechar(d); });
    d.querySelector('[data-fechar]').addEventListener('click', function () { fechar(d); });
  });

  /* Φ é um <a href="#mapa"> — sem JS leva ao mapa no rodapé; com JS abre o painel. */
  document.getElementById('btn-phi').addEventListener('click', function (e) { e.preventDefault(); abrir(dlgMapa, this); });
  document.getElementById('btn-tema').addEventListener('click', function () { abrir(dlgTema, this); });

  /* ---- Ξ: o sumário do que está aberto, lido dos h2 da página ---- */
  document.getElementById('btn-xi').addEventListener('click', function () {
    var alvo = document.getElementById('lista-sumario');
    alvo.innerHTML = '';
    var h1 = document.querySelector('main h1');
    var tits = [];
    if (h1) { if (!h1.id) h1.id = 'topo-da-pagina'; tits.push(h1); }
    document.querySelectorAll('main h2[id]').forEach(function (h) { tits.push(h); });
    tits.forEach(function (h) {
      var li = document.createElement('li');
      if (h.tagName === 'H2' && h1) li.className = 'n3';
      var a = document.createElement('a');
      a.href = '#' + h.id;
      a.textContent = h.textContent;
      a.addEventListener('click', function () { fechar(dlgSumario); });
      li.appendChild(a);
      alvo.appendChild(li);
    });
    abrir(dlgSumario, this);
  });

  document.querySelectorAll('[data-escolha-tema]').forEach(function (b) {
    b.addEventListener('click', function () { porTema(b.getAttribute('data-escolha-tema')); });
  });
  document.querySelectorAll('[data-escolha-fonte]').forEach(function (b) {
    b.addEventListener('click', function () { porFonte(b.getAttribute('data-escolha-fonte')); });
  });
  document.getElementById('btn-restaurar').addEventListener('click', function () {
    porTema('sepia'); porFonte('atkinson'); porEscala(1, true);
  });
})();
