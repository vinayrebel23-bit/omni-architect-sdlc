/// Pure first-match table. Source of the rows: `orchestrator/main.py:78-87`.
/// A cache hit is not consulted. See `docs/ADR/0005-table-always-runs.md`.
pub fn route_swarm(task_intent: &str) -> &'static str {
    let intent = task_intent.to_ascii_lowercase();
    if intent.contains("refactor") || intent.contains("complexity") {
        "janitor"
    } else if intent.contains("500 error") || intent.contains("incident") {
        "sre"
    } else if intent.contains("cost") || intent.contains("aws") || intent.contains("terraform") {
        "finops"
    } else if intent.contains("conversion") || intent.contains("drop-off") {
        "growthops"
    } else {
        "general"
    }
}

#[cfg(test)]
mod tests {
    use super::route_swarm;

    #[test]
    fn first_match_wins_the_locked_rows() {
        assert_eq!(route_swarm("refactor the 500 error path"), "janitor");
        assert_eq!(route_swarm("complexity is 12"), "janitor");
        assert_eq!(route_swarm("500 error on login"), "sre");
        assert_eq!(route_swarm("incident in the api"), "sre");
        assert_eq!(route_swarm("aws cost rose"), "finops");
        assert_eq!(route_swarm("terraform plan"), "finops");
        assert_eq!(route_swarm("conversion drop-off on checkout"), "growthops");
        assert_eq!(route_swarm("fix mobile login"), "general");
    }
}
