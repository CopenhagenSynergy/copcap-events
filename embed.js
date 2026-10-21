/*
 * Eastern Denmark Business Events — embed loader.
 * Hand-maintained (build_site.py does not touch this file).
 *
 * Paste on any page:
 *   <div class="copcap-events"></div>
 *   <script src="https://copenhagensynergy.github.io/copcap-events/embed.js" async></script>
 *
 * Optional attributes on the div:
 *   data-country="Denmark"   preselect a country; data-country="" shows all countries
 *   data-subscribe="0"       hide the "Add to my calendar" section
 *   data-theme="light"       light (default), dark, or auto (follows the visitor's system)
 *   data-bg="transparent"    let the host page's background show through
 *   data-height="900"        starting height in px before the calendar reports its own
 */
(function () {
  var script = document.currentScript;
  var base = script && script.src
    ? script.src.replace(/embed\.js(\?.*)?$/, "")
    : "https://copenhagensynergy.github.io/copcap-events/";
  var origin = new URL(base).origin;
  var frames = {};

  function mount(el, i) {
    if (el.getAttribute("data-mounted")) return;
    el.setAttribute("data-mounted", "1");
    var id = "copcap-events-" + i + "-" + Math.random().toString(36).slice(2, 8);
    var params = new URLSearchParams({ embed: "1", id: id });
    ["country", "subscribe", "theme", "bg"].forEach(function (k) {
      var v = el.getAttribute("data-" + k);
      if (v !== null) params.set(k, v);
    });
    var f = document.createElement("iframe");
    f.src = base + "?" + params.toString();
    f.title = "Eastern Denmark Business Events";
    f.setAttribute("allow", "clipboard-write");
    f.style.cssText = "display:block;width:100%;border:0;height:" +
      (parseInt(el.getAttribute("data-height"), 10) || 900) + "px";
    el.appendChild(f);
    frames[id] = f;
  }

  window.addEventListener("message", function (e) {
    if (e.origin !== origin) return;
    var d = e.data;
    if (!d || d.type !== "copcap-events:resize" || !frames[d.id]) return;
    var h = parseInt(d.height, 10);
    if (h > 0 && h < 20000) frames[d.id].style.height = h + "px";
  });

  function init() {
    var els = document.querySelectorAll(".copcap-events, #copcap-events");
    for (var i = 0; i < els.length; i++) mount(els[i], i);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
