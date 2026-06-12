(function(){var i=document.getElementById('vsoFilter'),l=document.getElementById('vsoList');if(!l)return;
var cards=[].slice.call(l.querySelectorAll('.vso-card'));
function f(){var q=(i.value||'').toLowerCase().trim(),s=0;cards.forEach(function(c){var m=!q||c.getAttribute('data-search').indexOf(q)>-1;c.style.display=m?'':'none';if(m)s++;});var cnt=document.getElementById('vsoCount');if(cnt)cnt.textContent=s;}
if(i)i.addEventListener('input',f);
var b=document.getElementById('vsoNear');
if(b&&navigator.geolocation){b.addEventListener('click',function(){b.textContent='Locating\u2026';navigator.geolocation.getCurrentPosition(function(p){var la=p.coords.latitude,lo=p.coords.longitude;
function d(a,b2,c2,d2){var R=3959,x=Math.PI/180,u=(c2-a)*x,v=(d2-b2)*x,q=Math.sin(u/2)*Math.sin(u/2)+Math.cos(a*x)*Math.cos(c2*x)*Math.sin(v/2)*Math.sin(v/2);return R*2*Math.atan2(Math.sqrt(q),Math.sqrt(1-q));}
cards.forEach(function(c){var la2=parseFloat(c.getAttribute('data-lat')),lo2=parseFloat(c.getAttribute('data-lng')),dd=(!isNaN(la2)&&!isNaN(lo2))?d(la,lo,la2,lo2):1e9;c.setAttribute('data-dist',dd);var bd=c.querySelector('.vso-dist');if(bd&&dd<1e9)bd.textContent=dd.toFixed(0)+' mi';});
cards.sort(function(a,b3){return parseFloat(a.getAttribute('data-dist'))-parseFloat(b3.getAttribute('data-dist'));});
cards.forEach(function(c){l.appendChild(c);});b.textContent='\u2713 Nearest first';},function(){b.textContent='Location unavailable';});});}
})();