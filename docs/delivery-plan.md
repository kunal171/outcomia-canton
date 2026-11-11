# Delivery plan

The target is a working limit-order prediction market suitable for presentation.

1. **Console Wallet gateway:** landing page, verified party/network connection,
   gated Canton workspace, disconnect/account-change handling and responsive UI.
2. **Binary market lifecycle:** creation, rules, deadlines, roles and opening.
3. **Collateral and positions:** funding, complete-set issuance/merge and withdrawals.
4. **Limit orders and settlement:** resting orders, cancellation, partial fills,
   price-time priority, fees and atomic asset conservation.
5. **Resolution and redemption:** authorized resolution, dispute/fallback rules
   and winning-position claims.
6. **Multi-outcome markets:** exactly one winner, complete-set collateral and
   outcome-specific books with the same settlement invariants.
7. **Clubs/private markets:** invitations, contract-level visibility and trade
   permissions; removal never prevents cancellation, withdrawal or redemption.
8. **Governance-created markets:** proposals, quorum, voting thresholds and
   authorized creation after approval.

Each numbered checkpoint may be split into smaller feature PRs. A checkpoint is
complete only when its working flow, failure checks and documentation are ready.
Do not start a new feature branch before closing the current checkpoint.

## Checkpoint 1 boundary

Connect Console Wallet, read its primary Canton party and network, and expose
only the Canton workspace. No deployed market contracts or order settlement are
claimed by this checkpoint. An unconfigured market deployment is shown explicitly.

## Settlement decisions to document before checkpoint 4

A backend proposing fills does not prove global price-time priority. Specify what
Daml checks, which orders the matcher can see, how sequencing is committed, and
how stale or competing fills fail. Keep the wallet adapter independent of these
contracts so account changes cannot reuse a previous party's commands.
