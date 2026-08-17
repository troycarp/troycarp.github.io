/* Carpenter Engineering — site behaviour.
   Four independent pieces: header state, mobile nav, project filtering, and the
   project lightbox. No dependencies. */
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ------------------------------------------------------- header state -- */

  var header = document.getElementById("siteHeader");
  var hero = document.querySelector(".hero");

  function syncHeader() {
    var threshold = hero ? hero.offsetHeight - header.offsetHeight - 40 : 40;
    header.dataset.solid = window.scrollY > Math.max(threshold, 40) ? "true" : "false";
  }

  var ticking = false;
  window.addEventListener(
    "scroll",
    function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () {
        syncHeader();
        ticking = false;
      });
    },
    { passive: true }
  );
  window.addEventListener("resize", syncHeader);
  syncHeader();

  /* --------------------------------------------------------- mobile nav -- */

  var navToggle = document.getElementById("navToggle");
  var siteNav = document.getElementById("siteNav");
  var mobileQuery = window.matchMedia("(max-width: 860px)");

  function closeNav() {
    navToggle.setAttribute("aria-expanded", "false");
    if (mobileQuery.matches) siteNav.hidden = true;
  }

  function applyNavMode() {
    // Outside the mobile breakpoint the nav is always visible; `hidden` would
    // otherwise survive a resize and blank out the desktop nav.
    siteNav.hidden = mobileQuery.matches && navToggle.getAttribute("aria-expanded") !== "true";
  }

  navToggle.addEventListener("click", function () {
    var open = navToggle.getAttribute("aria-expanded") === "true";
    navToggle.setAttribute("aria-expanded", String(!open));
    siteNav.hidden = open;
  });

  siteNav.addEventListener("click", function (event) {
    if (event.target.closest("a")) closeNav();
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && navToggle.getAttribute("aria-expanded") === "true") {
      closeNav();
      navToggle.focus();
    }
  });

  if (mobileQuery.addEventListener) mobileQuery.addEventListener("change", applyNavMode);
  else mobileQuery.addListener(applyNavMode);
  applyNavMode();

  /* ---------------------------------------------------- project filters -- */

  var grid = document.getElementById("workGrid");
  var cards = Array.prototype.slice.call(grid.querySelectorAll(".project"));
  var filters = Array.prototype.slice.call(document.querySelectorAll(".filter"));
  var emptyNote = document.getElementById("workEmpty");

  filters.forEach(function (button) {
    var key = button.dataset.filter;
    var count =
      key === "all"
        ? cards.length
        : cards.filter(function (card) {
            return card.dataset.cats.split(" ").indexOf(key) > -1;
          }).length;

    var badge = document.createElement("span");
    badge.className = "count";
    badge.textContent = count;
    button.appendChild(badge);

    button.addEventListener("click", function () {
      filters.forEach(function (other) {
        other.setAttribute("aria-pressed", String(other === button));
      });

      var shown = 0;
      cards.forEach(function (card) {
        var match = key === "all" || card.dataset.cats.split(" ").indexOf(key) > -1;
        card.hidden = !match;
        if (match) shown++;
      });
      emptyNote.hidden = shown > 0;
    });
  });

  /* ------------------------------------------------------- reveal on scroll */

  if (!reduceMotion && "IntersectionObserver" in window) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-in");
          observer.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.05 }
    );
    document.querySelectorAll(".reveal").forEach(function (el) {
      observer.observe(el);
    });
  } else {
    document.querySelectorAll(".reveal").forEach(function (el) {
      el.classList.add("is-in");
    });
  }

  /* ----------------------------------------------------------- lightbox -- */

  var dialog = document.getElementById("lightbox");
  var lbImage = document.getElementById("lbImage");
  var lbPrev = document.getElementById("lbPrev");
  var lbNext = document.getElementById("lbNext");
  var lbCounter = document.getElementById("lbCounter");
  var lbMeta = document.getElementById("lbMeta");
  var lbTitle = document.getElementById("lbTitle");
  var lbSummary = document.getElementById("lbSummary");
  var lbScope = document.getElementById("lbScope");
  var lbScopeTitle = document.getElementById("lbScopeTitle");
  var lbScopeWrap = document.getElementById("lbScopeWrap");
  var lbClose = document.getElementById("lbClose");

  var shots = [];
  var index = 0;
  var opener = null;

  function render() {
    var shot = shots[index];
    if (!shot) return;
    lbImage.src = shot.src;
    lbImage.alt = shot.alt || "";
    lbCounter.textContent = index + 1 + " / " + shots.length;
    lbCounter.hidden = shots.length < 2;
    lbPrev.hidden = shots.length < 2;
    lbNext.hidden = shots.length < 2;
  }

  function step(delta) {
    if (shots.length < 2) return;
    index = (index + delta + shots.length) % shots.length;
    render();
  }

  function open(data, source) {
    opener = source || null;
    shots = data.images || [];
    index = 0;

    lbMeta.textContent = data.meta || "";
    lbMeta.hidden = !data.meta;
    lbTitle.textContent = data.title || "";
    lbTitle.hidden = !data.title;
    lbSummary.textContent = data.summary || "";
    lbSummary.hidden = !data.summary;

    lbScope.textContent = "";
    if (data.scope && data.scope.length) {
      lbScopeTitle.textContent = data.scopeTitle || "Scope of work";
      data.scope.forEach(function (item) {
        var li = document.createElement("li");
        li.textContent = item;
        lbScope.appendChild(li);
      });
      lbScopeWrap.hidden = false;
    } else {
      lbScopeWrap.hidden = true;
    }

    render();
    document.body.style.overflow = "hidden";
    if (typeof dialog.showModal === "function") dialog.showModal();
    else dialog.setAttribute("open", "");
    lbClose.focus();
  }

  function close() {
    if (typeof dialog.close === "function") dialog.close();
    else dialog.removeAttribute("open");
  }

  dialog.addEventListener("close", function () {
    document.body.style.overflow = "";
    lbImage.src = "";
    if (opener) opener.focus();
    opener = null;
  });

  lbClose.addEventListener("click", close);
  lbPrev.addEventListener("click", function () {
    step(-1);
  });
  lbNext.addEventListener("click", function () {
    step(1);
  });

  // Click anywhere outside the panel dismisses.
  dialog.addEventListener("click", function (event) {
    if (!event.target.closest(".lightbox-panel")) close();
  });

  dialog.addEventListener("keydown", function (event) {
    if (event.key === "ArrowRight") {
      event.preventDefault();
      step(1);
    } else if (event.key === "ArrowLeft") {
      event.preventDefault();
      step(-1);
    }
  });

  // Horizontal swipe on touch devices.
  var touchX = null;
  dialog.addEventListener(
    "touchstart",
    function (event) {
      touchX = event.changedTouches[0].clientX;
    },
    { passive: true }
  );
  dialog.addEventListener(
    "touchend",
    function (event) {
      if (touchX === null) return;
      var delta = event.changedTouches[0].clientX - touchX;
      if (Math.abs(delta) > 48) step(delta < 0 ? 1 : -1);
      touchX = null;
    },
    { passive: true }
  );

  cards.forEach(function (card) {
    var trigger = card.querySelector(".project-open");
    if (!trigger) return;
    trigger.addEventListener("click", function () {
      var data = (window.CEI_PROJECTS || {})[card.dataset.project];
      if (data) open(data, trigger);
    });
  });

  // Standalone images (the plan sheet) open the same viewer, image only.
  document.querySelectorAll("[data-lightbox-single]").forEach(function (trigger) {
    trigger.addEventListener("click", function () {
      var inner = trigger.querySelector("img");
      open(
        {
          images: [
            {
              src: trigger.dataset.lightboxSingle,
              alt: inner ? inner.alt : trigger.getAttribute("aria-label") || ""
            }
          ]
        },
        trigger
      );
    });
  });

  /* ------------------------------------------------------------- footer -- */

  var year = document.getElementById("year");
  if (year) year.textContent = new Date().getFullYear();
})();
