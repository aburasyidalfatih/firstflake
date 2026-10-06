/* Loads GA4 / Meta Pixel after the page has rendered, only if IDs are set in admin. */
(function(){
  function go(){
    fetch('/api/config').then(function(r){return r.json()}).then(function(c){
      var ev=document.body.dataset.ev, val=c.price, cur=c.currency;
      if(ev==='purchase'){var k='ff_p_'+(new URLSearchParams(location.search).get('t')||'').slice(0,40);if(localStorage.getItem(k))ev='';else localStorage.setItem(k,1);}
      if(c.ga){
        var s=document.createElement('script');s.async=1;s.src='https://www.googletagmanager.com/gtag/js?id='+c.ga;document.head.appendChild(s);
        window.dataLayer=window.dataLayer||[];window.gtag=function(){dataLayer.push(arguments)};
        gtag('js',new Date());gtag('config',c.ga);
        if(ev==='checkout')gtag('event','begin_checkout',{value:+val,currency:cur});
        if(ev==='purchase')gtag('event','purchase',{value:+val,currency:cur,transaction_id:(new URLSearchParams(location.search).get('t')||'').split('.')[0]});
      }
      if(c.pixel){
        !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
        fbq('init',c.pixel);fbq('track','PageView');
        if(ev==='checkout')fbq('track','InitiateCheckout',{value:+val,currency:cur});
        if(ev==='purchase')fbq('track','Purchase',{value:+val,currency:cur});
      }
    }).catch(function(){});
  }
  if(document.readyState==='complete')setTimeout(go,1);else addEventListener('load',function(){setTimeout(go,300)});
})();
