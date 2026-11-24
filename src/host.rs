//! Host commands for the local verifier. Linux keeps `/bin/true` and
//! `/bin/false`. Windows uses `cmd /c exit`, which is present on every
//! install and does not open a socket.

pub fn true_program() -> String {
    if cfg!(windows) {
        "cmd".to_string()
    } else {
        "/bin/true".to_string()
    }
}

pub fn true_args() -> Vec<String> {
    if cfg!(windows) {
        vec!["/c".to_string(), "exit".to_string(), "0".to_string()]
    } else {
        Vec::new()
    }
}

pub fn false_program() -> String {
    if cfg!(windows) {
        "cmd".to_string()
    } else {
        "/bin/false".to_string()
    }
}

pub fn false_args() -> Vec<String> {
    if cfg!(windows) {
        vec!["/c".to_string(), "exit".to_string(), "1".to_string()]
    } else {
        Vec::new()
    }
}

pub fn sleep_program() -> String {
    if cfg!(windows) {
        // python.exe is on this host (TOOLCHAIN.json). `ping` opens a socket
        // and would fail the DST row-count gate. A local sleep does not.
        "python".to_string()
    } else {
        "/bin/sleep".to_string()
    }
}

pub fn sleep_args(seconds: &str) -> Vec<String> {
    if cfg!(windows) {
        let seconds = if seconds.is_empty() { "2" } else { seconds };
        vec![
            "-c".to_string(),
            format!("import time; time.sleep({seconds})"),
        ]
    } else {
        vec![seconds.to_string()]
    }
}

pub fn peak_rss_kb() -> u64 {
    if cfg!(windows) {
        return peak_rss_windows();
    }
    let Ok(text) = std::fs::read_to_string("/proc/self/status") else {
        return 0;
    };
    for line in text.lines() {
        let Some(rest) = line.strip_prefix("VmHWM:") else {
            continue;
        };
        let Some(raw) = rest.split_whitespace().next() else {
            continue;
        };
        if let Ok(value) = raw.parse() {
            return value;
        }
    }
    0
}

fn peak_rss_windows() -> u64 {
    // `tasklist` prints the working set as "12,345 K". Strip grouping
    // separators and keep the value in KB. Parse failure is 0, not a guess.
    let Ok(out) = std::process::Command::new("tasklist")
        .args([
            "/FI",
            &format!("PID eq {}", std::process::id()),
            "/FO",
            "CSV",
            "/NH",
        ])
        .output()
    else {
        return 0;
    };
    let text = String::from_utf8_lossy(&out.stdout);
    let Some(line) = text.lines().find(|l| l.contains(',')) else {
        return 0;
    };
    // CSV: "image","pid","session","session#","12,345 K"
    // The memory field itself contains a thousands-separator comma, so a
    // split on every comma lands on the last digit group ("345 K") and
    // reports 345 instead of 12345. Take the field after the fourth quote-comma.
    let parts: Vec<&str> = line.split(",").collect();
    if parts.len() < 5 {
        return 0;
    }
    let mem = parts[4..].join(",");
    let digits: String = mem.chars().filter(|c| c.is_ascii_digit()).collect();
    digits.parse::<u64>().unwrap_or(0)
}
