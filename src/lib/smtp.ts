import nodemailer from "nodemailer";

let transporter: nodemailer.Transporter | null = null;

export function getTransporter() {
  if (transporter) return transporter;

  transporter = nodemailer.createTransport({
    service: "gmail",
    auth: {
      user: process.env.SMTP_USER || "ionoxspace@gmail.com",
      pass: process.env.SMTP_PASS || "",
    },
  });

  return transporter;
}

export async function sendLicenseRequestEmail(name: string, email: string) {
  const transport = getTransporter();
  const smtpUser = process.env.SMTP_USER || "ionoxspace@gmail.com";

  await transport.sendMail({
    from: smtpUser,
    to: smtpUser,
    subject: "Fintel Licence Key Request",
    text: `New licence key request:\n\nName: ${name}\nEmail: ${email}\n\nPlease send them a Fintel licence key.`,
    html: `<h2>New Licence Key Request</h2><p><strong>Name:</strong> ${name}</p><p><strong>Email:</strong> ${email}</p><p>Please send them a Fintel licence key.</p>`,
    replyTo: email,
  });
}
