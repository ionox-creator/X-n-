import { NextResponse } from "next/server";
import { createHash } from "crypto";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const VALID_HASH = "6f6049bdc7afd3800d1cb877887eddd46faf5b26f35c2d73914af187ea54a69f";

export async function POST(req: Request) {
  try {
    const { key } = await req.json();
    if (!key || typeof key !== "string" || key.trim().length === 0) {
      return NextResponse.json({ valid: false, error: "Please enter a valid key" });
    }
    const hash = createHash("sha256").update(key.trim().toUpperCase()).digest("hex");
    if (hash === VALID_HASH) {
      return NextResponse.json({ valid: true, label: "Enterprise" });
    }
    return NextResponse.json({ valid: false, error: "Invalid license key" });
  } catch {
    return NextResponse.json({ valid: false, error: "Invalid request" });
  }
}
