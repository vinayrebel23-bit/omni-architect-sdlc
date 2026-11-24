use std::process::Command;

#[test]
fn forge_dst_seed_sweep_stays_local() {
    let exe = env!("CARGO_BIN_EXE_omni-architect");
    let before = tcp_lines();
    // Kickoff requires FORGE_DST_SEED=0..32. The Termux sweep stopped at 16.
    // The fault table is `seed % 6`, so 0..32 covers the same faults more than once
    // and still must open zero sockets.
    for seed in 0..32u32 {
        let out = Command::new(exe)
            .env("FORGE_DST_SEED", seed.to_string())
            .env("OPENROUTER_API_KEY", "dst-not-a-secret")
            .env_remove("OMNI_ALLOW_REMOTE")
            .arg("dst-once")
            .output()
            .unwrap_or_else(|err| panic!("spawn: {err}"));
        let stderr = String::from_utf8_lossy(&out.stderr);
        assert!(out.status.success(), "seed {seed}: {stderr}");
        let job: serde_json::Value = serde_json::from_slice(&out.stdout)
            .unwrap_or_else(|err| panic!("json seed {seed}: {err}: {stderr}"));
        assert_eq!(job["sockets_opened"], 0, "seed {seed}");
        match seed % 6 {
            0 => {
                assert_eq!(job["fault"], "timeout");
                assert_eq!(job["ci_status"], "fail");
            }
            1 => {
                assert_eq!(job["fault"], "nonzero");
                assert_eq!(job["ci_status"], "fail");
            }
            2 => assert_eq!(job["fault"], "dropped"),
            3 => {
                assert_eq!(job["fault"], "malformed");
                assert!(job["error"].as_str().unwrap_or("").contains("malformed"));
            }
            4 => {
                assert_eq!(job["fault"], "retry");
                assert_eq!(job["attempts"], 3);
                assert_eq!(job["ci_status"], "fail");
            }
            _ => {
                assert_eq!(job["fault"], "ok");
                assert_eq!(job["ci_status"], "pass");
            }
        }
    }
    let after = tcp_lines();
    assert_eq!(before, after, "tcp socket table changed during the sweep");
}

fn tcp_lines() -> usize {
    if cfg!(windows) {
        // `netstat -ano` lists every TCP row on the machine. Only rows owned
        // by this process count. A host-wide delta is other software, not a socket
        // opened by the router.
        let pid = std::process::id().to_string();
        let Ok(out) = std::process::Command::new("netstat")
            .args(["-ano", "-p", "tcp"])
            .output()
        else {
            return 0;
        };
        let text = String::from_utf8_lossy(&out.stdout);
        return text
            .lines()
            .filter(|line| {
                line.contains("TCP") && line.split_whitespace().last() == Some(pid.as_str())
            })
            .count();
    }
    let text = std::fs::read_to_string("/proc/self/net/tcp").unwrap_or_default();
    text.lines()
        .skip(1)
        .filter(|line| !line.trim().is_empty())
        .count()
}
