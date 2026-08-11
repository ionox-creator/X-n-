import Database from "better-sqlite3";
import path from "path";
import fs from "fs";

let dbInstance: Database.Database | null = null;

export function getDB() {
  if (dbInstance) return dbInstance;

  // Use DATABASE_URL or default path
  const dbPath = process.env.DATABASE_URL?.replace("file:", "") || path.join(process.cwd(), "data", "custom.db");

  // Ensure directory exists
  const dir = path.dirname(dbPath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  dbInstance = new Database(dbPath);

  // Create table if not exists
  dbInstance.exec(`
    CREATE TABLE IF NOT EXISTS LicenseKey (
      id TEXT PRIMARY KEY,
      keyHash TEXT UNIQUE NOT NULL,
      keyLabel TEXT,
      deviceFp TEXT,
      deviceInfo TEXT,
      boundAt INTEGER,
      createdAt INTEGER,
      usedCount INTEGER DEFAULT 0
    )
  `);

  return dbInstance;
}

export function initLicenseKeys(hashes: string[]) {
  const db = getDB();
  const stmt = db.prepare("INSERT OR IGNORE INTO LicenseKey (id, keyHash, keyLabel, createdAt) VALUES (?, ?, ?, ?)");
  const now = Date.now();
  const tx = db.transaction(() => {
    for (let i = 0; i < hashes.length; i++) {
      stmt.run("lk_" + String(i + 1).padStart(3, "0"), hashes[i], "Enterprise", now);
    }
  });
  tx();
}
