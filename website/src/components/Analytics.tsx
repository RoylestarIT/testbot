import Script from "next/script";

const YM_ID = process.env.NEXT_PUBLIC_YM_ID?.trim();
const GA_ID = process.env.NEXT_PUBLIC_GA_ID?.trim();

/** Яндекс.Метрика и GA4 — включаются только при заданных env на сборке. */
export function Analytics() {
  return (
    <>
      {YM_ID && (
        <>
          <Script id="ym-init" strategy="afterInteractive">
            {`(function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};
m[i].l=1*new Date();
for (var j = 0; j < document.scripts.length; j++) {if (document.scripts[j].src === r) { return; }}
k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)})
(window, document, "script", "https://mc.yandex.ru/metrika/tag.js", "ym");
ym(${JSON.stringify(Number(YM_ID))}, "init", { clickmap:true, trackLinks:true, accurateTrackBounce:true, webvisor:true });`}
          </Script>
          <noscript>
            <div>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={`https://mc.yandex.ru/watch/${YM_ID}`}
                alt=""
                style={{ position: "absolute", left: "-9999px" }}
              />
            </div>
          </noscript>
        </>
      )}
      {GA_ID && (
        <>
          <Script
            src={`https://www.googletagmanager.com/gtag/js?id=${GA_ID}`}
            strategy="afterInteractive"
          />
          <Script id="ga-init" strategy="afterInteractive">
            {`window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());gtag('config',${JSON.stringify(GA_ID)},{ anonymize_ip:true });`}
          </Script>
        </>
      )}
    </>
  );
}
