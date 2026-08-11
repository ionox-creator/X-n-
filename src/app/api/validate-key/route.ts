import { NextResponse } from "next/server";
import { createHash } from "crypto";
import { getDB, initLicenseKeys } from "@/lib/db";
import { getKeyHashes } from "@/lib/license-keys";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

let initialized = false;

function ensureInitialized() {
  if (!initialized) {
    try {
      initLicenseKeys(getKeyHashes());
      initialized = true;
    } catch (e) {
      console.error("[Validate Key] Init error:", e);
    }
  }
}

export async function POST(req: Request) {
  try {
    const { key, deviceFp, deviceInfo } = await req.json();

    if (!key || typeof key !== "string" || key.trim().length === 0) {
      return NextResponse.json({ valid: false, error: "Please enter a valid key" });
    }

    if (!deviceFp || typeof deviceFp !== "string") {
      return NextResponse.json({ valid: false, error: "Device fingerprint required" });
    }

    ensureInitialized();

    const hash = createHash("sha256").update(key.trim().toUpperCase()).digest("hex");
    const db = getDB();

    const row = db.prepare("SELECT * FROM LicenseKey WHERE keyHash = ?").get(hash) as any;

    if (!row) {
      return NextResponse.json({ valid: false, error: "Invalid license key" });
    }

    if (row.deviceFp === null) {
      db.prepare("UPDATE LicenseKey SET deviceFp = ?, deviceInfo = ?, boundAt = ?, usedCount = usedCount + 1 WHERE id = ?")
        .run(deviceFp, deviceInfo || "", Date.now(), row.id);
      return NextResponse.json({
        valid: true,
        label: row.keyLabel || "Enterprise",
        deviceBound: true,
      });
    } else if (row.deviceFp === deviceFp) {
      db.prepare("UPDATE LicenseKey SET usedCount = usedCount + 1 WHERE id = ?").run(row.id);
      return NextResponse.json({
        valid: true,
        label: row.keyLabel || "Enterprise",
        deviceBound: false,
      });
    } else {
      return NextResponse.json({
        valid: false,
        error: "This license key is already activated on another device",
      });
    }
  } catch (error) {
    console.error("[Validate Key] Error:", error);
    return NextResponse.json({ valid: false, error: "Invalid request" });
  }
}
