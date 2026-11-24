use anyhow::{Context, Result};
use rusqlite::{Connection, params};
use std::path::Path;

pub struct Ledger {
    conn: Connection,
}

impl Ledger {
    pub fn open(path: &Path) -> Result<Self> {
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent)?;
        }
        let conn = Connection::open(path)
            .with_context(|| format!("failed to open ledger {}", path.display()))?;
        conn.execute_batch(
            "PRAGMA journal_mode = WAL;
             PRAGMA synchronous = NORMAL;
             PRAGMA busy_timeout = 5000;
             CREATE TABLE IF NOT EXISTS decisions (
                 ticket_id TEXT PRIMARY KEY,
                 swarm TEXT NOT NULL,
                 ci_status TEXT NOT NULL,
                 created_at INTEGER NOT NULL
             );",
        )?;
        Ok(Self { conn })
    }

    pub fn record(&self, ticket_id: &str, swarm: &str, ci_status: &str) -> Result<()> {
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map(|d| d.as_secs() as i64)
            .unwrap_or(0);
        self.conn.execute(
            "INSERT INTO decisions (ticket_id, swarm, ci_status, created_at)
             VALUES (?1, ?2, ?3, ?4)
             ON CONFLICT(ticket_id) DO UPDATE SET
                swarm = excluded.swarm,
                ci_status = excluded.ci_status,
                created_at = excluded.created_at",
            params![ticket_id, swarm, ci_status, now],
        )?;
        Ok(())
    }
}
