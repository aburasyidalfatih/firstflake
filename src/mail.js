import nodemailer from 'nodemailer';

// Two ways to send: Mailketing HTTP API (default, recommended by Mailketing) or plain SMTP.
const MK_API = 'https://api.mailketing.co.id/api/v1/send';

function fromParts(s) {
  // smtp_from may be "Name <email>" or just "email"
  const m = /^\s*(.*?)\s*<([^>]+)>\s*$/.exec(s.smtp_from || '');
  const email = (m ? m[2] : s.smtp_from || '').trim();
  const name = (s.from_name || (m && m[1]) || 'First Flake').trim();
  return { name, email };
}

function transport(s) {
  const port = Number(s.smtp_port) || 587;
  return nodemailer.createTransport({
    host: s.smtp_host,
    port,
    secure: port === 465,
    auth: { user: s.smtp_user, pass: s.smtp_pass },
    connectionTimeout: 15000,
    greetingTimeout: 10000,
    socketTimeout: 20000,
  });
}

async function sendViaApi(s, { to, subject, text }) {
  if (!s.mk_api_token) throw new Error('Mailketing API token is not set');
  const { name, email } = fromParts(s);
  if (!email) throw new Error('From email is not set');
  const body = new URLSearchParams({
    api_token: s.mk_api_token,
    from_name: name,
    from_email: email,
    recipient: to,
    subject,
    content: text.replace(/\n/g, '<br>\n'),
  });
  const r = await fetch(MK_API, { method: 'POST', body, signal: AbortSignal.timeout(20000) });
  const j = await r.json().catch(() => ({}));
  if (j.status !== 'success') throw new Error(`Mailketing: ${j.response || `HTTP ${r.status}`}`);
  return j.response;
}

async function sendViaSmtp(s, { to, subject, text }) {
  if (!s.smtp_host || !s.smtp_user || !s.smtp_from) throw new Error('SMTP not configured');
  const { name, email } = fromParts(s);
  const info = await transport(s).sendMail({ from: { name, address: email }, to, subject, text });
  return info.messageId;
}

function send(s, msg) {
  return (s.mail_method === 'smtp' ? sendViaSmtp : sendViaApi)(s, msg);
}

export async function sendDownloadEmail(s, { to, name, link }) {
  const first = (name || '').split(' ')[0] || 'friend';
  const support = s.support_email || fromParts(s).email;
  return send(s, {
    to,
    subject: 'Your First Flake workbook is ready to download',
    text: `Hi ${first},

Thank you for your purchase! Here is your download page for ${s.product_name} and your 4 bonus guides:

${link}

The link works for 7 days. Save every PDF somewhere safe, then print the log pages, the Creek Card, and the Is It Gold? card.

First step tonight: read "A Letter from Josie" on page 4, score yourself on page 6, then spend one evening on "Choose Your Creek" (page 11). Trip 1 happens in a backyard tub, so you can start this weekend.

Questions? Just reply to this email or write to ${support}.

Read the river. It already knows where the gold is.
— First Flake`,
  });
}

export async function sendTestEmail(s, to) {
  return send(s, {
    to,
    subject: 'First Flake test email',
    text: `This is a test email from your First Flake admin dashboard.

If you can read this, buyers will receive their download emails from ${fromParts(s).email} (sent via ${s.mail_method === 'smtp' ? 'SMTP' : 'the Mailketing API'}).

Tip: check that this landed in the inbox, not spam. If it went to spam, add the SPF and DKIM records Mailketing gives you for your sending domain.

Sent ${new Date().toUTCString()}`,
  });
}

export async function testSmtp(s) {
  if (s.mail_method === 'api') throw new Error('Send method is Mailketing API. Use "Send test email" instead.');
  await transport(s).verify();
  return true;
}
