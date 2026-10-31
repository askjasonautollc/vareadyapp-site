(function(){var b=document.getElementById('vsoNear'),l=document.getElementById('vsoList'),m=document.getElementById('vsoNearMsg');if(!b||!l)return;
if(!navigator.geolocation){b.hidden=true;return;}
function e(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function d(a,b2,c2,d2){var R=3959,x=Math.PI/180,u=(c2-a)*x,v=(d2-b2)*x,q=Math.sin(u/2)*Math.sin(u/2)+Math.cos(a*x)*Math.cos(c2*x)*Math.sin(v/2)*Math.sin(v/2);return R*2*Math.atan2(Math.sqrt(q),Math.sqrt(1-q));}
/* The office file is about 180 KB gzipped, so it loads only after the tap. */
b.addEventListener('click',function(){b.disabled=true;b.textContent='Locating…';
navigator.geolocation.getCurrentPosition(function(p){var la=p.coords.latitude,lo=p.coords.longitude;
fetch('/vso/near.json').then(function(r){return r.json();}).then(function(rows){
rows.forEach(function(o){o.d=d(la,lo,o.a,o.g);});rows.sort(function(x,y){return x.d-y.d;});
l.innerHTML=rows.slice(0,12).map(function(o){return '<li class="vso-card"><div class="vso-top"><span class="vso-name">'+e(o.n)+'</span><span class="vso-dist">'+o.d.toFixed(0)+' mi</span></div><div class="vso-org">'+e(o.o)+'</div><div class="vso-loc">'+e(o.l)+'</div><div class="vso-actions">'+(o.t?'<a href="tel:'+e(o.t)+'">Call</a>':'')+'<a href="https://www.google.com/maps/search/?api=1&query='+o.a+','+o.g+'" target="_blank" rel="noopener nofollow">Directions</a><a href="/vso/'+e(o.s)+'.html">More in this state</a></div></li>';}).join('');
l.hidden=false;b.textContent='Nearest first';if(m)m.textContent='The 12 closest offices.';
},function(){b.disabled=false;b.textContent='Try again';if(m)m.textContent='Could not load offices. Pick your state below.';});
},function(){b.disabled=false;b.textContent='Show offices near me';if(m)m.textContent='Location is off. Pick your state below.';});});
})();
