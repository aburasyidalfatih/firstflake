import nodemailer from 'nodemailer';

function transport(s) {
  const port = Number(s.smtp_port) || 587;
  return nodemailer.createTransport({
    host: s.smtp_host,
    port,
    secure: port === 465,
    auth: { user: s.smtp_user, pass: s.smtp_pass },
  });
}

export async function sendDownloadEmail(s, { to, name, link }) {
  if (!s.smtp_host || !s.smtp_user || !s.smtp_from) throw new Error('SMTP not configured');
  const first = (name || '').split(' ')[0] || 'friend';
  const support = s.support_email || s.smtp_from;
  await transport(s).sendMail({
    from: s.smtp_from,
    to,
    subject: 'Your First Flake workbook is ready to download',
    text: `Hi ${first},

Thank you for your purchase! Here is your download link for ${s.product_name}:

${link}

The link works for 7 days. Save the PDF somewhere safe, then print the log pages and the Creek Card.

First step tonight: read "A Letter from Josie" on page 3, then score yourself on page 5. Trip 1 happens in your bathtub, so you can start this weekend.

Questions? Just reply to this email or write to ${support}.

Read the river. It already knows where the gold is.
— First Flake`,
  });
}

export async function testSmtp(s) {
  await transport(s).verify();
  return true;
}
