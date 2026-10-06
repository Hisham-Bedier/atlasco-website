/* Atlasco Egypt - Main JS */
(function () {
  'use strict';

  /* ---- SCROLL TARGET ----
     Odoo's website frontend layout makes #wrapwrap (not window/body) the
     actual scrolling element (html/body get overflow:hidden). Any
     window.addEventListener('scroll', ...) below that point never fires on
     a real page, so every scroll-driven effect silently stayed inert
     (header condense, parallax, pinned-scroll, scroll-reveal) — found via
     real-browser verification, not just script checks. Route scroll
     listeners through #wrapwrap when present, falling back to window so
     this still works on any page that doesn't use that layout. */
  function scrollTarget() { return document.getElementById('wrapwrap') || window; }
  function scrollTop() {
    var t = scrollTarget();
    return t === window ? (window.scrollY || window.pageYOffset || 0) : t.scrollTop;
  }

  /* ---- TABS ---- */
  function initTabs() {
    document.querySelectorAll('.atl-tab-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var target = this.dataset.tab;
        var parent = this.closest('.atl-solutions-inner');
        parent.querySelectorAll('.atl-tab-btn').forEach(function (b) { b.classList.remove('active'); });
        parent.querySelectorAll('.atl-tab-content').forEach(function (c) { c.classList.remove('active'); });
        this.classList.add('active');
        var content = parent.querySelector('[data-tab-content="' + target + '"]');
        if (content) content.classList.add('active');
      });
    });
  }

  /* ---- SLIDER ---- */
  function initSlider(sliderEl) {
    var track = sliderEl.querySelector('.atl-categories-track');
    var prevBtn = sliderEl.querySelector('.atl-slider-btn.prev');
    var nextBtn = sliderEl.querySelector('.atl-slider-btn.next');
    var dots = sliderEl.querySelectorAll('.atl-slider-dot');
    if (!track) return;
    var cards = track.querySelectorAll('.atl-category-card');
    var cardWidth = cards[0] ? cards[0].offsetWidth + 20 : 280;
    var current = 0;
    var max = Math.max(0, cards.length - 4);

    function goTo(idx) {
      current = Math.max(0, Math.min(idx, max));
      track.style.transform = 'translateX(-' + (current * cardWidth) + 'px)';
      dots.forEach(function (d, i) { d.classList.toggle('active', i === current); });
    }

    if (prevBtn) prevBtn.addEventListener('click', function () { goTo(current - 1); });
    if (nextBtn) nextBtn.addEventListener('click', function () { goTo(current + 1); });
    dots.forEach(function (d, i) { d.addEventListener('click', function () { goTo(i); }); });
  }

  document.querySelectorAll('.atl-categories-slider').forEach(initSlider);

  /* ---- RESULTS CAROUSEL ---- */
  function initResultsCarousel() {
    var grid = document.querySelector('.atl-results-grid');
    if (!grid) return;
    var prevBtn = grid.parentElement.querySelector('.atl-nav-arrow.prev');
    var nextBtn = grid.parentElement.querySelector('.atl-nav-arrow.next');
    var cards = grid.querySelectorAll('.atl-result-card');
    var offset = 0;
    var visible = 4;

    function update() {
      cards.forEach(function (c, i) {
        c.style.display = (i >= offset && i < offset + visible) ? '' : 'none';
      });
    }

    update();
    if (prevBtn) prevBtn.addEventListener('click', function () { if (offset > 0) { offset--; update(); } });
    if (nextBtn) nextBtn.addEventListener('click', function () { if (offset < cards.length - visible) { offset++; update(); } });
  }

  initResultsCarousel();

  /* ---- MULTI-PANEL CASCADING SIDEMENU ---- */
  function initSideMenu() {
    var menuBtn = document.querySelector('.atl-menu-btn');
    var sidemenu = document.querySelector('.atl-sidemenu');
    if (!menuBtn || !sidemenu) return;
    var overlay = sidemenu.querySelector('.atl-sidemenu-overlay');
    var closeBtn = sidemenu.querySelector('.atl-sm-close');
    var backBtn = sidemenu.querySelector('.atl-sm-back');
    var l1 = sidemenu.querySelector('.atl-sm-l1');
    var l2Panels = sidemenu.querySelectorAll('.atl-sm-l2');
    var l3Panels = sidemenu.querySelectorAll('.atl-sm-l3');

    // Below 800px the drawer shows one full-width panel at a time (see the
    // @media (max-width:800px) block in atlasco.css); [data-sm-level] tells
    // that CSS which of L1/L2/L3 is the "current" screen. Above 800px this
    // attribute is inert — desktop keeps the side-by-side cascade untouched.
    function setLevel(level) {
      sidemenu.setAttribute('data-sm-level', level);
    }

    function positionCloseBtn() {
      if (!closeBtn) return;
      var l2Open = sidemenu.querySelector('.atl-sm-l2.atl-sm-active');
      var l3Open = sidemenu.querySelector('.atl-sm-l3.atl-sm-active');
      var x = 220;  // L1 width
      if (l2Open) x += 260;
      if (l3Open) x += 280;
      closeBtn.style.left = x + 'px';
    }

    function clearActives() {
      sidemenu.querySelectorAll('.atl-sm-item.atl-sm-active').forEach(function (i) {
        i.classList.remove('atl-sm-active');
      });
      l2Panels.forEach(function (p) { p.classList.remove('atl-sm-active'); });
      l3Panels.forEach(function (p) { p.classList.remove('atl-sm-active'); });
      positionCloseBtn();
    }
    function openMenu() {
      clearActives();
      if (l1) l1.classList.add('atl-sm-active');
      setLevel('l1');
      sidemenu.classList.add('open');
      document.body.classList.add('atl-menu-open');
    }
    function closeMenu() {
      sidemenu.classList.remove('open');
      document.body.classList.remove('atl-menu-open');
    }
    function showPanel(name, level) {
      var nodes = level === 2 ? l2Panels : l3Panels;
      nodes.forEach(function (p) {
        if (p.dataset.smPanel === name) p.classList.add('atl-sm-active');
        else p.classList.remove('atl-sm-active');
      });
      setLevel(level === 2 ? 'l2' : 'l3');
      positionCloseBtn();
    }
    // Back button (mobile/tablet only, hidden by CSS at l1): L3 -> L2 just
    // steps the visible level back (the L2 panel is still .atl-sm-active,
    // it was never cleared when L3 opened). L2 -> L1 also only steps the
    // level back — L1 keeps its own active item highlighted.
    function goBack() {
      var level = sidemenu.getAttribute('data-sm-level');
      if (level === 'l3') {
        setLevel('l2');
      } else if (level === 'l2') {
        setLevel('l1');
      }
    }

    menuBtn.addEventListener('click', function (e) { e.preventDefault(); openMenu(); });
    if (closeBtn) closeBtn.addEventListener('click', closeMenu);
    if (backBtn) backBtn.addEventListener('click', goBack);
    if (overlay) overlay.addEventListener('click', closeMenu);

    // Wire L1 items (in panel 1). Items with data-sm-target have BOTH a main
    // landing page (href) and a sub-panel: the chevron opens the sub-panel,
    // tapping the label navigates to the main page. Expose openL1Panel so the
    // top desktop nav can trigger the same sub-panel open.
    function openL1Panel(item) {
      var tgt = item.dataset.smTarget;
      if (!tgt) return;
      l1.querySelectorAll('.atl-sm-item').forEach(function (i) {
        i.classList.remove('atl-sm-active');
      });
      item.classList.add('atl-sm-active');
      // Clear L3 when L2 changes
      l3Panels.forEach(function (p) { p.classList.remove('atl-sm-active'); });
      showPanel(tgt, 2);
    }
    sidemenu._openL1Panel = openL1Panel;
    if (l1) {
      l1.querySelectorAll('.atl-sm-item').forEach(function (item) {
        item.addEventListener('click', function (e) {
          var tgt = item.dataset.smTarget;
          if (tgt) {
            var href = item.getAttribute('href');
            var onChev = e.target.closest && e.target.closest('.atl-sm-chev');
            if (onChev || !href || href === '#') {
              // chevron (or no real page) → open the sub-panel, don't navigate
              e.preventDefault();
              openL1Panel(item);
            } else {
              // label → go to the main landing page, close menu after
              setTimeout(closeMenu, 50);
            }
          } else {
            // leaf — let navigation proceed, close menu after
            setTimeout(closeMenu, 50);
          }
        });
      });
    }

    // Wire L2 items — those with data-sm-target open L3
    l2Panels.forEach(function (panel) {
      panel.querySelectorAll('.atl-sm-item').forEach(function (item) {
        item.addEventListener('click', function (e) {
          var tgt = item.dataset.smTarget;
          if (tgt) {
            e.preventDefault();
            panel.querySelectorAll('.atl-sm-item').forEach(function (i) {
              i.classList.remove('atl-sm-active');
            });
            item.classList.add('atl-sm-active');
            showPanel(tgt, 3);
          } else {
            setTimeout(closeMenu, 50);
          }
        });
      });
    });

    // Leaf links in L3 just navigate
    l3Panels.forEach(function (panel) {
      panel.querySelectorAll('.atl-sm-item').forEach(function (a) {
        a.addEventListener('click', function () { setTimeout(closeMenu, 50); });
      });
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && sidemenu.classList.contains('open')) closeMenu();
    });
  }

  /* ---- HEADER SCROLL-CONDENSE ----
     Inline media queries can't do this, so toggle a class imperatively when
     the page is scrolled past the threshold; CSS handles the height/logo/shadow. */
  function initHeaderCondense() {
    var nav = document.querySelector('.atl-navbar');
    if (!nav) return;
    var ticking = false;
    function apply() {
      nav.classList.toggle('is-condensed', scrollTop() > 16);
      ticking = false;
    }
    scrollTarget().addEventListener('scroll', function () {
      if (!ticking) { window.requestAnimationFrame(apply); ticking = true; }
    }, { passive: true });
    apply();
  }

  /* ---- STAT COUNTERS ---- */
  function animateCount(el) {
    var target = parseInt(el.dataset.target || '0', 10);
    var suffix = el.dataset.suffix || '';
    var duration = 1500;
    var start = null;
    function step(ts) {
      if (!start) start = ts;
      var progress = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.floor(target * eased).toLocaleString() + suffix;
      if (progress < 1) requestAnimationFrame(step);
      else el.textContent = target.toLocaleString() + suffix;
    }
    requestAnimationFrame(step);
  }
  function initCounters() {
    var stats = document.querySelector('.atl-stats');
    if (!stats) return;
    var numbers = stats.querySelectorAll('.atl-stat-number[data-target]');
    if (!numbers.length) return;
    if (!('IntersectionObserver' in window)) {
      numbers.forEach(animateCount);
      return;
    }
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          numbers.forEach(animateCount);
          observer.disconnect();
        }
      });
    }, { threshold: 0.3 });
    observer.observe(stats);
  }

  /* ---- CONTACT FORM ----
     This used to preventDefault() and fake a "Sending... / Request Sent!"
     animation with a setTimeout, without ever submitting the form - found
     while wiring the CRM lead integration: the real POST to /contact/submit
     (which now also creates a crm.lead) was never actually reaching the
     server for any real visitor, only the fake client-side animation ran.
     Just disable the button on click so it can't be double-submitted while
     the real page reload (with the server-rendered success/error banner
     already built into contact_submit) is in flight. -->
  var contactForm = document.querySelector('#atl-contact-form');
  if (contactForm) {
    contactForm.addEventListener('submit', function () {
      var btn = this.querySelector('.btn-submit');
      btn.textContent = 'Sending...';
      btn.disabled = true;
    });
  }

  /* ---- ENROLLMENT FORM ---- */
  var enrollForm = document.querySelector('#atl-enroll-form');
  if (enrollForm) {
    enrollForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var btn = this.querySelector('.btn-submit');
      btn.textContent = 'Submitting...';
      btn.disabled = true;
      setTimeout(function () {
        btn.textContent = 'Enrollment Request Sent!';
        btn.style.background = '#0d9488';
        enrollForm.reset();
      }, 1500);
    });
  }

  /* ---- HAZEM #3 + #21: Scroll-triggered fade-in ----
       v6 2026-05-25: history page had 13/28 fx nodes stuck at opacity:0
       on /about/history. Root cause: threshold 0.15 + negative bottom
       rootMargin (-40px) combined with tall timeline items meant some
       items scrolled past the trigger window in some browsers/timings
       before the observer fired. data-fx-delay values up to 1260ms made
       it worse by stalling reveal even once the observer did fire.
       Fix: lower threshold to 0.05 + drop negative rootMargin + add a
       3s belt-and-braces failsafe that force-reveals anything that is
       still hidden after the user has had time to scroll. */
  function initFadeInOnScroll() {
    var fxNodes = document.querySelectorAll('[data-fx^="fade-"]');
    if (!fxNodes.length) return;
    if (!('IntersectionObserver' in window)) {
      fxNodes.forEach(function (n) { n.classList.add('atl-fx-in'); });
      return;
    }
    var prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) {
      fxNodes.forEach(function (n) { n.classList.add('atl-fx-in'); });
      return;
    }
    var observer = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          var el = entry.target;
          var delay = parseInt(el.dataset.fxDelay || '0', 10);
          // clamp delay so deeply-staggered timeline items still reveal
          // promptly once their row enters the viewport
          if (delay > 400) { delay = 400; }
          if (delay > 0) {
            setTimeout(function () { el.classList.add('atl-fx-in'); }, delay);
          } else {
            el.classList.add('atl-fx-in');
          }
          obs.unobserve(el);
        }
      });
    }, { threshold: 0.05, rootMargin: '0px' });
    fxNodes.forEach(function (n) {
      try { observer.observe(n); } catch (e) { n.classList.add('atl-fx-in'); }
    });
    // belt-and-braces: any node still hidden after 3s of scroll exposure
    // gets force-revealed so users never see a permanently-blank section
    setTimeout(function () {
      fxNodes.forEach(function (n) {
        if (!n.classList.contains('atl-fx-in')) {
          n.classList.add('atl-fx-in');
        }
      });
    }, 3000);
  }

  /* ---- HAZEM #21: Subtle hero parallax (background translateY on scroll) ---- */
  function initHeroParallax() {
    var hero = document.querySelector('.atl-hero[data-parallax="hero"]');
    if (!hero) return;
    var bg = hero.querySelector('.atl-hero-bg');
    if (!bg) return;
    var prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) return;
    var ticking = false;
    function update() {
      var rect = hero.getBoundingClientRect();
      if (rect.bottom < 0 || rect.top > window.innerHeight) {
        ticking = false;
        return;
      }
      // shift bg up to 60px slower than scroll
      var offset = Math.max(-60, Math.min(0, rect.top * 0.18));
      bg.style.transform = 'translate3d(0,' + (-offset) + 'px,0)';
      ticking = false;
    }
    scrollTarget().addEventListener('scroll', function () {
      if (!ticking) {
        window.requestAnimationFrame(update);
        ticking = true;
      }
    }, { passive: true });
    update();
  }

  /* ---- HAZEM #5: Industries horizontal scroll (prev/next + drag) ---- */
  function initIndustriesScroller() {
    document.querySelectorAll('[data-industries-scroller="1"]').forEach(function (wrap) {
      var track = wrap.querySelector('.atl-industries-track');
      var prev = wrap.querySelector('.atl-ind-nav.prev');
      var next = wrap.querySelector('.atl-ind-nav.next');
      if (!track) return;
      var card = track.querySelector('.atl-industry-card');
      var step = card ? (card.offsetWidth + 16) : 336;

      function updateNav() {
        if (!prev || !next) return;
        prev.disabled = track.scrollLeft <= 4;
        next.disabled = track.scrollLeft + track.clientWidth >= track.scrollWidth - 4;
      }
      if (prev) prev.addEventListener('click', function () {
        track.scrollBy({ left: -step, behavior: 'smooth' });
      });
      if (next) next.addEventListener('click', function () {
        track.scrollBy({ left: step, behavior: 'smooth' });
      });
      track.addEventListener('scroll', function () {
        window.requestAnimationFrame(updateNav);
      }, { passive: true });

      /* drag-to-scroll fallback for non-touch pointers */
      var isDown = false;
      var startX = 0;
      var startScroll = 0;
      var moved = false;
      track.addEventListener('mousedown', function (e) {
        isDown = true;
        moved = false;
        startX = e.pageX;
        startScroll = track.scrollLeft;
        track.classList.add('atl-dragging');
      });
      window.addEventListener('mouseup', function () {
        if (isDown) {
          isDown = false;
          track.classList.remove('atl-dragging');
        }
      });
      track.addEventListener('mouseleave', function () {
        if (isDown) {
          isDown = false;
          track.classList.remove('atl-dragging');
        }
      });
      track.addEventListener('mousemove', function (e) {
        if (!isDown) return;
        var dx = e.pageX - startX;
        if (Math.abs(dx) > 5) moved = true;
        track.scrollLeft = startScroll - dx;
      });
      /* suppress click after drag */
      track.addEventListener('click', function (e) {
        if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; }
      }, true);

      updateNav();
    });
  }

  /* ---- HAZEM #10: Solutions categories slide right on scroll ---- */
  function initSolutionsScrollX() {
    var section = document.querySelector('.atl-solutions[data-scrollx="categories"]');
    if (!section) return;
    var tabList = section.querySelector('.atl-tab-list');
    if (!tabList) return;
    var prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReduced) return;
    if (window.innerWidth < 900) return; // skip on mobile
    var ticking = false;
    var maxShift = 60; // cap horizontal slide so cards don't drift off-screen

    function update() {
      var rect = section.getBoundingClientRect();
      var vh = window.innerHeight;
      if (rect.bottom < 0 || rect.top > vh) {
        ticking = false;
        return;
      }
      // progress: 0 when section top enters viewport bottom, 1 when section bottom leaves top
      var total = rect.height + vh;
      var traveled = vh - rect.top;
      var progress = Math.max(0, Math.min(1, traveled / total));
      var shift = (progress - 0.5) * 2 * maxShift; // -maxShift -> +maxShift
      shift = Math.max(-maxShift, Math.min(maxShift, shift));
      tabList.style.transform = 'translate3d(' + shift + 'px,0,0)';
      ticking = false;
    }
    scrollTarget().addEventListener('scroll', function () {
      if (!ticking) {
        window.requestAnimationFrame(update);
        ticking = true;
      }
    }, { passive: true });
    update();
  }

  /* ---- INDUSTRIES — PINNED VERTICAL→HORIZONTAL SCROLL ----
     Root cause of the white-space-on-zoom bug this replaces: the section's
     reserved scroll height used to be a hardcoded constant (a fixed "820px
     box" + a fixed "700px runway"), which has no relationship to the
     ACTUAL horizontal distance the card track needs to travel. That real
     distance depends on track.scrollWidth and the viewport's own width —
     both of which change under browser zoom — so whenever the hardcoded
     constants didn't match the real numbers at a given zoom level, the
     drag either finished before the browser's own sticky-release point
     (a frozen dead zone until the leftover reserved scroll ran out) or
     the box itself sat shorter than the real viewport while pinned. Both
     read as blank/white space that grows with zoom and — for the dead
     zone specifically — visibly "resolves" once you scroll enough to
     use up the mismatch, matching exactly what was reported.
     Fix: measure the real distance from the rendered DOM (track.scrollWidth
     minus the actual visible width, using computed padding rather than a
     hardcoded number) and the real viewport height, then set the section's
     reserved height to exactly viewportHeight + thatDistance — so the
     browser's own sticky-release point and the drag's own completion
     point are mathematically guaranteed to coincide, at any zoom level.
     Re-measured on resize (which fires on zoom) and again after the
     window's 'load' event, since fonts/images finishing can still shift
     card widths after the first measurement. */
  function initPinnedIndustriesScroll() {
    var section = document.querySelector('[data-pinned-h-scroll]');
    if (!section) return;
    var inner = section.querySelector('.atl-industries-pinned-inner');
    var track = section.querySelector('.atl-industries-track');
    if (!inner || !track) return;

    // Skip on mobile + reduced-motion (CSS falls back to native horiz scroll)
    if (window.matchMedia('(max-width: 800px)').matches) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    var SCROLL_RATIO = 0.5; // vertical scroll px per horizontal px (1 = 1:1)
    var maxX = 0;        // horizontal distance the track must travel
    var scrollableH = 0; // vertical scroll distance reserved to drive it

    function measure() {
      // clientWidth already includes the inner's own padding, so subtract
      // the real computed padding (not a hardcoded number) to get the
      // actual visible width available for cards.
      var cs = getComputedStyle(inner);
      var padL = parseFloat(cs.paddingLeft) || 0;
      var padR = parseFloat(cs.paddingRight) || 0;
      var visibleW = inner.clientWidth - padL - padR;
      var trackW = track.scrollWidth;
      maxX = Math.max(0, trackW - visibleW);
      // Vertical scroll reserved to drive the drag = a fraction of the
      // horizontal distance (SCROLL_RATIO), so the cards travel faster than
      // 1:1 and the pinned section is released sooner. Raise towards 1 for
      // a slower/longer drag, lower for a quicker one.
      scrollableH = maxX * SCROLL_RATIO;
      // inner is height:100vh (see CSS) so it always exactly covers the
      // viewport while pinned; reserving exactly that plus the scroll
      // distance means the browser's sticky-release point and the
      // drag's own end point land on the same scroll position.
      section.style.height = (window.innerHeight + scrollableH) + 'px';
    }

    var ticking = false;
    function update() {
      if (scrollableH <= 0) {
        track.style.transform = '';
        ticking = false;
        return;
      }
      var rect = section.getBoundingClientRect();
      var progress = Math.min(1, Math.max(0, -rect.top / scrollableH));
      var x = progress * maxX;
      track.style.transform = 'translate3d(' + (-x) + 'px, 0, 0)';
      ticking = false;
    }

    function remeasureAndUpdate() {
      measure();
      update();
    }

    scrollTarget().addEventListener('scroll', function () {
      if (!ticking) {
        requestAnimationFrame(update);
        ticking = true;
      }
    }, { passive: true });
    // Re-measure (not just re-render) on resize: this is what makes zoom
    // changes correct live, since zooming fires a resize event and changes
    // every width/height measurement above — a plain re-render with the
    // old distances would keep the stale, now-wrong reserved height.
    window.addEventListener('resize', remeasureAndUpdate, { passive: true });
    // Fonts/images finishing after the first measurement can still change
    // card widths (the clamp(...) sizing and any image-driven layout), so
    // measure once more once everything has actually finished loading.
    window.addEventListener('load', remeasureAndUpdate, { passive: true });

    measure();
    update();
  }

  /* ---- CHAIRMAN MESSAGE WORD-BY-WORD TYPEWRITER ----
     WAEL-AI 2026-06-17 (design ruling: Yasmine-AI). Scoped to .atl-cmsg-body only.
     Strategy (the no-reflow / no-drop-cap-flicker key): the FULL text stays in the
     DOM at all times (progressive enhancement — no-JS/robots see all 5 paragraphs).
     JS only wraps each word in an inline <span class="atl-cw"> via text-node splitting,
     then reveals words by toggling opacity (NEVER textContent/display). Because every
     word occupies its final layout slot from frame zero (invisible, not absent), the
     card box is full-height before the first reveal tick => zero layout shift. The
     ::first-letter drop-cap stays attached to P1's first real text node the whole time
     (P1 first word shown at t=0), so it can't detach or flicker. */
  function initChairmanTypewriter() {
    var body = document.querySelector('.atl-cmsg-body');
    if (!body) return;
    var paras = Array.prototype.slice.call(body.querySelectorAll('p'));
    if (!paras.length) return;

    var prefersReduced = window.matchMedia &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Wrap each word of each paragraph in an inline span, preserving whitespace.
    // We only touch text nodes so element structure (and the drop-cap anchor) is intact.
    var allWords = []; // flat reveal order across all paragraphs
    paras.forEach(function (p) {
      var raw = p.textContent;
      // tokenize into [word, space, word, space, ...] keeping spaces as plain text
      var tokens = raw.split(/(\s+)/);
      var frag = document.createDocumentFragment();
      tokens.forEach(function (tok) {
        if (tok === '') return;
        if (/^\s+$/.test(tok)) {
          frag.appendChild(document.createTextNode(tok));
        } else {
          var s = document.createElement('span');
          s.className = 'atl-cw';
          s.textContent = tok;
          frag.appendChild(s);
          allWords.push(s);
        }
      });
      p.textContent = '';
      p.appendChild(frag);
    });
    if (!allWords.length) return;

    // Reduced motion / no IO support => show everything instantly, no caret, no typing.
    if (prefersReduced || !('IntersectionObserver' in window)) {
      body.classList.add('is-typed-done');
      allWords.forEach(function (w) { w.classList.add('is-shown'); });
      return;
    }

    // Caret element (decorative). Lives at the end of the active paragraph.
    var caret = document.createElement('span');
    caret.className = 'atl-cmsg-caret';
    caret.setAttribute('aria-hidden', 'true');

    // Drop-cap anchor: reveal P1's first word immediately so ::first-letter paints gold
    // and is stable for the whole animation (it must never be the thing that "appears").
    allWords[0].classList.add('is-shown');

    var i = 1;                 // next word index to reveal (0 already shown)
    var started = false;
    var finished = false;
    var ioTriggerTs = 0;
    var BASE_MS = 130;         // per-word base — slowed per Youssef 2026-06-17 [Wael-AI]
    var JITTER_MS = 25;        // +/- jitter for human feel
    var PARA_PAUSE_MS = 1300;  // inter-paragraph pause — slowed per Youssef 2026-06-17 [Wael-AI]
    var INITIAL_DELAY_MS = 350;

    function placeCaretAfter(span) {
      if (caret.parentNode) caret.parentNode.removeChild(caret);
      if (span && span.parentNode) {
        span.parentNode.insertBefore(caret, span.nextSibling);
      }
    }

    function finish() {
      if (finished) return;
      finished = true;
      allWords.forEach(function (w) { w.classList.add('is-shown'); });
      body.classList.add('is-typed-done');
      // hold briefly, then fade the caret out
      setTimeout(function () { caret.classList.add('is-gone'); }, 600);
      detachSkip();
    }

    function step() {
      if (finished) return;
      if (i >= allWords.length) { finish(); return; }
      var w = allWords[i];
      w.classList.add('is-shown');
      placeCaretAfter(w);
      // detect paragraph boundary: pause longer when the NEXT word lives in a new <p>
      var crossesPara = (i + 1 < allWords.length) &&
        (allWords[i + 1].parentNode !== w.parentNode);
      i++;
      var delay = BASE_MS + (Math.random() * 2 - 1) * JITTER_MS;
      if (crossesPara) delay += PARA_PAUSE_MS;
      setTimeout(step, delay);
    }

    // ---- skip handling (click immediate; scroll only after initial delay) ----
    function onSkip() { finish(); }
    function onScrollSkip(e) {
      // ignore the scroll that itself triggered the IO (race guard)
      if (e && e.timeStamp && (e.timeStamp - ioTriggerTs) < 400) return;
      finish();
    }
    function attachClickSkip() {
      body.addEventListener('click', onSkip, { once: true });
    }
    function attachScrollSkip() {
      scrollTarget().addEventListener('scroll', onScrollSkip, { passive: true });
    }
    function detachSkip() {
      body.removeEventListener('click', onSkip);
      scrollTarget().removeEventListener('scroll', onScrollSkip);
    }

    function begin() {
      if (started) return;
      started = true;
      body.classList.add('is-typing');
      placeCaretAfter(allWords[0]);
      attachClickSkip();        // deliberate click is genuine skip intent — bind now
      setTimeout(function () {
        attachScrollSkip();     // bind scroll-skip only after the trigger scroll settles
        step();
      }, INITIAL_DELAY_MS);
    }

    function arm() {
      var obs = new IntersectionObserver(function (entries, o) {
        entries.forEach(function (e) {
          if (e.isIntersecting && !started) {
            ioTriggerTs = e.time || (window.performance && performance.now()) || 0;
            o.disconnect();
            begin();
          }
        });
      }, { threshold: 0.35 });
      obs.observe(body);
    }

    // Wait for the cursive webfont so word boxes are measured/laid out in the final
    // font (avoids any FOUT-driven wrap change). Layout is reserved regardless because
    // all words are present; this just makes the first paint match the final paint.
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(arm);
      // failsafe: arm anyway if fonts.ready stalls
      setTimeout(function () { if (!started) arm(); }, 1500);
    } else {
      arm();
    }
  }

  /* ---- CONTACT FORM: pre-select industry from ?industry= URL param ---- */
  function initContactIndustryPrefill() {
    var select = document.querySelector('form select[name="industry"]');
    if (!select) return;
    var params = new URLSearchParams(window.location.search);
    var slug = (params.get('industry') || '').trim().toLowerCase();
    if (!slug) return;
    var slugMap = {
      'oil-gas': 'Oil & Gas',
      'pharmaceutical': 'Pharmaceutical',
      'medical': 'Medical',
      'food-beverage': 'Food & Beverage',
      'steel': 'Steel',
      'power-generation': 'Power Generation',
      'manufacturing': 'Manufacturing'
    };
    var label = slugMap[slug];
    if (!label) { select.value = 'Other'; return; }
    for (var i = 0; i < select.options.length; i++) {
      if (select.options[i].text.trim().toLowerCase() === label.toLowerCase()) {
        select.selectedIndex = i;
        return;
      }
    }
    select.value = 'Other';
  }

  /* ---- PARTNERS EDITORIAL COMB — v8 (2026-06-05) ---- */
  function initPartnerComb() {
    var comb = document.getElementById('atlPartnerComb');
    if (!comb) return;
    // Backed by content.home_partners_showall_url (see homepage.xml), with
    // '/partners' as a fallback so this still works if the attribute is
    // ever missing (e.g. a stale cached page).
    var showAllUrl = comb.getAttribute('data-showall-url') || '/partners';

    // ClickUp 869eg533x: this used to be a 15-entry literal array here (the
    // 23 original partners were hardcoded, not backend records, so the
    // honeycomb had no ORM data to read). Now that every atlasco.partner
    // record with show_on_home=True IS the full set (the original 23
    // migrated by AtlascoPartner._seed_legacy_partners(), plus anything
    // added since), this reads that list straight from the server-rendered
    // data-partners JSON (see the homepage() route) — nothing hardcoded.
    var PARTNERS = [];
    try {
      var _comb = document.getElementById('atlPartnerComb');
      if (_comb && _comb.dataset && _comb.dataset.partners) {
        PARTNERS = JSON.parse(_comb.dataset.partners) || [];
      }
    } catch (e) { /* comb just renders empty if this ever fails */ }

    function buildComb() {
      comb.innerHTML = '';
      var CW = comb.clientWidth || 600;
      // 4-column flat-top honeycomb: CW = 3*0.75*W + W = 3.25W
      var W = CW / 3.25;
      var Hbox = W * Math.sqrt(3) / 2;
      var colStep = W * 0.75;
      var rowStep = Hbox;
      // Was a hardcoded [4, 4, 4, 4] (exactly 16 cells: 15 partners + show
      // all). W above is derived assuming exactly 4 columns fit CW, so a
      // 5th+ column would overflow the container — grow ROWS instead,
      // keeping 4 columns fixed; the comb's height already adapts (see
      // totalH below), so a taller strip is free but a wider one isn't.
      // Identical [4,4,4,4] output for today's 15 partners.
      var totalCells = PARTNERS.length + 1; // + the "show all" CTA tile
      var NUM_COLS = 4;
      var baseRows = Math.floor(totalCells / NUM_COLS);
      var extraCols = totalCells % NUM_COLS; // LAST N columns get one extra row, so
      var COLS = [];                          // the CTA lands bottom-right like before
      for (var _c = 0; _c < NUM_COLS; _c++) {
        COLS.push(baseRows + (_c >= NUM_COLS - extraCols ? 1 : 0));
      }
      var cellPositions = [];
      COLS.forEach(function(len, col) {
        var yShift = (col % 2) ? rowStep / 2 : 0;
        for (var r = 0; r < len; r++) {
          cellPositions.push({x: col * colStep, y: r * rowStep + yShift});
        }
      });
      cellPositions.sort(function(a, b) { return (a.y - b.y) || (a.x - b.x); });
      var totalH = 0;
      cellPositions.forEach(function(p) { totalH = Math.max(totalH, p.y + Hbox); });
      comb.style.height = totalH + 'px';

      cellPositions.forEach(function(pos, i) {
        var isCTA = (i === cellPositions.length - 1);
        var hex = document.createElement('a');
        hex.className = 'atl-pe-hex ' + (isCTA ? 'atl-pe-hex-cta' : 'atl-pe-hex-partner');
        hex.href = isCTA ? showAllUrl : PARTNERS[i].href;
        hex.style.cssText = 'left:' + pos.x + 'px;top:' + pos.y + 'px;width:' + W + 'px;height:' + Hbox + 'px;transition-delay:' + (0.22 + i * 0.035) + 's';

        if (isCTA) {
          hex.innerHTML = '<div class="atl-pe-hex-frame"></div>' +
            '<div class="atl-pe-hex-cell atl-pe-hex-cell-cta">' +
            '<div class="atl-pe-hex-name" style="font-size:' + (W * 0.072).toFixed(1) + 'px">Show all<br>partners</div>' +
            '<div class="atl-pe-hex-circ">&#8594;</div></div>';
        } else {
          var p = PARTNERS[i];
          hex.innerHTML = '<div class="atl-pe-hex-frame"></div>' +
            '<div class="atl-pe-hex-cell">' +
            '<img class="atl-pe-hex-logo' + (p.cls ? ' ' + p.cls : '') + '" src="' + p.img + '" alt="' + p.n + '" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'block\'"/>' +
            '<div class="atl-pe-hex-name" style="display:none;font-size:' + (W * 0.095).toFixed(1) + 'px">' + p.n + '</div>' +
            '<div class="atl-pe-hex-disc" style="font-size:' + (W * 0.050).toFixed(1) + 'px">' + p.d + '</div></div>';
        }
        comb.appendChild(hex);
      });

      // reveal
      requestAnimationFrame(function() {
        requestAnimationFrame(function() {
          comb.querySelectorAll('.atl-pe-hex').forEach(function(h) {
            h.classList.add('atl-pe-hex-visible');
          });
        });
      });
    }

    buildComb();
    var rto;
    window.addEventListener('resize', function() {
      clearTimeout(rto);
      rto = setTimeout(buildComb, 140);
    });
  }

  /* ---- Top nav items with sub-pages: open the burger side menu at their
         section. Inside the menu the label navigates to the main page and the
         chevron opens the sub-panel (see initSideMenu). ---- */
  function initNavSubnav() {
    var menuBtn = document.querySelector('.atl-menu-btn');
    var sidemenu = document.querySelector('.atl-sidemenu');
    document.querySelectorAll('.atl-nav-links a[data-sm-open]').forEach(function (link) {
      link.addEventListener('click', function (e) {
        e.preventDefault();
        var target = link.getAttribute('data-sm-open');
        if (menuBtn) menuBtn.click();
        var item = document.querySelector('.atl-sm-l1 .atl-sm-item[data-sm-target="' + target + '"]');
        if (item && sidemenu && sidemenu._openL1Panel) {
          setTimeout(function () { sidemenu._openL1Panel(item); }, 0);
        }
      });
    });
  }

  /* ---- Active nav highlight: mark the top-level nav link for the current page ---- */
  function initActiveNav() {
    var links = document.querySelectorAll('.atl-nav-links > li > a');
    if (!links.length) return;
    var path = window.location.pathname.replace(/\/+$/, '') || '/';
    links.forEach(function (a) {
      var href = (a.getAttribute('href') || '').replace(/[?#].*$/, '').replace(/\/+$/, '');
      if (!href || href === '/') return;
      if (path === href || path.indexOf(href + '/') === 0) {
        a.classList.add('active');
      }
    });
  }

  /* ---- RELIABILITY CARDS — staggered scroll entrance (client animation handoff 2026-07-25) ---- */
  function initReliabilityCards() {
    var grid = document.querySelector('.atl-reliability-cards');
    if (!grid) return;
    var cards = Array.prototype.slice.call(grid.querySelectorAll('.atl-reliability-card'));
    if (!cards.length) return;
    function showAll() { cards.forEach(function (c) { c.classList.add('is-in'); }); }
    var prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    grid.classList.add('rc-anim'); // arms the hidden initial state (CSS)
    if (prefersReduced || !('IntersectionObserver' in window)) { showAll(); return; }
    var step = 110;
    var observer = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        var i = cards.indexOf(el);
        obs.unobserve(el);
        setTimeout(function () { el.classList.add('is-in'); }, Math.max(0, i) * step);
      });
    }, { threshold: 0.2, rootMargin: '0px 0px -8% 0px' });
    cards.forEach(function (c) {
      try { observer.observe(c); } catch (e) { c.classList.add('is-in'); }
    });
    // failsafe: never leave a card permanently hidden
    setTimeout(function () {
      cards.forEach(function (c) { if (!c.classList.contains('is-in')) c.classList.add('is-in'); });
    }, 1600);
  }

  /* ---- HOMEPAGE HERO CAROUSEL (restored 2026-07-27) ---- */
  function initHeroCarousel() {
    var root = document.querySelector('.atl-hero--carousel');
    if (!root) return;
    var slides = [].slice.call(root.querySelectorAll('.atl-hero-slide'));
    if (slides.length < 2) return;
    var dots = [].slice.call(root.querySelectorAll('.atl-hero-dot'));
    var prev = root.querySelector('.atl-hero-nav--prev');
    var next = root.querySelector('.atl-hero-nav--next');
    var i = 0, timer = null;
    var DELAY = 6000;
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function show(n) {
      i = (n + slides.length) % slides.length;
      slides.forEach(function (s, k) { s.classList.toggle('is-active', k === i); });
      dots.forEach(function (d, k) { d.classList.toggle('is-active', k === i); });
    }
    function stop() { if (timer) { clearInterval(timer); timer = null; } }
    function restart() { stop(); if (!reduce) timer = setInterval(function () { show(i + 1); }, DELAY); }
    function go(n) { show(n); restart(); }

    // In the Website editor every slide is stacked and visible (see CSS) so
    // the client can edit each one — never autoplay there.
    if (document.body.classList.contains('editor_enable')) { show(0); return; }

    if (prev) prev.addEventListener('click', function () { go(i - 1); });
    if (next) next.addEventListener('click', function () { go(i + 1); });
    dots.forEach(function (d, k) { d.addEventListener('click', function () { go(k); }); });
    root.addEventListener('mouseenter', stop);
    root.addEventListener('mouseleave', restart);
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) { stop(); } else { restart(); }
    });

    var x0 = null;
    root.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    root.addEventListener('touchend', function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 45) { go(dx < 0 ? i + 1 : i - 1); }
      x0 = null;
    }, { passive: true });

    show(0);
    restart();
  }

  /* ---- INIT (handles both pre- and post-DOMContentLoaded loading) ---- */
  function bootAtlasco() {
    initHeroCarousel();
    initReliabilityCards();
    initTabs();
    document.querySelectorAll('.atl-categories-slider').forEach(initSlider);
    initResultsCarousel();
    initSideMenu();
    initHeaderCondense();
    initNavSubnav();
    initActiveNav();
    initCounters();
    initFadeInOnScroll();
    initHeroParallax();
    initIndustriesScroller();
    initPinnedIndustriesScroll();
    initSolutionsScrollX();
    initChairmanTypewriter(); // WAEL-AI 2026-06-17 — word-by-word reveal on .atl-cmsg-body (Youssef request)
    initContactIndustryPrefill();
    initPartnerComb();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bootAtlasco);
  } else {
    bootAtlasco();
  }
})();
