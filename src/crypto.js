import { createCipheriv, createDecipheriv, createHmac, randomBytes, scryptSync, timingSafeEqual } from 'node:crypto';

const APP_SECRET = process.env.APP_SECRET;
if (!APP_SECRET || APP_SECRET.length < 16) {
  console.error('APP_SECRET env var is required (at least 16 random characters).');
  process.exit(1);
}
const KEY = scryptSync(APP_SECRET, 'firstflake-salt', 32);

// AES-256-GCM for secrets stored in the database.
export function encrypt(text) {
  const iv = randomBytes(12);
  const c = createCipheriv('aes-256-gcm', KEY, iv);
  const enc = Buffer.concat([c.update(text, 'utf8'), c.final()]);
  return Buffer.concat([iv, c.getAuthTag(), enc]).toString('base64');
}
export function decrypt(b64) {
  const buf = Buffer.from(b64, 'base64');
  const d = createDecipheriv('aes-256-gcm', KEY, buf.subarray(0, 12));
  d.setAuthTag(buf.subarray(12, 28));
  return Buffer.concat([d.update(buf.subarray(28)), d.final()]).toString('utf8');
}

// HMAC-signed tokens: "<payload>.<exp>.<sig>"
function sign(data) {
  return createHmac('sha256', KEY).update(data).digest('base64url');
}
export function makeToken(payload, ttlMs) {
  const exp = Date.now() + ttlMs;
  const body = `${payload}.${exp}`;
  return `${body}.${sign(body)}`;
}
export function readToken(token) {
  if (!token) return null;
  const i = token.lastIndexOf('.');
  if (i < 0) return null;
  const body = token.slice(0, i), sig = token.slice(i + 1);
  const expected = sign(body);
  if (sig.length !== expected.length || !timingSafeEqual(Buffer.from(sig), Buffer.from(expected))) return null;
  const j = body.lastIndexOf('.');
  const exp = Number(body.slice(j + 1));
  if (!exp || Date.now() > exp) return null;
  return body.slice(0, j);
}
