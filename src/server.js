import { Hono } from 'hono';
import { serve } from '@hono/node-server';
import { serveStatic } from '@hono/node-server/serve-static';
import { getCookie, setCookie, deleteCookie } from 'hono/cookie';
import { createReadStream, statSync, existsSync, readFileSync } from 'node:fs';
import { Readable } from 'node:stream';
import { timingSafeEqual } from 'node:crypto';
import { insertEvent, seenToday, funnel } from './db.js';
import { createHash } from 'node:crypto';
import { getSettings, saveSettings, insertOrder, markEmailSent, bumpDownloads, getOrder, updateStatus, listOrders, stats, DEFAULTS } from './db.js';
import { makeToken, readToken } from './crypto.js';
import { captureOrder, summarize, testCredentials } from './paypal.js';
import { sendDownloadEmail, sendTestEmail, testSmtp } from './mail.js';

const PORT = Number(process.env.PORT) || 3000;
const FILES_DIR = process.env.FILES_DIR || './private';
// key -> [file on disk, filename shown to buyer]
const FILES = {
  workbook: ['first-flake-workbook.pdf', 'First-Flake-7-Trip-Workbook.pdf'],
  bonus1: ['bonus-1-public-panning-areas-by-state.pdf', 'Bonus-1-Public-Panning-Areas-by-State.pdf'],
  bonus2: ['bonus-2-check-a-mining-claim.pdf', 'Bonus-2-How-to-Check-a-Mining-Claim.pdf'],
  bonus3: ['bonus-3-is-it-gold-card.pdf', 'Bonus-3-Is-It-Gold-ID-Card.pdf'],
  bonus4: ['bonus-4-paydirt-shortcut.pdf', 'Bonus-4-Trip-1-Paydirt-Shortcut.pdf'],
};
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD;
if (!ADMIN_PASSWORD) { console.error('ADMIN_PASSWORD env var is required.'); process.exit(1); }

const DAY = 24 * 60 * 60 * 1000;
const app = new Hono();

function siteUrl(c, s) {
  return (s.site_url || new URL(c.req.url).origin).replace(/\/$/, '');
}
function downloadLink(c, s, orderId, ttl = 7 * DAY) {
  return `${siteUrl(c, s)}/download?t=${encodeURIComponent(makeToken(`dl:${orderId}`, ttl))}`;
}

/* ---------- public API ---------- */

app.get('/healthz', (c) => c.text('ok'));

// Anonymous, cookie-free funnel tracking. Visitor id = hash(secret + day + ip + user agent), never stored raw.
const BOT = /bot|crawl|spider|slurp|preview|facebookexternalhit|headless|lighthouse|monitor|curl|wget|python/i;
app.post('/api/e', async (c) => {
  const ua = c.req.header('user-agent') || '';
  if (!ua || BOT.test(ua)) return c.body(null, 204);
  const { type, source } = await c.req.json().catch(() => ({}));
  if (!['view', 'checkout', 'pay_click'].includes(type)) return c.body(null, 204);
  const ip = c.req.header('cf-connecting-ip') || c.req.header('x-forwarded-for')?.split(',')[0].trim() || 'local';
  const day = new Date().toISOString().slice(0, 10);
  const vid = createHash('sha256').update(`${process.env.APP_SECRET}|${day}|${ip}|${ua}`).digest('hex').slice(0, 16);
  if (!seenToday.get(type, vid)) {
    const src = typeof source === 'string' ? source.toLowerCase().replace(/[^a-z0-9._-]/g, '').slice(0, 40) || null : null;
    insertEvent.run(type, vid, src);
  }
  return c.body(null, 204);
});

app.get('/api/config', (c) => {
  const s = getSettings();
  return c.json({ clientId: s.paypal_client_id, env: s.paypal_env, price: s.price, currency: s.currency, product: s.product_name, ga: s.ga_id, pixel: s.meta_pixel_id });
});

app.post('/api/capture', async (c) => {
  const s = getSettings();
  let orderID;
  try { ({ orderID } = await c.req.json()); } catch { return c.json({ error: 'Bad request' }, 400); }
  if (!orderID || !/^[A-Z0-9]{10,30}$/i.test(orderID)) return c.json({ error: 'Invalid order id' }, 400);

  let order;
  try { order = await captureOrder(s, orderID); }
  catch (e) { console.error('capture', e.message); return c.json({ error: 'Could not reach PayPal. Please contact support with your receipt.' }, 502); }

  const o = summarize(order);
  if (!o.paid || o.currency !== s.currency || Number(o.amount) !== Number(s.price)) {
    insertOrder.run(orderID, o.captureId, o.email, o.name, Number(o.amount) || 0, o.currency || s.currency, 'failed');
    return c.json({ error: 'Payment not completed' }, 402);
  }
  insertOrder.run(orderID, o.captureId, o.email, o.name, Number(o.amount), o.currency, 'paid');

  if (o.email) {
    sendDownloadEmail(s, { to: o.email, name: o.name, link: downloadLink(c, s, orderID) })
      .then(() => markEmailSent.run(orderID))
      .catch((e) => console.error('email', orderID, e.message));
  }
  return c.json({ token: makeToken(`dl:${orderID}`, 7 * DAY) });
});

app.get('/api/download', (c) => {
  const payload = readToken(c.req.query('t'));
  if (!payload || !payload.startsWith('dl:')) return c.text('Download link is invalid or expired.', 403);
  const orderId = payload.slice(3);
  const order = getOrder.get(orderId);
  if (!order || order.status !== 'paid') return c.text('This order is not active.', 403);
  const f = FILES[c.req.query('f') || 'workbook'];
  if (!f) return c.text('Unknown file.', 404);
  const path = `${FILES_DIR}/${f[0]}`;
  if (!existsSync(path)) return c.text('File not available yet. Please contact support.', 404);
  if (f === FILES.workbook) bumpDownloads.run(orderId);
  return new Response(Readable.toWeb(createReadStream(path)), {
    headers: {
      'Content-Type': 'application/pdf',
      'Content-Length': String(statSync(path).size),
      'Content-Disposition': `attachment; filename="${f[1]}"`,
      'Cache-Control': 'private, no-store',
    },
  });
});

/* ---------- admin ---------- */

const attempts = new Map(); // ip -> {n, until}
function safeEq(a, b) {
  const x = Buffer.from(a), y = Buffer.from(b);
  return x.length === y.length && timingSafeEqual(x, y);
}

app.post('/admin/api/login', async (c) => {
  const ip = c.req.header('x-forwarded-for')?.split(',')[0].trim() || 'local';
  const a = attempts.get(ip) || { n: 0, until: 0 };
  if (Date.now() < a.until) return c.json({ error: 'Too many attempts. Try again in 15 minutes.' }, 429);
  const { password } = await c.req.json().catch(() => ({}));
  if (!password || !safeEq(password, ADMIN_PASSWORD)) {
    a.n++; if (a.n >= 5) { a.n = 0; a.until = Date.now() + 15 * 60 * 1000; }
    attempts.set(ip, a);
    return c.json({ error: 'Wrong password' }, 401);
  }
  attempts.delete(ip);
  setCookie(c, 'admin', makeToken('admin', 12 * 60 * 60 * 1000), { httpOnly: true, sameSite: 'Strict', path: '/admin', secure: (c.req.header('x-forwarded-proto') || new URL(c.req.url).protocol.replace(':', '')) === 'https', maxAge: 12 * 3600 });
  return c.json({ ok: true });
});
app.post('/admin/api/logout', (c) => { deleteCookie(c, 'admin', { path: '/admin' }); return c.json({ ok: true }); });

app.use('/admin/api/*', async (c, next) => {
  if (c.req.path === '/admin/api/login') return next();
  if (readToken(getCookie(c, 'admin')) !== 'admin') return c.json({ error: 'Unauthorized' }, 401);
  await next();
});

app.get('/admin/api/stats', (c) => c.json(stats()));
app.get('/admin/api/funnel', (c) => c.json(funnel(Math.max(0, Number(c.req.query('days')) || 0))));
app.get('/admin/api/orders', (c) => {
  const page = Math.max(1, Number(c.req.query('page')) || 1);
  return c.json(listOrders({ q: c.req.query('q') || '', limit: 50, offset: (page - 1) * 50 }));
});

app.get('/admin/api/orders/:id/link', (c) => c.json({ link: downloadLink(c, getSettings(), c.req.param('id')) }));

app.post('/admin/api/orders/:id/resend', async (c) => {
  const order = getOrder.get(c.req.param('id'));
  if (!order) return c.json({ error: 'Not found' }, 404);
  const { email } = await c.req.json().catch(() => ({}));
  const to = email || order.email;
  if (!to) return c.json({ error: 'No email on this order' }, 400);
  const s = getSettings();
  try {
    await sendDownloadEmail(s, { to, name: order.name, link: downloadLink(c, s, order.paypal_order_id) });
    markEmailSent.run(order.paypal_order_id);
    return c.json({ ok: true });
  } catch (e) { return c.json({ error: e.message }, 500); }
});

app.post('/admin/api/orders/:id/status', async (c) => {
  const { status } = await c.req.json().catch(() => ({}));
  if (!['paid', 'refunded', 'failed'].includes(status)) return c.json({ error: 'Bad status' }, 400);
  updateStatus.run(status, c.req.param('id'));
  return c.json({ ok: true });
});

app.get('/admin/api/settings', (c) => {
  const s = getSettings();
  const masked = { ...s };
  for (const k of ['paypal_secret', 'smtp_pass', 'mk_api_token']) masked[k] = s[k] ? '••••••••' : '';
  masked._has = { paypal_secret: !!s.paypal_secret, smtp_pass: !!s.smtp_pass, mk_api_token: !!s.mk_api_token };
  return c.json(masked);
});
app.post('/admin/api/settings', async (c) => {
  const body = await c.req.json().catch(() => ({}));
  const clean = {};
  for (const k of Object.keys(DEFAULTS)) {
    if (!(k in body)) continue;
    const v = String(body[k]).trim();
    if (v === '••••••••') continue; // untouched masked secret
    clean[k] = v;
  }
  if (clean.price && !/^\d+(\.\d{1,2})?$/.test(clean.price)) return c.json({ error: 'Price must be like 17.00' }, 400);
  if (clean.paypal_env && !['live', 'sandbox'].includes(clean.paypal_env)) return c.json({ error: 'Bad env' }, 400);
  if (clean.mail_method && !['api', 'smtp'].includes(clean.mail_method)) return c.json({ error: 'Bad mail method' }, 400);
  if (clean.ga_id && !/^G-[A-Z0-9]{4,20}$/i.test(clean.ga_id)) return c.json({ error: 'Google Analytics ID must look like G-XXXXXXX' }, 400);
  if (clean.meta_pixel_id && !/^\d{6,20}$/.test(clean.meta_pixel_id)) return c.json({ error: 'Meta Pixel ID must be digits only' }, 400);
  saveSettings(clean);
  return c.json({ ok: true });
});
app.post('/admin/api/test/paypal', async (c) => {
  try { await testCredentials(getSettings()); return c.json({ ok: true }); }
  catch (e) { return c.json({ error: e.message }, 400); }
});
app.post('/admin/api/test/email', async (c) => {
  const { to } = await c.req.json().catch(() => ({}));
  if (!to || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(to)) return c.json({ error: 'Enter a valid email address' }, 400);
  try { await sendTestEmail(getSettings(), to); return c.json({ ok: true }); }
  catch (e) { return c.json({ error: e.message }, 400); }
});
app.post('/admin/api/test/smtp', async (c) => {
  try { await testSmtp(getSettings()); return c.json({ ok: true }); }
  catch (e) { return c.json({ error: e.message }, 400); }
});

/* ---------- static ---------- */
app.get('/admin', (c) => c.redirect('/admin/'));
app.use('/admin/*', serveStatic({ root: './private', rewriteRequestPath: (p) => p.replace(/^\/admin\/?$/, '/admin.html') }));
// Clean URLs: /terms serves terms.html; old *.html links 301 to the clean form (query string kept).
app.use('/*', async (c, next) => {
  const p = c.req.path;
  if (p.endsWith('.html')) {
    const clean = p === '/index.html' ? '/' : p.slice(0, -5);
    const q = new URL(c.req.url).search;
    return c.redirect(clean + q, 301);
  }
  await next();
});

// HTML pages are served from memory with cache-busting ?v=<content hash> added to every local asset,
// so Cloudflare always fetches a fresh copy when a CSS/JS/image file changes.
const PUBLIC = './public';
const assetVersion = new Map();
function versionOf(file) {
  if (!assetVersion.has(file)) {
    try { assetVersion.set(file, createHash('sha1').update(readFileSync(`${PUBLIC}/${file}`)).digest('hex').slice(0, 10)); }
    catch { assetVersion.set(file, null); }
  }
  return assetVersion.get(file);
}
// Any local asset reference: "file.ext", "/file.ext", "https://firstflake.com/file.ext", also inside srcset lists.
const ASSET_RE = /(["\s,])((?:https:\/\/firstflake\.com)?\/?)([\w.-]+\.(?:css|js|webp|jpg|jpeg|png|ico|svg))(?=["\s,])/g;
const EDGE_CACHEABLE = new Set(['index', 'privacy', 'terms', 'sales-policy', 'checkout']);
const pages = new Map();
function renderPage(name) {
  if (!pages.has(name)) {
    let html = null;
    try {
      html = readFileSync(`${PUBLIC}/${name}.html`, 'utf8');
      // Inline the small stylesheet so it doesn't block first paint.
      const css = readFileSync(`${PUBLIC}/style.css`, 'utf8').replace(/\s*\n\s*/g, '');
      html = html.replace(/<link rel="stylesheet" href="\/?style\.css">/, () => `<style>${css}</style>`);
      html = html.replace(ASSET_RE, (m, lead, prefix, file) => {
        const v = versionOf(file);
        return v ? `${lead}${prefix}${file}?v=${v}` : m;
      });
      // Cloudflare Email Obfuscation would inject a render-blocking script; opt this page out.
      html = html.replace(/<body([^>]*)>/, '<body$1><!--email_off-->').replace('</body>', '<!--/email_off--></body>');
    } catch { html = null; }
    pages.set(name, html);
  }
  return pages.get(name);
}
app.get('/*', async (c, next) => {
  const p = c.req.path;
  if (/\.[a-z0-9]+$/i.test(p)) {
    await next();
    // Versioned asset URLs never change content, so they can be cached for a long time.
    if (c.req.query('v') && c.res.status === 200) c.res.headers.set('Cache-Control', 'public, max-age=31536000, immutable');
    return;
  }
  const name = p === '/' || p === '' ? 'index' : p.replace(/^\/|\/$/g, '');
  const html = /^[\w-]+$/.test(name) ? renderPage(name) : null;
  if (!html) return next();
  // Static pages may be cached at Cloudflare's edge for 5 minutes (needs a Cache Rule in Cloudflare to take effect).
  const cc = EDGE_CACHEABLE.has(name) ? 'public, max-age=0, s-maxage=300' : 'no-cache';
  return c.html(html, 200, { 'Cache-Control': cc });
});
app.use('/*', serveStatic({ root: PUBLIC }));

serve({ fetch: app.fetch, port: PORT }, () => console.log(`First Flake running on :${PORT}`));
