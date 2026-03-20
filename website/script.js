/* LYCHEETAH FRAMEWORK — SCRIPT
   Refused spectacle. Validated struggle.
   Minimal: mobile nav toggle, smooth scroll, platform tabs. Nothing else. */

(function () {
  'use strict';

  // ============================================================
  // MOBILE NAV TOGGLE
  // ============================================================

  var toggle = document.getElementById('nav-toggle');
  var links  = document.getElementById('nav-links');

  if (toggle && links) {
    toggle.addEventListener('click', function () {
      var isOpen = links.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(isOpen));
    });

    // Close on outside click
    document.addEventListener('click', function (e) {
      if (!toggle.contains(e.target) && !links.contains(e.target)) {
        links.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });

    // Close on escape key
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        links.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // ============================================================
  // PLATFORM TABS (for-agents.html)
  // ============================================================

  var tabBtns   = document.querySelectorAll('.platform-tab-btn');
  var tabPanels = document.querySelectorAll('.platform-tab-panel');

  if (tabBtns.length > 0) {
    tabBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var target = btn.getAttribute('data-tab');

        // Update buttons
        tabBtns.forEach(function (b) {
          b.classList.remove('active');
          b.setAttribute('aria-selected', 'false');
        });
        btn.classList.add('active');
        btn.setAttribute('aria-selected', 'true');

        // Update panels
        tabPanels.forEach(function (panel) {
          panel.classList.remove('active');
        });
        var targetPanel = document.getElementById('tab-' + target);
        if (targetPanel) {
          targetPanel.classList.add('active');
        }
      });
    });
  }

  // ============================================================
  // SMOOTH SCROLL (for anchor links)
  // ============================================================

  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      var id = anchor.getAttribute('href').slice(1);
      var target = document.getElementById(id);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

}());
