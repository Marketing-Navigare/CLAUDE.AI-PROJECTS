/* =========================================================
   Workshop de Estética Avançada — Navigare
   Interações: menu mobile, scroll suave, reveal, sticky CTA
   ========================================================= */
(function () {
  'use strict';

  var header     = document.querySelector('.site-header');
  var navToggle  = document.getElementById('navToggle');
  var mobileNav  = document.getElementById('mobileNav');
  var mobileCta  = document.getElementById('mobileCta');
  var hero       = document.querySelector('.hero');

  /* ---------- Menu mobile ---------- */
  function closeMenu() {
    if (!mobileNav) return;
    mobileNav.classList.remove('open');
    navToggle.setAttribute('aria-expanded', 'false');
    navToggle.setAttribute('aria-label', 'Abrir menu');
  }

  function openMenu() {
    mobileNav.classList.add('open');
    navToggle.setAttribute('aria-expanded', 'true');
    navToggle.setAttribute('aria-label', 'Fechar menu');
  }

  if (navToggle && mobileNav) {
    navToggle.addEventListener('click', function (e) {
      e.stopPropagation();
      mobileNav.classList.contains('open') ? closeMenu() : openMenu();
    });

    mobileNav.addEventListener('click', function (e) {
      if (e.target.closest('a')) closeMenu();
    });

    document.addEventListener('click', function (e) {
      if (!mobileNav.classList.contains('open')) return;
      if (!mobileNav.contains(e.target) && !navToggle.contains(e.target)) closeMenu();
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeMenu();
    });

    window.addEventListener('resize', function () {
      if (window.innerWidth > 860) closeMenu();
    });
  }

  /* ---------- Scroll suave com compensação do header ---------- */
  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      var id = link.getAttribute('href');
      if (!id || id === '#') return;

      var target = document.querySelector(id);
      if (!target) return;

      e.preventDefault();
      closeMenu();

      var headerH = header ? header.offsetHeight : 0;
      var top = target.getBoundingClientRect().top + window.pageYOffset - headerH - 8;

      var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      window.scrollTo({ top: Math.max(top, 0), behavior: reduce ? 'auto' : 'smooth' });

      if (history.replaceState) history.replaceState(null, '', id);
    });
  });

  /* ---------- Entrada do hero (revela de imediato, em cascata) ---------- */
  var heroReveal = hero ? hero.querySelectorAll('.fade-up') : [];
  Array.prototype.forEach.call(heroReveal, function (el, i) {
    el.style.transitionDelay = (0.08 * i) + 's';
    requestAnimationFrame(function () { el.classList.add('is-visible'); });
  });

  /* ---------- Reveal on scroll ---------- */
  var revealables = Array.prototype.filter.call(
    document.querySelectorAll('.fade-up'),
    function (el) { return !hero || !hero.contains(el); }
  );

  if ('IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });

    revealables.forEach(function (el) { observer.observe(el); });
  } else {
    revealables.forEach(function (el) { el.classList.add('is-visible'); });
  }

  /* ---------- Header scrolled + sticky CTA ---------- */
  var ticking = false;

  function onScroll() {
    var y = window.pageYOffset;

    if (header) header.classList.toggle('scrolled', y > 24);

    if (mobileCta) {
      var threshold = hero ? hero.offsetHeight * 0.6 : 520;
      var atBottom  = (window.innerHeight + y) >= (document.body.offsetHeight - 160);
      mobileCta.classList.toggle('visible', y > threshold && !atBottom);
    }

    ticking = false;
  }

  window.addEventListener('scroll', function () {
    if (!ticking) {
      window.requestAnimationFrame(onScroll);
      ticking = true;
    }
  }, { passive: true });

  onScroll();
})();
