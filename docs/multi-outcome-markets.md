# Multi-outcome markets on Canton

Status: **plan (2026-11-26)**. Nothing here is implemented yet. It brings
Canton to parity with Solana's multi-outcome markets
(kunal171/outcomia `docs/multi-outcome-markets.md`), changed only where
Canton's ledger model requires it. Each milestone ships as a contracts PR in
this repository plus the matching UI PR in the shared app.

## Rules carried over from Solana

| Rule | Canton |
| --- | --- |
| 2–8 named outcomes, exactly one winner | Outcome IDs are zero-based list indices, fixed with the terms. |
| Invalid is a result, not a tradable asset | It refunds an equal share to every outcome. |
| Complete sets | Locking Q collateral units mints Q contracts of every outcome; merging Q of every outcome returns Q units. A winning contract pays 1 unit. |
| Exact invalid refunds | Each contract refunds `1/N`. Every quantity must be a multiple of the lot `L`, and `L/N` must be exact at the asset's precision: `L × 10^d` divisible by `N`. Checked at creation; split, merge, matching and redemption keep the lot. |
| Independent books per outcome | Buy and sell priority and FIFO per outcome. |
| Full-set matching | Buys of every outcome mint sets when their prices sum to at most 1; sells of every outcome merge sets when their prices sum to at least 1. |
| Resolution | Same creator/admin, review delay, correction and fallback model as binary, choosing a winning outcome or invalid. |
| Exits | Cancel, withdraw, merge and redeem never need membership or an open market. |

## Design

**Separate templates, binary untouched.** A new `Outcomia.MultiOutcome`
module holds the market, reserve, lots, book, orders and fills. Binary
contracts, types and their tests do not change. A shared resolution schedule
(close time, earliest resolution, fallback, review delay) is extracted so
both market kinds use one implementation of the resolution windows.

| Template | Role |
| --- | --- |
| `MultiMarket` | Terms (question, outcome labels and criteria, invalid criteria, rules document, collateral, tick, lot, schedule), status, factory scope and access. |
| `MultiReserve` / `MultiSettledReserve` | Complete-set backing; after resolution, the payout source for redemption. |
| `MultiLot` | A holder's contracts: one count per outcome. |
| `MultiProposal` / `MultiFinal` | Winner or invalid, with evidence, corrections and finalization. |
| `MultiBook` / `MultiOrder` / `MultiFill` | One bounded book per market holding every outcome's orders, the fee pool (including the club fee share) and fill receipts. |

**Creation through the market factory.** The factory standard already carries
a list of outcomes. Two outcomes keep creating binary markets; three to eight
create multi-outcome markets, for public and club factories alike, so club
policies, eligibility and club fees apply unchanged.

**Bounded books.** As on binary Canton books, one market's orders live in one
book (at most 128 references), not in linked ladders. Matching is driven by
the operator service, which proposes fills and the ledger revalidates.

## Milestones

| Milestone | Contracts | UI (same milestone) |
| --- | --- | --- |
| MO1 — Markets and custody | Terms and validation, factory creation (public and club), open, close, cancel draft, split and merge, lots, resolution (winner or invalid), settlement and redemption | Create form with 2–8 outcomes, market page, split and merge, propose, correct and finalize, redeem |
| MO2 — Order book | Place and cancel per outcome with fee quotes and eligibility, same-outcome matching, fee pool and club share, departed-order clearing | Trade ticket per outcome, book view, operator match, order list |
| MO3 — Full-set matching | Mint and merge across all outcomes, with partial fills and fees | Implied prices, operator "match full set" |
| MO4 — History | Indexer support for multi-outcome fills and resolution | Charts and activity |

## Open questions

- Payout per contract is one collateral unit, as for binary Canton markets.
  Solana allows a configurable face payout; Canton can add it later.
- Book capacity (128 orders) is shared by all outcomes of a market. A busy
  8-outcome market may need a larger bound, at the cost of bigger contracts.
