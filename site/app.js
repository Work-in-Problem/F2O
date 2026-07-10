// F2O site — toggles + copy buttons (boot.js already set theme/lang before paint).
(function () {
  var root = document.documentElement;

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

  document.querySelectorAll("pre[data-copy]").forEach(function (pre) {
    var btn = document.createElement("button");
    btn.className = "copy-btn";
    btn.type = "button";
    btn.textContent = "copy";
    btn.addEventListener("click", function () {
      var clone = pre.cloneNode(true);
      var b = clone.querySelector(".copy-btn");
      if (b) b.remove();
      var text = clone.textContent.replace(/^\n+|\n+$/g, "");
      navigator.clipboard.writeText(text).then(function () {
        btn.textContent = "copied!";
        btn.classList.add("done");
        setTimeout(function () { btn.textContent = "copy"; btn.classList.remove("done"); }, 1400);
      });
    });
    pre.appendChild(btn);
  });
})();
