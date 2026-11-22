use anyhow::{Context, Result};
use serde::Serialize;
use std::process::{Command, Stdio};
use std::thread;
use std::time::{Duration, Instant};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "lowercase")]
pub enum CiStatus {
    Pass,
    Fail,
}

impl CiStatus {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Pass => "pass",
            Self::Fail => "fail",
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
pub struct VerifyReport {
    pub status: CiStatus,
    pub exit_code: Option<i32>,
    pub fault: String,
    pub attempts: u32,
    pub sockets_opened: u32,
    pub error: Option<String>,
}

/// Runs a local command. `pass` is returned only when the process exits 0.
pub fn run_command(program: &str, args: &[String], timeout: Duration) -> Result<VerifyReport> {
    let mut child = Command::new(program)
        .args(args)
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .with_context(|| format!("failed to spawn {program}"))?;
    let started = Instant::now();
    loop {
        if let Some(status) = child.try_wait()? {
            let exit_code = status.code();
            let ok = status.success();
            return Ok(VerifyReport {
                status: if ok { CiStatus::Pass } else { CiStatus::Fail },
                exit_code,
                fault: if ok {
                    "ok".to_string()
                } else {
                    "nonzero".to_string()
                },
                attempts: 1,
                sockets_opened: 0,
                error: if ok {
                    None
                } else {
                    Some(format!("{program} exited {exit_code:?}"))
                },
            });
        }
        if started.elapsed() >= timeout {
            let _ = child.kill();
            let _ = child.wait();
            return Ok(VerifyReport {
                status: CiStatus::Fail,
                exit_code: None,
                fault: "timeout".to_string(),
                attempts: 1,
                sockets_opened: 0,
                error: Some(format!("{program} exceeded {timeout:?}")),
            });
        }
        thread::sleep(Duration::from_millis(5));
    }
}

pub fn fault_for_seed(seed: u32) -> &'static str {
    match seed % 6 {
        0 => "timeout",
        1 => "nonzero",
        2 => "dropped",
        3 => "malformed",
        4 => "retry",
        _ => "ok",
    }
}

/// Local verifier faults for `FORGE_DST_SEED`. Does not open a socket.
/// `ok` and `nonzero` spawn `/bin/true` and `/bin/false`. Other faults are injected
/// at this seam so the sweep does not sleep through 16 real timeouts.
pub fn run_dst_seed(seed: u32) -> Result<VerifyReport> {
    match fault_for_seed(seed) {
        "timeout" => Ok(injected("timeout", 1, "timeout")),
        "nonzero" => run_command("/bin/false", &[], Duration::from_secs(2)),
        "dropped" => Ok(injected("dropped", 1, "dropped connection")),
        "malformed" => Ok(injected("malformed", 1, "malformed payload")),
        "retry" => {
            let mut attempts = 0u32;
            while attempts < 3 {
                attempts = attempts.saturating_add(1);
                thread::sleep(Duration::from_millis(1));
            }
            Ok(injected("retry", attempts, "bounded retry exhausted"))
        }
        _ => run_command("/bin/true", &[], Duration::from_secs(2)),
    }
}

fn injected(fault: &str, attempts: u32, error: &str) -> VerifyReport {
    VerifyReport {
        status: CiStatus::Fail,
        exit_code: None,
        fault: fault.to_string(),
        attempts,
        sockets_opened: 0,
        error: Some(error.to_string()),
    }
}

#[cfg(test)]
mod tests {
    use super::{CiStatus, run_command};
    use std::time::Duration;

    #[test]
    fn exit_zero_is_pass_and_exit_one_is_fail() {
        let ok = run_command("/bin/true", &[], Duration::from_secs(2)).expect("true");
        assert_eq!(ok.status, CiStatus::Pass);
        assert_eq!(ok.sockets_opened, 0);
        let bad = run_command("/bin/false", &[], Duration::from_secs(2)).expect("false");
        assert_eq!(bad.status, CiStatus::Fail);
        assert_ne!(bad.exit_code, Some(0));
        assert_eq!(bad.sockets_opened, 0);
    }

    #[test]
    fn timeout_is_fail_and_does_not_open_a_socket() {
        let got = run_command("/bin/sleep", &["2".to_string()], Duration::from_millis(40))
            .expect("sleep");
        assert_eq!(got.status, CiStatus::Fail);
        assert_eq!(got.fault, "timeout");
        assert_eq!(got.sockets_opened, 0);
    }
}
