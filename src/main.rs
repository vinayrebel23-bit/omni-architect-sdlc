#![forbid(unsafe_code)]

use anyhow::Result;
use clap::{Parser, Subcommand};
use omni_architect::{App, Config, health, run_dst_seed};
use serde::Serialize;
use std::io::{BufRead, BufReader};
use std::path::PathBuf;
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};
#[cfg(unix)]
use std::thread;

#[derive(Parser)]
#[command(name = "omni-architect", about = "Native ticket router")]
struct Cli {
    /// Highest-precedence secret. Never printed.
    #[arg(long, global = true)]
    api_key: Option<String>,
    /// File containing `OPENROUTER_API_KEY=`. Lowest precedence above empty.
    #[arg(long, global = true)]
    config: Option<PathBuf>,
    #[arg(long, global = true)]
    db: Option<PathBuf>,
    #[command(subcommand)]
    cmd: Cmd,
}

#[derive(Subcommand)]
enum Cmd {
    /// Read tickets from stdin until EOF or SIGTERM.
    Serve,
    /// Print a health probe. Does not call a model.
    Health,
    /// Route one already-sanitized intent.
    Route { intent: String },
    /// Run a verifier command and print its CI status.
    Verify {
        #[arg(long)]
        program: Option<String>,
        /// Arguments for the verifier program. Repeat the flag.
        #[arg(long)]
        arg: Vec<String>,
    },
    /// Admit one ticket.
    Admit { id: String, text: String },
    /// Print BenchMetrics JSON for admit+route+local verify+ledger.
    Bench {
        #[arg(long, default_value_t = 200)]
        iters: u32,
        #[arg(long)]
        program: Option<String>,
        /// Arguments for `--program`. Repeat the flag. Required on Windows
        /// when the program is `cmd`, because `cmd` with no args exits 0
        /// without proving a verifier command.
        #[arg(long)]
        arg: Vec<String>,
    },
    /// Print the parsed FORGE_DST_SEED, or `none`.
    DstSeed,
    /// Run one local DST seed. Refuses to open a socket.
    DstOnce,
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    let stop = Arc::new(AtomicBool::new(false));
    install_signals(Arc::clone(&stop))?;
    let config = Config::from_process(cli.api_key.as_deref(), cli.config.as_deref(), cli.db)?;
    match cli.cmd {
        Cmd::Health => {
            let _ = config.has_key();
            println!("{}", health());
        }
        Cmd::Route { intent } => {
            println!("{}", omni_architect::route_swarm(&intent));
        }
        Cmd::Verify { program, arg } => {
            let program = match program {
                Some(program) if !program.is_empty() => program,
                _ => config.verify_program.clone(),
            };
            if program.is_empty() {
                anyhow::bail!("verifier program is unset");
            }
            let args = if arg.is_empty() {
                config.verify_args.clone()
            } else {
                arg
            };
            let report = omni_architect::run_command(&program, &args, config.verify_timeout)?;
            println!("{}", serde_json::to_string(&report)?);
            if report.status == omni_architect::CiStatus::Fail {
                std::process::exit(1);
            }
        }
        Cmd::Admit { id, text } => {
            let mut app = App::open(config)?;
            if stop.load(Ordering::Relaxed) {
                app.stop_admission();
            }
            let decision = app.admit(&id, &text)?;
            println!("{}", serde_json::to_string(&decision)?);
        }
        Cmd::Bench {
            iters,
            program,
            arg,
        } => {
            let mut config = config;
            if let Some(program) = program.filter(|p| !p.is_empty()) {
                config.verify_program = program;
            }
            if !arg.is_empty() {
                config.verify_args = arg;
            }
            let report = omni_architect::bench_metrics(&config, iters)?;
            println!("{}", serde_json::to_string(&report)?);
        }
        Cmd::DstSeed => match std::env::var("FORGE_DST_SEED") {
            Ok(seed) if !seed.is_empty() => println!("{seed}"),
            _ => println!("none"),
        },
        Cmd::DstOnce => {
            if std::env::var("OMNI_ALLOW_REMOTE").ok().as_deref() == Some("1") {
                anyhow::bail!("DST refuses OMNI_ALLOW_REMOTE=1");
            }
            let seed: u32 = std::env::var("FORGE_DST_SEED")
                .ok()
                .and_then(|raw| raw.parse().ok())
                .ok_or_else(|| anyhow::anyhow!("FORGE_DST_SEED is required"))?;
            let report = run_dst_seed(seed)?;
            let body = DstOut {
                seed,
                fault: report.fault.clone(),
                attempts: report.attempts,
                sockets_opened: report.sockets_opened,
                ci_status: report.status.as_str().to_string(),
                error: report.error.clone(),
            };
            println!("{}", serde_json::to_string(&body)?);
        }
        Cmd::Serve => {
            let mut app = App::open(config)?;
            let stdin = std::io::stdin();
            let mut lines = BufReader::new(stdin.lock()).lines();
            let mut n = 0u64;
            loop {
                if stop.load(Ordering::Relaxed) {
                    app.stop_admission();
                    eprintln!("admission stopped");
                    break;
                }
                let Some(line) = lines.next() else {
                    break;
                };
                let line = line?;
                if line.trim().is_empty() {
                    continue;
                }
                n = n.saturating_add(1);
                let decision = app.admit(&format!("t{n}"), line.trim())?;
                println!("{}", serde_json::to_string(&decision)?);
            }
        }
    }
    Ok(())
}

#[derive(Serialize)]
struct DstOut {
    seed: u32,
    fault: String,
    attempts: u32,
    sockets_opened: u32,
    ci_status: String,
    error: Option<String>,
}

fn install_signals(stop: Arc<AtomicBool>) -> Result<()> {
    // Unix keeps the signal-hook iterator so SIGTERM stops admission.
    // Windows has no SIGTERM iterator in that crate; ctrlc covers Ctrl+C
    // and Ctrl-Break, which is the console equivalent of stopping admission.
    #[cfg(unix)]
    {
        let mut signals = signal_hook::iterator::Signals::new([
            signal_hook::consts::SIGTERM,
            signal_hook::consts::SIGINT,
        ])?;
        thread::spawn(move || {
            for _sig in &mut signals {
                stop.store(true, Ordering::Relaxed);
            }
        });
    }
    #[cfg(windows)]
    {
        ctrlc::set_handler(move || {
            stop.store(true, Ordering::Relaxed);
        })?;
    }
    Ok(())
}
