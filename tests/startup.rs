use std::process::Command;

#[test]
fn process_exits_nonzero_without_api_key() {
    let exe = env!("CARGO_BIN_EXE_omni-architect");
    let out = Command::new(exe)
        .env_remove("OPENROUTER_API_KEY")
        .env_remove("OMNI_CONFIG_FILE")
        .arg("health")
        .output()
        .unwrap_or_else(|err| panic!("spawn: {err}"));
    assert!(
        !out.status.success(),
        "health succeeded without a key: {}",
        String::from_utf8_lossy(&out.stdout)
    );
    let stderr = String::from_utf8_lossy(&out.stderr);
    assert!(
        stderr.contains("OPENROUTER_API_KEY is unset"),
        "stderr: {stderr}"
    );
    assert!(!stderr.contains("sk-or-"));
}
