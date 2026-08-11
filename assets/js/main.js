/* =========================================================
   Workshop de Estética Avançada — Navigare
   Contagem regressiva, revelações no scroll, parallax leve,
   barra fixa mobile e rastreamento de CTAs.
   ========================================================= */
(function () {
  "use strict";

  /* -------------------------------------------------------
     ⚠️  CONFIGURAÇÃO — edite apenas estas duas linhas
     ------------------------------------------------------- */

  /* Link de inscrição. Enquanto estiver vazio, os botões rolam até a
     seção final. Preenchido, TODOS os CTAs passam a apontar para cá. */
  var LINK_INSCRICAO =
    "https://www.sympla.com.br/evento/associacao-de-recursos-esteticos-para-potencializacao-de-resultados/3493821";

  /* Data e hora do evento — 20/08/2026, 19h, America/Fortaleza (UTC−03:00) */
  var DATA_EVENTO = "2026-08-20T19:00:00-03:00";

  /* ------------------------------------------------------- */

  var reduzirMovimento = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------------------------------------------------------
     1. Links de inscrição
     --------------------------------------------------------- */
  var ctas = Array.prototype.slice.call(document.querySelectorAll("[data-cta]"));

  if (LINK_INSCRICAO) {
    ctas.forEach(function (el) {
      el.setAttribute("href", LINK_INSCRICAO);
      el.setAttribute("target", "_blank");
      el.setAttribute("rel", "noopener noreferrer");
    });
  } else if (window.console && console.info) {
    console.info(
      "[Navigare] Link de inscrição não configurado. " +
      "Defina LINK_INSCRICAO em assets/js/main.js."
    );
  }

  /* ---------------------------------------------------------
     2. Eventos de conversão (GTM / GA4 / Meta Pixel)
     --------------------------------------------------------- */
  function rastrearClique(origem) {
    var payload = {
      event: "cta_click",
      cta_location: origem,
      event_name: "Workshop Estética Avançada — João Pessoa",
      event_date: DATA_EVENTO
    };

    if (window.dataLayer && typeof window.dataLayer.push === "function") {
      window.dataLayer.push(payload);
    }
    if (typeof window.gtag === "function") {
      window.gtag("event", "cta_click", {
        cta_location: origem,
        event_category: "inscricao",
        event_label: "Workshop Estética Avançada"
      });
    }
    if (typeof window.fbq === "function") {
      window.fbq("track", "Lead", { content_name: "Workshop Estética Avançada", source: origem });
    }
  }

  ctas.forEach(function (el) {
    el.addEventListener("click", function () {
      rastrearClique(el.getAttribute("data-cta") || "desconhecido");
    });
  });

  /* ---------------------------------------------------------
     3. Contagem regressiva
     --------------------------------------------------------- */
  var relogio = document.getElementById("clock");
  var aviso = document.getElementById("clock-over");

  if (relogio && aviso) {
    var alvo = new Date(DATA_EVENTO).getTime();
    var campos = {
      dias:     relogio.querySelector('[data-unit="dias"]'),
      horas:    relogio.querySelector('[data-unit="horas"]'),
      minutos:  relogio.querySelector('[data-unit="minutos"]'),
      segundos: relogio.querySelector('[data-unit="segundos"]')
    };

    var pad = function (n, casas) {
      var s = String(n);
      while (s.length < (casas || 2)) { s = "0" + s; }
      return s;
    };

    var tique = function () {
      var restante = alvo - Date.now();

      if (restante <= 0) {
        relogio.hidden = true;
        aviso.hidden = false;
        clearInterval(intervalo);
        return;
      }

      var seg = Math.floor(restante / 1000);
      campos.dias.textContent     = pad(Math.floor(seg / 86400));
      campos.horas.textContent    = pad(Math.floor(seg / 3600) % 24);
      campos.minutos.textContent  = pad(Math.floor(seg / 60) % 60);
      campos.segundos.textContent = pad(seg % 60);
    };

    tique();
    var intervalo = setInterval(tique, 1000);
  }

  /* ---------------------------------------------------------
     4. Revelações no scroll
     --------------------------------------------------------- */
  var reveláveis = document.querySelectorAll(".reveal, .fade-img");

  if (!("IntersectionObserver" in window) || reduzirMovimento) {
    Array.prototype.forEach.call(reveláveis, function (el) { el.classList.add("is-in"); });
  } else {
    var observador = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (entrada) {
        if (entrada.isIntersecting) {
          entrada.target.classList.add("is-in");
          observador.unobserve(entrada.target);
        }
      });
    }, { rootMargin: "0px 0px -12% 0px", threshold: 0.12 });

    Array.prototype.forEach.call(reveláveis, function (el) { observador.observe(el); });
  }

  /* ---------------------------------------------------------
     5. Parallax discreto nas fotografias
     --------------------------------------------------------- */
  var camadas = document.querySelectorAll("[data-parallax] [data-depth]");

  if (camadas.length && !reduzirMovimento && window.matchMedia("(min-width: 901px)").matches) {
    var pendente = false;

    var mover = function () {
      pendente = false;
      var meio = window.innerHeight / 2;

      Array.prototype.forEach.call(camadas, function (camada) {
        var caixa = camada.getBoundingClientRect();
        if (caixa.bottom < -200 || caixa.top > window.innerHeight + 200) { return; }
        var centro = caixa.top + caixa.height / 2;
        var desloc = (centro - meio) * parseFloat(camada.dataset.depth || "0.04");
        camada.style.transform = "translate3d(0," + Math.max(-20, Math.min(20, desloc)).toFixed(2) + "px,0)";
      });
    };

    window.addEventListener("scroll", function () {
      if (!pendente) { pendente = true; window.requestAnimationFrame(mover); }
    }, { passive: true });

    mover();
  }

  /* ---------------------------------------------------------
     6. Cabeçalho e barra fixa mobile
     --------------------------------------------------------- */
  var topbar = document.getElementById("topbar");
  var barra = document.getElementById("sticky-cta");
  var hero = document.getElementById("topo");

  window.addEventListener("scroll", function () {
    if (topbar) { topbar.classList.toggle("is-stuck", window.scrollY > 12); }
  }, { passive: true });

  if (barra && hero && "IntersectionObserver" in window) {
    new IntersectionObserver(function (entradas) {
      barra.classList.toggle("is-visible", !entradas[0].isIntersecting);
    }, { rootMargin: "-40% 0px 0px 0px" }).observe(hero);
  }

  /* ---------------------------------------------------------
     7. Scroll suave para âncoras internas
     --------------------------------------------------------- */
  document.addEventListener("click", function (evento) {
    var alvoLink = evento.target.closest('a[href^="#"]');
    if (!alvoLink) { return; }

    var id = alvoLink.getAttribute("href");
    if (id === "#" || alvoLink.target === "_blank") { return; }

    var destino = document.querySelector(id);
    if (!destino) { return; }

    evento.preventDefault();
    destino.scrollIntoView({
      behavior: reduzirMovimento ? "auto" : "smooth",
      block: "start"
    });
    if (history.replaceState) { history.replaceState(null, "", id); }
  });

  /* ---------------------------------------------------------
     8. Ano no rodapé
     --------------------------------------------------------- */
  var ano = document.getElementById("ano");
  if (ano) { ano.textContent = new Date().getFullYear(); }
})();
