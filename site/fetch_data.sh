#!/usr/bin/env bash
# Write site/data/issues.json for the plan page: tickets, pull requests and milestones of the repository,
# read with the GitHub CLI. Run by .github/workflows/pages.yml; locally it needs `gh` (logged in) and `jq`.
set -euo pipefail
repo="${GITHUB_REPOSITORY:-fedro86/DECADE}"
out="$(dirname "$0")/data/issues.json"
mkdir -p "$(dirname "$out")"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
gh api --paginate "repos/$repo/issues?state=all&per_page=100" | jq -s 'add | map({
  number, title, state, closed_at, body,
  labels: [.labels[].name],
  milestone: (if .milestone then {title: .milestone.title, due_on: .milestone.due_on} else null end),
  pr: (.pull_request != null), draft: (.draft // false), merged_at: (.pull_request.merged_at // null)})' > "$tmp/issues.json"
gh api "repos/$repo/milestones?state=all&per_page=100" | jq 'map({number, title, description, due_on, state})' > "$tmp/milestones.json"
jq -n --arg repo "$repo" --arg t "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --slurpfile i "$tmp/issues.json" --slurpfile m "$tmp/milestones.json" \
  '{repo: $repo, generated_at: $t, issues: $i[0], milestones: $m[0]}' > "$out"
echo "wrote $out: $(jq '.issues | length' "$out") issues and pull requests, $(jq '.milestones | length' "$out") milestones"
