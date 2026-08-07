(function(){var i=document.getElementById('vsoFilter'),l=document.getElementById('vsoList');if(!l)return;
var cards=[].slice.call(l.querySelectorAll('.vso-card')),cnt=document.getElementById('vsoCount'),raf=0;
/* Cache the haystack once. Reading a data attribute per card per keystroke was
   forcing a DOM read on 800+ nodes for every character typed. */
var hay=cards.map(function(c){return (c.getAttribute('data-search')||'').toLowerCase();});
/* Toggle the hidden attribute instead of writing style.display, and only when
   the state actually changes. Writing display on every card every keystroke was
   the layout thrash that made a big state feel stuck while typing. */
function apply(){raf=0;var q=(i.value||'').toLowerCase().trim(),s=0;
for(var n=0;n<cards.length;n++){var m=!q||hay[n].indexOf(q)>-1;if(m)s++;
if(cards[n].hidden===m)cards[n].hidden=!m;}
if(cnt)cnt.textContent=s;}
/* Coalesce to one pass per frame, so holding a key down cannot queue work. */
function f(){if(raf)return;raf=requestAnimationFrame(apply);}
if(i)i.addEventListener('input',f);
var b=document.getElementById('vsoNear');
if(b&&navigator.geolocation){b.addEventListener('click',function(){b.textContent='Locating\u2026';navigator.geolocation.getCurrentPosition(function(p){var la=p.coords.latitude,lo=p.coords.longitude;
function d(a,b2,c2,d2){var R=3959,x=Math.PI/180,u=(c2-a)*x,v=(d2-b2)*x,q=Math.sin(u/2)*Math.sin(u/2)+Math.cos(a*x)*Math.cos(c2*x)*Math.sin(v/2)*Math.sin(v/2);return R*2*Math.atan2(Math.sqrt(q),Math.sqrt(1-q));}
var order=cards.map(function(c,n){var la2=parseFloat(c.getAttribute('data-lat')),lo2=parseFloat(c.getAttribute('data-lng')),dd=(!isNaN(la2)&&!isNaN(lo2))?d(la,lo,la2,lo2):1e9;var bd=c.querySelector('.vso-dist');if(bd&&dd<1e9)bd.textContent=dd.toFixed(0)+' mi';return{c:c,d:dd,n:n};});
order.sort(function(a,b3){return a.d-b3.d||a.n-b3.n;});
/* One fragment, one reflow, instead of 800 appendChild calls against the live list. */
var fr=document.createDocumentFragment();order.forEach(function(o){fr.appendChild(o.c);});l.appendChild(fr);
cards=order.map(function(o){return o.c;});hay=cards.map(function(c){return (c.getAttribute('data-search')||'').toLowerCase();});
b.textContent='\u2713 Nearest first';},function(){b.textContent='Location unavailable';});});}
})();