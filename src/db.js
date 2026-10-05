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
  CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    secret INTEGER DEFAULT 0
  );
`);

// Keys ending in "_secret"/"_pass" are stored encrypted.
const SECRET_KEYS = new Set(['paypal_secret', 'smtp_pass']);

export const DEFAULTS = {
  paypal_env: 'sandbox',
  paypal_client_id: '',
  paypal_secret: '',
  price: '17.00',
  currency: 'USD',
  product_name: 'First Flake: 7-Trip Field Workbook (PDF)',
  smtp_host: 'smtp.mailketing.co.id',
  smtp_port: '587',
  smtp_user: '',
  smtp_pass: '',
  smtp_from: '',
  site_url: 'https://firstflake.com',
  support_email: 'hello@firstflake.com',
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
