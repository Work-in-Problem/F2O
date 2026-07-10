// Runs in <head> before paint: restore theme + pick language.
// Language default: stored pref wins; else browser language th* -> th, anything else -> en.
(function () {
  var r = document.documentElement;
  try {
    var t = localStorage.getItem("f2o-theme");
    if (t === "light" || t === "dark") r.setAttribute("data-theme", t);
    var l = localStorage.getItem("f2o-lang");
    if (l !== "th" && l !== "en") {
      // Primary browser language only: th* -> Thai, anything else (or unknown) -> English.
      var primary = (navigator.languages && navigator.languages[0]) || navigator.language || "";
      l = String(primary).toLowerCase().indexOf("th") === 0 ? "th" : "en";
    }
    r.setAttribute("data-lang", l);
    r.setAttribute("lang", l);
  } catch (e) { /* defaults in the HTML tag stand */ }
})();
