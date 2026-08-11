export async function register() {
  if (process.env.NEXT_RUNTIME === "nodejs") {
    try {
      const { getDB, initLicenseKeys } = await import("@/lib/db");
      const { getKeyHashes } = await import("@/lib/license-keys");
      const db = getDB();
      initLicenseKeys(getKeyHashes());
      console.log("[Fintel] License database initialized with 55 keys");
    } catch (e) {
      console.error("[Fintel] DB init error:", e);
    }
  }
}
