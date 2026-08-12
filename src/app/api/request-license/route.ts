import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  try {
    const { name, email } = await req.json();
    if (!name || !email) {
      return NextResponse.json({ success: false, error: "Name and email required" });
    }
    return NextResponse.json({ success: true, message: "Request sent!" });
  } catch {
    return NextResponse.json({ success: false, error: "Failed" });
  }
}
