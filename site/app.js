// F2O site — theme (dark default) + language (TH default) + copy buttons.
(function () {
  var root = document.documentElement;

  // ----- restore prefs (dark + TH are the defaults, set in the HTML tag) -----
  try {
    var t = localStorage.getItem("f2o-theme");
    if (t === "light" || t === "dark") root.setAttribute("data-theme", t);
    var l = localStorage.getItem("f2o-lang");
    if (l === "th" || l === "en") root.setAttribute("data-lang", l);
  } catch (e) { /* private mode etc. — defaults stand */ }

  document.getElementById("theme-toggle").addEventListener("click", function () {
    var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try { localStorage.setItem("f2o-theme", next); } catch (e) {}
  });

  document.getElementById("lang-toggle").addEventListener("click", function () {
    var next = root.getAttribute("data-lang") === "th" ? "en" : "th";
    root.setAttribute("data-lang", next);
    root.setAttribute("lang", next);
    try { localStorage.setItem("f2o-lang", next); } catch (e) {}
  });

  // ----- copy buttons on every code block -----
  document.querySelectorAll("pre[data-copy]").forEach(function (pre) {
    var btn = document.createElement("button");
    btn.className = "copy-btn";
    btn.type = "button";
    btn.textContent = "copy";
    btn.addEventListener("click", function () {
      var text = pre.textContent.replace(/^copy\s*/,"").replace(/\s*(copied!|copy)\s*$/, "");
      // pre.textContent includes the button label; safer: clone without button
      var clone = pre.cloneNode(true);
      var b = clone.querySelector(".copy-btn");
      if (b) b.remove();
      text = clone.textContent.replace(/^\n+|\n+$/g, "");
      navigator.clipboard.writeText(text).then(function () {
        btn.textContent = "copied!";
        btn.classList.add("done");
        setTimeout(function () { btn.textContent = "copy"; btn.classList.remove("done"); }, 1400);
      });
    });
    pre.appendChild(btn);
  });
})();
