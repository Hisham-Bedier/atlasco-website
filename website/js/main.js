/* Atlasco Egypt — Main JavaScript */
(function () {
  'use strict';

  /* ======= MEGA SIDEBAR ======= */
  var sidebarData = [
    {
      label: 'About', href: 'about.html',
      desc: 'Our story and people',
      subs: [
        { label: 'Our History', href: 'history.html', items: ['Company Timeline', 'Founding Story', '35 Years of Growth'] },
        { label: 'Our People', href: 'team.html', items: ['Leadership Team', 'Board of Directors', 'Engineering Team'] },
        { label: 'Recognition', href: 'about.html', items: ['Awards & Certifications', 'Industry Memberships', 'Media Coverage'] }
      ]
    },
    {
      label: 'Industries', href: 'industries.html',
      desc: 'Sectors we serve across Egypt',
      subs: [
        { label: 'Process Industries', items: ['Oil & Gas', 'Petrochemicals', 'Pharmaceuticals'] },
        { label: 'Heavy Industry', items: ['Cement & Mining', 'Steel & Metals', 'Power Generation'] },
        { label: 'Consumer Industries', items: ['FMCG & Food', 'Textiles', 'Water Treatment'] }
      ]
    },
    {
      label: 'Products', href: 'products.html',
      desc: 'World-class industrial equipment',
      subs: [
        { label: 'Compressed Air', items: ['Rotary Screw Compressors', 'Oil-Free Compressors', 'Nitrogen Generators'] },
        { label: 'Fluid Power', items: ['Hydraulic Filtration', 'Filter Housings', 'Filter Elements'] },
        { label: 'Condition Monitoring', items: ['Vibration Sensors', 'Thermal Cameras', 'Oil Analysis Kits'] }
      ]
    },
    {
      label: 'Services', href: 'services.html',
      desc: 'Full lifecycle asset support',
      subs: [
        { label: 'Reliability Programs', items: ['A.R.M.S.', 'Predictive Maintenance', 'Condition Monitoring'] },
        { label: 'Field Services', items: ['Commissioning', 'Preventive Maintenance', 'Emergency Response'] },
        { label: 'Training', items: ['Primegear Academy', 'In-House Training', 'Certification Pathways'] }
      ]
    },
    {
      label: 'Partners', href: 'partners.html',
      desc: 'Our technology partners',
      subs: [
        { label: 'Compressed Air', items: ['CompAir UK', 'OXYMAT Denmark'] },
        { label: 'Fluid Power', items: ['HYDAC Germany', 'Pall Corporation', 'SPM Instruments'] },
        { label: 'Instrumentation', items: ['Emerson CSI', 'SKF', 'FLIR Systems'] }
      ]
    },
    {
      label: 'Careers', href: 'careers.html',
      desc: 'Grow your engineering career',
      subs: [
        { label: 'Life at Atlasco', items: ['Our Culture', 'Annual Events', 'Team Stories'] },
        { label: 'Opportunities', items: ['Engineering Roles', 'Sales Roles', 'Graduate Program'] },
        { label: 'Development', items: ['Primegear Academy', 'Certifications', 'Training Programs'] }
      ]
    }
  ];

  var chevronSvg = '<svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"/></svg>';

  var sbHtml = '<div class="sidebar-overlay" id="sbOverlay"></div>'
    + '<div class="mega-sidebar" id="megaSidebar">'
    +   '<div class="sb-panel-l">'
    +     '<div class="sb-head">'
    +       '<div class="sb-logo"><div class="sb-logo-icon"><svg viewBox="0 0 28 28" fill="none" width="16" height="16"><path d="M4 24L10 8L14 18L18 8L24 24" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M7 18H21" stroke="white" stroke-width="2" stroke-linecap="round"/></svg></div><strong>ATLASCO</strong></div>'
    +       '<button class="sb-close" id="sbClose">&times;</button>'
    +     '</div>'
    +     '<nav class="sb-nav" id="sbNav"></nav>'
    +     '<div class="sb-footer"><a href="contact.html" class="sb-cta">Contact Us &rarr;</a></div>'
    +   '</div>'
    +   '<div class="sb-panel-m" id="sbMid"></div>'
    +   '<div class="sb-panel-r" id="sbRight"></div>'
    + '</div>';

  document.body.insertAdjacentHTML('afterbegin', sbHtml);

  var sbOverlay  = document.getElementById('sbOverlay');
  var megaSidebar = document.getElementById('megaSidebar');
  var sbNav      = document.getElementById('sbNav');
  var sbClose    = document.getElementById('sbClose');
  var sbMid      = document.getElementById('sbMid');
  var sbRight    = document.getElementById('sbRight');

  /* Build left nav */
  sidebarData.forEach(function (section, idx) {
    var a = document.createElement('a');
    a.className = 'sb-nav-item';
    a.href = section.href;
    a.dataset.idx = idx;
    a.innerHTML = '<span>' + section.label + '</span>' + chevronSvg;
    a.addEventListener('mouseenter', function () { showMid(idx); });
    a.addEventListener('click', function (e) { e.preventDefault(); showMid(idx); });
    sbNav.appendChild(a);
  });

  var activeMidIdx = -1;
  var activeSubIdx = -1;

  function showMid(idx) {
    if (activeMidIdx === idx) return;
    activeMidIdx = idx;
    activeSubIdx = -1;
    sbNav.querySelectorAll('.sb-nav-item').forEach(function (el) { el.classList.remove('sb-active'); });
    sbNav.querySelectorAll('.sb-nav-item')[idx].classList.add('sb-active');
    var section = sidebarData[idx];
    var html = '<div class="sb-panel-head"><h4>' + section.label + '</h4><p>' + section.desc + '</p></div><div class="sb-sub-list">';
    section.subs.forEach(function (sub, si) {
      html += '<a class="sb-sub-item" href="' + (sub.href || section.href) + '" data-si="' + si + '">'
        + '<span>' + sub.label + '</span>' + chevronSvg + '</a>';
    });
    html += '</div>';
    sbMid.innerHTML = html;
    sbRight.innerHTML = '';
    sbMid.querySelectorAll('.sb-sub-item').forEach(function (el) {
      el.addEventListener('mouseenter', function () { showRight(idx, parseInt(el.dataset.si)); });
      el.addEventListener('click', function (e) { e.preventDefault(); showRight(idx, parseInt(el.dataset.si)); });
    });
    /* Auto-show first sub */
    if (section.subs.length > 0) showRight(idx, 0);
  }

  function showRight(sectionIdx, subIdx) {
    if (activeSubIdx === subIdx && activeMidIdx === sectionIdx) return;
    activeSubIdx = subIdx;
    sbMid.querySelectorAll('.sb-sub-item').forEach(function (el) { el.classList.remove('sb-active'); });
    var subEl = sbMid.querySelectorAll('.sb-sub-item')[subIdx];
    if (subEl) subEl.classList.add('sb-active');
    var sub = sidebarData[sectionIdx].subs[subIdx];
    if (!sub) return;
    var html = '<div class="sb-panel-head"><h4>' + sub.label + '</h4><p>Select a topic below</p></div><div class="sb-third-list">';
    var subHref = sub.href || sidebarData[sectionIdx].href;
    sub.items.forEach(function (item) {
      html += '<a class="sb-third-item" href="' + subHref + '">' + item + '</a>';
    });
    html += '</div>';
    sbRight.innerHTML = html;
  }

  function openSidebar() {
    sbOverlay.classList.add('open');
    megaSidebar.classList.add('open');
    document.body.style.overflow = 'hidden';
    if (sidebarData.length > 0) showMid(0);
  }

  function closeSidebar() {
    sbOverlay.classList.remove('open');
    megaSidebar.classList.remove('open');
    document.body.style.overflow = '';
    activeMidIdx = -1;
    activeSubIdx = -1;
  }

  sbClose.addEventListener('click', closeSidebar);
  sbOverlay.addEventListener('click', closeSidebar);

  /* ======= MOBILE MENU (replaced by sidebar) ======= */
  var menuBtn   = document.querySelector('.menu-btn');
  var mobileMenu  = document.querySelector('.mobile-menu');
  var mobileClose = document.querySelector('.mobile-menu-close');

  if (menuBtn) {
    menuBtn.addEventListener('click', openSidebar);
  }
  if (mobileClose && mobileMenu) {
    mobileClose.addEventListener('click', function () { mobileMenu.classList.remove('open'); });
  }

  /* ======= SOLUTION TABS ======= */
  document.querySelectorAll('.tab-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var tabId = this.dataset.tab;
      var wrapper = this.closest('.tabs-wrapper');
      wrapper.querySelectorAll('.tab-btn').forEach(function (b) { b.classList.remove('active'); });
      wrapper.querySelectorAll('.tab-panel').forEach(function (p) { p.classList.remove('active'); });
      this.classList.add('active');
      var panel = wrapper.querySelector('[data-panel="' + tabId + '"]');
      if (panel) panel.classList.add('active');
    });
  });

  /* ======= CATEGORY SLIDER ======= */
  var sliderWrap = document.querySelector('.slider-wrapper');
  if (sliderWrap) {
    var track    = sliderWrap.querySelector('.slider-track');
    var cards    = track ? track.querySelectorAll('.category-card') : [];
    var prevBtn  = document.querySelector('.slider-btn.prev');
    var nextBtn  = document.querySelector('.slider-btn.next');
    var dots     = document.querySelectorAll('.s-dot');
    var current  = 0;
    var perView  = 4;

    function cardW() { return cards[0] ? cards[0].offsetWidth + 20 : 280; }
    function maxIdx() { return Math.max(0, cards.length - perView); }

    function goTo(idx) {
      current = Math.max(0, Math.min(idx, maxIdx()));
      if (track) track.style.transform = 'translateX(-' + (current * cardW()) + 'px)';
      dots.forEach(function (d, i) { d.classList.toggle('active', i === current); });
    }

    if (prevBtn) prevBtn.addEventListener('click', function () { goTo(current - 1); });
    if (nextBtn) nextBtn.addEventListener('click', function () { goTo(current + 1); });
    dots.forEach(function (d, i) { d.addEventListener('click', function () { goTo(i); }); });

    window.addEventListener('resize', function () { goTo(current); });
  }

  /* ======= CONTACT FORM ======= */
  var contactForm = document.getElementById('contactForm');
  if (contactForm) {
    contactForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var btn = this.querySelector('.submit-btn');
      btn.textContent = 'Sending…';
      btn.disabled = true;
      setTimeout(function () {
        btn.textContent = '✓ Request Sent!';
        btn.style.background = '#16a34a';
        contactForm.reset();
        setTimeout(function () {
          btn.textContent = 'Submit Request ▶';
          btn.style.background = '';
          btn.disabled = false;
        }, 3000);
      }, 1400);
    });
  }

  /* ======= ENROLLMENT FORM ======= */
  var enrollForm = document.getElementById('enrollForm');
  if (enrollForm) {
    enrollForm.addEventListener('submit', function (e) {
      e.preventDefault();
      var btn = this.querySelector('.submit-btn');
      btn.textContent = 'Submitting…';
      btn.disabled = true;
      setTimeout(function () {
        btn.textContent = '✓ Enrollment Submitted!';
        btn.style.background = '#0d9488';
        enrollForm.reset();
        setTimeout(function () {
          btn.textContent = 'Submit Enrollment Request →';
          btn.style.background = '';
          btn.disabled = false;
        }, 3000);
      }, 1400);
    });
  }

  /* ======= ACTIVE NAV LINK ======= */
  var path = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(function (a) {
    if (a.getAttribute('href') === path) a.classList.add('active');
  });

  /* ======= NAV SEPARATOR (between social icons & menu btn) ======= */
  var menuBtnEl = document.querySelector('.nav-right .menu-btn');
  if (menuBtnEl) {
    var sep = document.createElement('span');
    sep.className = 'nav-sep';
    menuBtnEl.parentNode.insertBefore(sep, menuBtnEl);
  }

  /* ======= FIX YOUTUBE PLAY ICON ======= */
  document.querySelectorAll('.si-yt svg').forEach(function (svg) {
    if (!svg.querySelector('polygon')) {
      var poly = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
      poly.setAttribute('points', '9.75 15.02 15.5 12 9.75 8.98 9.75 15.02');
      poly.setAttribute('fill', '#ff0000');
      svg.appendChild(poly);
    }
  });

  /* ======= STATS COUNTER ANIMATION ======= */
  var statsBar = document.querySelector('.stats-bar');
  if (statsBar && 'IntersectionObserver' in window) {
    var counterDone = false;
    var counterObserver = new IntersectionObserver(function (entries) {
      if (counterDone) return;
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        counterDone = true;
        counterObserver.disconnect();
        statsBar.querySelectorAll('.stat-number').forEach(function (el) {
          var raw = el.textContent.trim();
          var suffix = raw.replace(/[\d,]/g, '');
          var target = parseInt(raw.replace(/\D/g, ''), 10);
          if (!target) return;
          var duration = 2000;
          var startTime = null;
          function step(timestamp) {
            if (!startTime) startTime = timestamp;
            var progress = Math.min((timestamp - startTime) / duration, 1);
            var eased = 1 - Math.pow(1 - progress, 3);
            var value = Math.round(eased * target);
            el.textContent = value.toLocaleString() + suffix;
            if (progress < 1) requestAnimationFrame(step);
          }
          requestAnimationFrame(step);
        });
      });
    }, { threshold: 0.4 });
    counterObserver.observe(statsBar);
  }

})();
