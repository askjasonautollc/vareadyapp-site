/* VA Ready — anonymous download-click tracking via Vercel Web Analytics.
   Fires a `download_click` custom event when any App Store / Google Play link is
   clicked, anywhere on the site. No cookies, no PII — store + page + placement only. */
(function () {
  function store(href) {
    if (href.indexOf('apps.apple.com') > -1)  return 'ios';
    if (href.indexOf('play.google.com') > -1) return 'android';
    return null;
  }
  function placement(el) {
    if (el.closest('nav'))      return 'nav';
    if (el.closest('footer'))   return 'footer';
    if (el.closest('.cta-pro')) return 'cta-pro';
    if (el.closest('.cta'))     return 'cta';
    if (el.closest('.hero'))    return 'hero';
    return 'body';
  }
  document.addEventListener('click', function (e) {
    var a = e.target && e.target.closest ? e.target.closest('a[href]') : null;
    if (!a) return;
    var s = store(a.href);
    if (!s) return;
    if (typeof window.va === 'function') {
      window.va('event', {
        name: 'download_click',
        data: { store: s, page: location.pathname, placement: placement(a) }
      });
    }
  }, true); // capture phase: fires before same-tab navigation; va() uses sendBeacon
})();
