# Multi-outcome markets on Canton

Status: **MO1 merged (2026-11-26); MO2 built (2026-11-27)**, contracts and UI; MO3–MO4 pending
(see [Progress](#progress)). It brings
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
a list of outcomes. Exactly `YES, NO` keeps creating binary markets (`NO, YES`
is rejected); any other list of 2 to 8 labels creates a multi-outcome market,
for public and club factories alike, so club policies and eligibility apply
unchanged. Multi-outcome markets exist only in factory scope, so the issuing
factory's current admins close, propose and correct them; there is no draft
state and no fallback resolver.

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

## Progress

**MO1 contracts — done** (branch `feat/multi-outcome-mo1`, 238 tests pass).

- `contracts/main/daml/Outcomia/MultiOutcome.daml`: `MultiTerms`,
  `MultiResult = Winner Int | InvalidResult`, `multiTermsErrors`,
  `refundAligned` (`L × 10^d` divisible by `N`, computed modulo `N`),
  `multiPayout`; templates `MultiMarket` (`Multi_Close`, `Multi_Propose`),
  `MultiProposal` (`MultiProposal_Correct`, `MultiProposal_Finalize`),
  `MultiFinal`, `MultiLot { counts }`, `MultiReserve` (`MultiReserve_Split`,
  `MultiReserve_Merge`, `MultiReserve_BindResolution`) and
  `MultiSettledReserve` (`MultiSettled_Redeem`).
- `Factory.daml`: `maxOutcomes = 8`; `createBundle` routes to `createBinary`
  or `createMulti`. Multi markets get a market and reserve; the book comes in MO2.
- `contracts/test/daml/Outcomia/MultiOutcomeTest.daml`: routing, exact refunds,
  split/merge, admin resolution with corrections, close, winner and invalid
  payouts.

**MO1 UI — done** (outcomia-solana branch `feat/canton-multi-outcome-mo1`).

- `app/lib/canton/model.ts`: the six `Multi*` templates, `finalRecord`,
  `multiResult`, decoding checks. `transport.ts` reads the wallet's `MultiLot`s.
- `app/lib/canton/commands.ts`: `multiSplit`, `multiMerge`, `multiRedeem`,
  `multiClose`, `multiPropose`, `multiCorrect`, `multiFinalize`, `multiBind`;
  `standardTerms` accepts 2–8 unique labels. `server.ts` allows registry
  context for split, merge and redeem.
- `app/lib/canton/multi.ts`: `lotTotals`, `multiClaim`, `parseOutcomes`.
- `app/components/canton/multi-market.tsx`: outcomes with holdings, mint and
  return complete sets, claim, close, propose/correct, finalize, prepare claims,
  rules. The create form (`manage.tsx`) has a YES/NO or multiple-outcomes switch
  (one `Label: criterion` per line).
- `app/scripts/canton-multi.test.mjs` (5 tests, part of `npm run test:canton`).

**MO2 contracts — done** (branch `feat/multi-outcome-mo2`, 244 tests pass).

- `contracts/main/daml/Outcomia/MultiOrders.daml`: `MultiBook` (place buy/sell
  per outcome with fee quotes and eligibility, `MatchBest`, `Cancel`,
  `CancelIneligible`, fee withdrawal, club share), `MultiOrder` (settlement via
  buy→sell delegation, self-trade cancellation, release), `MultiTradeFill`,
  pure `planMultiFill`. Orders carry `outcomeCount` so released contracts form
  a full-width lot.
- `createMulti` now also creates the book; `Club_WithdrawMultiFees` pays the
  club owner from multi books.
- `MultiOrdersTest.daml`: per-outcome fills with price improvement, taker fee
  and club share, self-cross cancellation, cancel after close, planner heads.

**MO2 UI — done** (outcomia-solana branch `feat/canton-multi-outcome-mo2`):
commands `multiBuy`, `multiSell`, `multiCancel`, `multiClearDeparted`,
`multiMatch`, `multiWithdrawFees`, `multiSetShare`, `clubWithdrawMultiFees`;
catalog quotes include multi orders; market page shows the book, an order
ticket, your orders, and operator match/clear/fees; club screens include multi
books.

**Next steps**

1. MO3 full-set matching: mint when the best buys of every outcome sum to at
   most 1, merge when the best sells sum to at least 1 (a multi-leg version of
   `OrderBook_MatchComplement`), with fees and partial fills; UI implied prices
   and an operator "match full set" action.
2. MO4 indexer history (`MultiTradeFill`, resolution) and charts.
3. Not covered yet: a club test for `Club_WithdrawMultiFees`; multi lots on the
   Positions page.
