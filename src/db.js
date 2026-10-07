import { DatabaseSync } from 'node:sqlite';
import { mkdirSync } from 'node:fs';
import { dirname } from 'node:path';
import { encrypt, decrypt } from './crypto.js';

const DB_PATH = process.env.DB_PATH || './data/app.db';
mkdirSync(dirname(DB_PATH), { recursive: true });

export const db = new DatabaseSync(DB_PATH);
db.exec(`
  PRAGMA journal_mode = WAL;
  CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paypal_order_id TEXT UNIQUE NOT NULL,
    capture_id TEXT,
    email TEXT,
    name TEXT,
    amount REAL NOT NULL,
    currency TEXT NOT NULL,
    status TEXT NOT NULL,
    email_sent INTEGER DEFAULT 0,
    downloads INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
  );
  CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT DEFAULT (datetime('now')),
    type TEXT NOT NULL,
    vid TEXT NOT NULL,
    source TEXT
  );
  CREATE INDEX IF NOT EXISTS events_type_ts ON events(type, ts);
  CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    secret INTEGER DEFAULT 0
  );
`);

// Keys ending in "_secret"/"_pass" are stored encrypted.
const SECRET_KEYS = new Set(['paypal_secret', 'smtp_pass', 'mk_api_token']);

export const DEFAULTS = {
  paypal_env: 'sandbox',
  paypal_client_id: '',
  paypal_secret: '',
  price: '9.00',
  currency: 'USD',
  product_name: 'First Flake: 7-Trip Field Workbook (PDF)',
  smtp_host: 'smtp.mailketing.co.id',
  smtp_port: '587',
  smtp_user: '',
  smtp_pass: '',
  smtp_from: 'hello@firstflake.com',
  from_name: 'Josie at First Flake',
  mail_method: 'api',
  mk_api_token: '',
  site_url: 'https://firstflake.com',
  support_email: 'hello@firstflake.com',
  ga_id: '',
  meta_pixel_id: '',
};

export function getSettings() {
  const out = { ...DEFAULTS };
  for (const row of db.prepare('SELECT key, value, secret FROM settings').all()) {
    out[row.key] = row.secret ? decrypt(row.value) : row.value;
  }
  return out;
}

export function saveSettings(obj) {
  const stmt = db.prepare('INSERT INTO settings (key, value, secret) VALUES (?, ?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value, secret = excluded.secret');
  for (const [k, v] of Object.entries(obj)) {
    if (!(k in DEFAULTS)) continue;
    const isSecret = SECRET_KEYS.has(k);
    if (isSecret && v === '') continue; // blank secret field = keep existing
    stmt.run(k, isSecret ? encrypt(String(v)) : String(v), isSecret ? 1 : 0);
  }
}

export const insertOrder = db.prepare(`
  INSERT INTO orders (paypal_order_id, capture_id, email, name, amount, currency, status)
  VALUES (?, ?, ?, ?, ?, ?, ?)
  ON CONFLICT(paypal_order_id) DO UPDATE SET capture_id = excluded.capture_id, status = excluded.status`);
export const markEmailSent = db.prepare('UPDATE orders SET email_sent = 1 WHERE paypal_order_id = ?');
export const bumpDownloads = db.prepare('UPDATE orders SET downloads = downloads + 1 WHERE paypal_order_id = ?');
export const getOrder = db.prepare('SELECT * FROM orders WHERE paypal_order_id = ?');
export const updateStatus = db.prepare('UPDATE orders SET status = ? WHERE paypal_order_id = ?');

export function listOrders({ q = '', limit = 50, offset = 0 }) {
  const like = `%${q}%`;
  return db.prepare(`SELECT * FROM orders WHERE email LIKE ? OR paypal_order_id LIKE ? OR name LIKE ?
    ORDER BY id DESC LIMIT ? OFFSET ?`).all(like, like, like, limit, offset);
}

export const insertEvent = db.prepare('INSERT INTO events (type, vid, source) VALUES (?, ?, ?)');
export const seenToday = db.prepare("SELECT 1 FROM events WHERE type = ? AND vid = ? AND date(ts) = date('now') LIMIT 1");

// Funnel for the last `days` days (0 = all time). Unique visitors per step; paid comes from orders.
export function funnel(days) {
  const since = days > 0 ? `datetime('now','-${Number(days)} days')` : `'1970-01-01'`;
  const uniq = (type) => db.prepare(`SELECT COUNT(DISTINCT vid || date(ts)) n FROM events WHERE type = ? AND ts >= ${since}`).get(type).n;
  const paid = db.prepare(`SELECT COUNT(*) n, COALESCE(SUM(amount),0) sum FROM orders WHERE status = 'paid' AND created_at >= ${since}`).get();
  const sources = db.prepare(`SELECT COALESCE(source,'direct') source, COUNT(DISTINCT vid || date(ts)) n FROM events WHERE type = 'view' AND ts >= ${since} GROUP BY 1 ORDER BY n DESC LIMIT 8`).all();
  const daily = db.prepare(`SELECT date(ts) d,
      COUNT(DISTINCT CASE WHEN type='view' THEN vid END) v,
      COUNT(DISTINCT CASE WHEN type='checkout' THEN vid END) c,
      COUNT(DISTINCT CASE WHEN type='pay_click' THEN vid END) p
    FROM events WHERE ts >= datetime('now','-13 days') GROUP BY d ORDER BY d DESC`).all();
  const paidDaily = Object.fromEntries(db.prepare(`SELECT date(created_at) d, COUNT(*) n FROM orders WHERE status='paid' AND created_at >= datetime('now','-13 days') GROUP BY d`).all().map((r) => [r.d, r.n]));
  return {
    view: uniq('view'), checkout: uniq('checkout'), pay_click: uniq('pay_click'),
    paid: paid.n, revenue: paid.sum, sources,
    daily: daily.map((r) => ({ ...r, paid: paidDaily[r.d] || 0 })),
  };
}

export function stats() {
  const paid = "status = 'paid'";
  const one = (sql) => db.prepare(sql).get();
  return {
    total: one(`SELECT COUNT(*) n, COALESCE(SUM(amount),0) sum FROM orders WHERE ${paid}`),
    today: one(`SELECT COUNT(*) n, COALESCE(SUM(amount),0) sum FROM orders WHERE ${paid} AND date(created_at) = date('now')`),
    month: one(`SELECT COUNT(*) n, COALESCE(SUM(amount),0) sum FROM orders WHERE ${paid} AND strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')`),
    refunded: one(`SELECT COUNT(*) n, COALESCE(SUM(amount),0) sum FROM orders WHERE status = 'refunded'`),
    daily: db.prepare(`SELECT date(created_at) d, COUNT(*) n, SUM(amount) sum FROM orders WHERE ${paid} AND created_at >= date('now','-29 days') GROUP BY d ORDER BY d`).all(),
  };
}
