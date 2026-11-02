/* Anca Creations – site behaviour (vanilla JS, no dependencies) */
(function () {
  "use strict";

  document.documentElement.classList.add("js");

  /* ---- Mobile navigation ---- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  /* ---- Reveal on scroll ---- */
  var revealEls = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* ---- Toasts ---- */
  document.querySelectorAll(".toast").forEach(function (toast) {
    var close = toast.querySelector(".toast-close");
    var remove = function () { toast.remove(); };
    if (close) close.addEventListener("click", remove);
    setTimeout(remove, 6500);
  });

  /* ---- Confirm dialogs for forms that ask for it ---- */
  document.querySelectorAll("form[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (!window.confirm(form.getAttribute("data-confirm"))) e.preventDefault();
    });
  });

  /* ---- Lightbox for gallery items ---- */
  var items = Array.prototype.slice.call(document.querySelectorAll("[data-lightbox]"));
  if (items.length) {
    var box = document.createElement("div");
    box.className = "lightbox";
    box.hidden = true;
    box.setAttribute("role", "dialog");
    box.setAttribute("aria-modal", "true");
    box.setAttribute("aria-label", "Media viewer");

    var stage = document.createElement("div");
    stage.className = "lb-stage";
    var caption = document.createElement("div");
    caption.className = "lb-caption";
    var capTitle = document.createElement("strong");
    var capText = document.createElement("span");
    caption.appendChild(capTitle);
    caption.appendChild(capText);

    function makeBtn(cls, label, text) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "lb-btn " + cls;
      b.setAttribute("aria-label", label);
      b.textContent = text;
      return b;
    }
    var btnClose = makeBtn("lb-close", "Close", "×");
    var btnPrev = makeBtn("lb-prev", "Previous", "‹");
    var btnNext = makeBtn("lb-next", "Next", "›");

    box.appendChild(stage);
    box.appendChild(caption);
    box.appendChild(btnClose);
    box.appendChild(btnPrev);
    box.appendChild(btnNext);
    document.body.appendChild(box);

    var index = 0;
    var lastFocus = null;

    function render() {
      var el = items[index];
      var type = el.getAttribute("data-type");
      var src = el.getAttribute("data-src");
      var title = el.getAttribute("data-title") || "";
      stage.textContent = "";
      var media;
      if (type === "video") {
        media = document.createElement("video");
        media.controls = true;
        media.autoplay = true;
        media.playsInline = true;
        media.src = src;
      } else {
        media = document.createElement("img");
        media.src = src;
        media.alt = title;
      }
      stage.appendChild(media);
      capTitle.textContent = title;
      capText.textContent = el.getAttribute("data-caption") || "";
      var many = items.length > 1;
      btnPrev.style.display = many ? "" : "none";
      btnNext.style.display = many ? "" : "none";
    }

    function open(i) {
      index = i;
      lastFocus = document.activeElement;
      render();
      box.hidden = false;
      document.body.style.overflow = "hidden";
      btnClose.focus();
    }
    function close() {
      box.hidden = true;
      stage.textContent = ""; // stops any playing video
      document.body.style.overflow = "";
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    }
    function step(d) {
      index = (index + d + items.length) % items.length;
      render();
    }

    items.forEach(function (el, i) {
      el.addEventListener("click", function () { open(i); });
      el.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(i); }
      });
    });
    btnClose.addEventListener("click", close);
    btnPrev.addEventListener("click", function () { step(-1); });
    btnNext.addEventListener("click", function () { step(1); });
    box.addEventListener("click", function (e) { if (e.target === box) close(); });
    document.addEventListener("keydown", function (e) {
      if (box.hidden) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowLeft") step(-1);
      if (e.key === "ArrowRight") step(1);
    });
  }

  /* ---- Upload dropzone with previews ---- */
  document.querySelectorAll("[data-dropzone]").forEach(function (zone) {
    var input = zone.querySelector('input[type="file"]');
    var previews = zone.parentNode.querySelector("[data-previews]");
    if (!input || !previews) return;

    function showPreviews() {
      previews.textContent = "";
      Array.prototype.forEach.call(input.files, function (file) {
        var wrap = document.createElement("div");
        wrap.className = "preview";
        var url = URL.createObjectURL(file);
        var el;
        if (file.type.indexOf("video/") === 0) {
          el = document.createElement("video");
          el.muted = true;
          el.preload = "metadata";
          el.src = url + "#t=0.1";
        } else if (file.type.indexOf("image/") === 0) {
          el = document.createElement("img");
          el.src = url;
          el.alt = file.name;
        }
        if (el) wrap.appendChild(el);
        var label = document.createElement("small");
        label.textContent = file.name;
        wrap.appendChild(label);
        previews.appendChild(wrap);
      });
    }

    input.addEventListener("change", showPreviews);
    ["dragenter", "dragover"].forEach(function (evt) {
      zone.addEventListener(evt, function () { zone.classList.add("is-over"); });
    });
    ["dragleave", "drop"].forEach(function (evt) {
      zone.addEventListener(evt, function () { zone.classList.remove("is-over"); });
    });
  });
})();
