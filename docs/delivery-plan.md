# Delivery plan

The target is a working limit-order prediction market suitable for presentation.

1. **Console Wallet gateway in the shared Outcomia UI:** landing page, verified party/network connection,
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

## Current status

The shared wallet gateway, binary lifecycle and [approved asset transfers](collateral-transfers.md)
are locally tested. Collateral support includes dedicated-vault asset balances
and [complete-set split/merge](complete-set-positions.md). [Resting orders](binary-limit-orders.md)
add funded placement and cancellation. The [matching planner](binary-matching.md) defines selection, partial fills,
maker-price execution and cancel-newer self-trade behavior. [Atomic settlement](binary-settlement.md) now applies one fill or self-trade
cancellation, with signed-order delegation and actual token transfers. The [fee rules](fee-accounting.md) are documented; fee contracts, resolution
and redemption remain. No public Canton deployment
or wallet-to-ledger market commands are implemented yet. See the [lifecycle design](binary-market-lifecycle.md).

The chosen [collateral custody model](collateral-custody.md) uses a dedicated
vault party with explicit signer trust. Its public-network hosting is not configured.

## Checkpoint 1 boundary

In the original Outcomia app, the wallet selects Solana markets or the Canton
prediction workspace. Loop or Console Wallet verifies its primary party and network.
This repository owns Canton contracts and services; it does not host a second UI. No deployed market contracts or order settlement are
claimed by this checkpoint. An unconfigured market deployment is shown explicitly.

## Matching and settlement boundary

The bounded order index commits acceptance sequence and price. The pure planner
selects best-price/FIFO and requests cancellation of the newer
self-crossing order. Fees are zero at this stage. Settlement recomputes the plan from verified contracts and updates partial
orders and backing atomically. The operator triggers one fill per command.
See the [order design](binary-limit-orders.md).
Keep wallet identity independent of these contracts so account changes cannot
reuse a previous party's commands.

## Clubs/private-market status

[Clubs and private markets](clubs-private-markets.md) are planned, not implemented.
The current contracts have no club membership or invitation gate. Existing
matching and account-registry disclosure must be redesigned before promising
private club activity. Member removal must preserve safe exits. The roadmap
sequence remains fees, resolution/redemption, multi-outcome, clubs, then governance.
