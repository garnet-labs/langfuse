# Pull request review

The approval engine and advisory merge gate are vendored from the PostHog fork
at commit `aee1db69f6a10196dacd03f15721cf6e4df6b072`. The engine is unchanged
except for the CODEOWNERS format registration and its small adapter.

Ownership comes from `.github/CODEOWNERS` on the trusted base branch. Missing,
empty or unsupported configuration stops review rather than inventing an owner.
Unmatched paths have no ownership assurance. The pinned source has no
`tools/owners` package; its PostHog resolver is not enabled here.
The adapter supports the active individual-owner rules in this repository.
Team handles, email owners and unsupported pattern syntax stop review; they
cannot fall through to the engine's PostHog-specific team-membership checks.

Apply `stamphog` to opt a ready, same-repository pull request into review. The
workflow reruns when the runtime record arrives. Bot authors remain subject to
the canonical engine's human-review rule; `agent` and `dependency` describe the
change, not permission to bypass review. No branch-protection settings change.

The recorder runs cold `pnpm install --no-frozen-lockfile` using the repository's
Node and package-manager pins, and `cargo fetch --locked && cargo build --locked`
in `ai-gateway` and `packages/native`. Cargo uses each crate's own toolchain.
Repository build-script restrictions stay intact. Installs/builds, not the full
application suite, are the measured workloads; databases, browser workloads,
Docker publishing and application integration runs are omitted. Agent code
changes receive this same limited dependency workload, not proof of their
application-level behavior.

Dependency proof only attests supported manifest paths after all three jobs
succeed and the current-head record declares complete capture and no new
behavior against the exact PR base. Missing, stale, incomplete, best-effort or
first-run evidence attests nothing. Evidence may lift only `deps_toolchain` into
review, never clear auth, migrations, billing, public API or policy edits.

Recording uses tokenless OIDC: each recorded job requests `contents: read` and
`id-token: write`, with no API-token input. Approval review references the existing
organization-level `ANTHROPIC_API_KEY` (or `STAMPHOG_ANTHROPIC_API_KEY`); no
repository secrets are added. Publishing, evidence status and the advisory gate
use the automatic repository token. Policy and engine edits require human review.
