# Multi-outcome markets

Markets with 2–8 named outcomes and exactly one winner, at parity with Solana
(outcomia `docs/multi-outcome-markets.md`). They are created only through a market
factory (public or club), so the factory's admins resolve them. They have no draft
state and no fallback resolver. Binary contracts are untouched.

## Rules

| Rule | Canton |
| --- | --- |
| Outcomes | IDs are zero-based list indexes, fixed with the terms |
| Complete sets | Locking `Q` units mints `Q` of every outcome; merging `Q` of every outcome returns `Q`; a winning contract pays 1 unit |
| Invalid | A result, not a tradable asset: every contract refunds `1/N`. Each quantity is a multiple of the lot `L`, and `L × 10^d` must be divisible by `N`, checked at creation. |
| Books | One bounded `MultiBook` per market (128 references shared by all outcomes), with per-outcome price-time priority, the fee pool and the club share |
| Exits | Cancel, withdraw, merge and redeem never need membership or an open market |

## Templates

| Template | Role |
| --- | --- |
| `MultiMarket` | Terms, status, factory scope and access |
| `MultiReserve` → `MultiSettledReserve` | Complete-set backing, then the redemption source |
| `MultiLot` | A holder's count per outcome |
| `MultiProposal` → `MultiFinal` | Winner or invalid, with evidence, corrections and finalization; `winnerIndex` mirrors the result for indexers |
| `MultiBook`, `MultiOrder` | Per-outcome orders, fee quotes, eligibility, matching and cancellation |
| `MultiTradeFill`, `MultiFullSetFill` | Fill receipts |

## Matching

- **Same outcome:** `MultiBook_MatchBest` works like binary direct matching.
- **Full set:** `MultiBook_MatchFullSet` takes the best order of every outcome on one
  side:
  - **Buys** mint sets when their limits sum to at least 1.
  - **Sells** merge sets when their limits sum to at most 1.
  - **Prices:** makers trade at their limits, and the taker (the newest order) at 1
    minus the makers' sum. If the makers' limits alone reach 1 on the buy side,
    nothing matches until the book changes.
  - **Authority:** each head's signed order passes its owner's authority to the next
    leg, so the last leg settles with every owner's authority.
  - **Self-trades:** an owner holding two heads has the newest cancelled
    (`MultiOrder_CancelFullSetSelfTrade`).

## Limits

- **Payout:** one collateral unit per contract. Solana's configurable face payout is
  not supported.
- **Book capacity:** 128 orders shared by all outcomes may be tight for busy
  8-outcome markets.
- **Indexing:** the indexer leaves out settled reserves, per-outcome lot counts and
  full-set legs, because of engine limits.
- **Charts:** the app shows activity from ledger receipts. Indexer-backed charts
  wait for remote-network support in CantonGrid.
