import { NextResponse } from "next/server";
import { sendLicenseRequestEmail } from "@/lib/smtp";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  try {
    const { name, email } = await req.json();

    if (!name || !email) {
      return NextResponse.json({ success: false, error: "Name and email are required" });
    }

    await sendLicenseRequestEmail(name, email);

    return NextResponse.json({
      success: true,
      message: "Request sent! We will reply with your key shortly.",
    });
  } catch (error) {
    console.error("[Request License] Error:", error);
    return NextResponse.json(
      { success: false, error: "Failed to send request. Please try again." },
      { status: 500 }
    );
  }
}
