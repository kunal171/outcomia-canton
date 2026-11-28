# Trading

Binary markets trade through one bounded `OrderBook` per market. The operator
submits matches; traders sign placement once and never approve each fill.
Multi-outcome books follow the same rules (see [multi-outcome](multi-outcome-markets.md)).

## Orders

`OrderRegistry` creates one book per market (at most 1,024 books). Each book holds
at most 128 active references across both outcomes and sides, and gives every
accepted order an increasing ID.

- **Placing:** needs an Open market before cutoff, a price strictly between 0 and
  1 on the tick, and a whole-lot quantity. Restricted markets also need an
  eligibility proof (see [clubs](clubs.md)).
- **Funding a buy:** the price × quantity plus the maximum fee budget is locked in
  a vault holding. For example, 3 YES at 0.40 with a 25 bps fee locks 1.203.
- **Funding a sell:** 1–16 lots are consumed. The sold contracts are held in the
  order; the rest return as one lot.
- **Cancelling:** owner only, through the current book. It needs no market,
  protocol or admission, so it works after cutoff, closure and revocation.
- **Fee quote:** each order checks the live protocol ID, fee revision, rate and
  asset precision at placement, and keeps that snapshot for its lifetime.

Crossed orders can rest until the operator matches them. Ticks and amounts use
exact Decimal and integer arithmetic; nothing uses floats or rounded division.

## Matching

**Direct.** `OrderBook_MatchBest` fills the best YES (or NO) buy against the best
sell of that outcome:
- **Priority:** highest buy or lowest sell, then the lowest order ID.
- **Price:** the older order is the maker, and the fill executes at its price.

For a buy of 5 at 0.60 against an older sell of 3 at 0.40, the buyer gets 3
contracts, the seller 1.20, and the buyer 0.60 back as price improvement; 2
contracts at 0.60 stay on the book.

**Complementary.** `OrderBook_MatchComplement` trades the two outcomes' heads on
the same side through the complete set, as on Solana:

| Pair | Crosses when | Effect per contract |
| --- | --- | --- |
| YES buy at `y` and NO buy at `n` | `y + n ≥ 1` | Mint: 1 unit enters the reserve, and one YES and one NO are created |
| YES sell at `y` and NO sell at `n` | `y + n ≤ 1` | Merge: one YES and one NO burn, and 1 unit leaves the reserve |

- **Prices:** the maker trades at its price `q` and the taker at `1 − q`, which is
  never worse than its limit.
- **Route choice:** when a head can trade both ways, the operator service picks the
  route that gives the taker the better price, preferring direct on ties.

**Rules for both routes:**
- **Self-trades:** if both heads have the same owner, the newer order is cancelled
  and its backing returned.
- **Atomic, one pair per call:** each call fills one pair and returns the successor
  book, and everything in it commits together.

## Settlement

The caller supplies no price or quantity. In one transaction the settlement:

1. fetches the Open market, the book and every indexed order, and checks their
   terms, owners, assets, vault and exact escrow;
2. recomputes priority and amounts;
3. credits the seller, collects the fee, refunds the buyer and delivers the lot;
4. recreates partial orders with their original IDs and commits the new book and a
   `TradeFill` (or `ComplementFill`) receipt.

**Authority comes from nested choices.** The book supplies the operator and vault,
the signed buy supplies its owner, and the signed sell supplies its owner. So the
operator can settle without fresh trader signatures, but no single party can call
the inner choices.

**Any failure rolls back everything**, including a seller credit made before a
failed buyer refund. Receipts are audit records, not collateral.

## Fees

- **Who pays:** the operator sets `takerFeeBps` (0–1,000), and every change bumps
  `feeRevision`. Only the taker of an executed fill pays, at its own snapshotted
  rate; makers pay nothing. Placement, cancellation, split/merge, resolution and
  redemption are free.
- **Rounding:** fees round down to the asset unit `u = 10^-d`. Books require
  `priceTick × lot` to be a multiple of `u`.

  ```text
  F(n) = floor((n × rateBps / 10,000) / u) × u
  fee for a fill = F(previous taker notional + this fill) − fee already paid
  ```

  Orders track cumulative taker notional and fees paid, so partial fills don't
  restart the rounding. Buys reserve the future cumulative fee, not a fresh
  estimate. A tiny sell can lose its whole proceeds to the fee; settlement then
  skips the zero transfer.
- **Fee pool:** earned fees go into one backed holding per book (`OrderBook.fees`),
  in the same transaction as the fill. `OrderBook_WithdrawFees` pays only the
  operator.
- **Club share:** books of club markets reserve `clubShareBps` (at most 5,000) of
  each fee as `clubFees`. The operator can withdraw only the rest, and the club
  owner withdraws the club's part with `Club_WithdrawFees`.

At 25 bps with 6 decimals, a buy of 5 at 0.60 that takes 3 at 0.40 moves:

| Cash | Amount |
| --- | ---: |
| Initial escrow | 3.0075 |
| Seller | 1.20 |
| Fee | 0.003 |
| Buyer refund | 0.6015 |
| Remaining escrow | 1.203 |

An independent Python reference checks 4,400 buy lifecycles and 57,510 fill
invariants. `python3 scripts/generate-fee-vectors.py --check` verifies the 308
checked-in fee vectors that the Daml arithmetic tests use.

## Limits

- **One book per market:** placing, cancelling, matching and fee withdrawal all
  serialize on it, and stale requests must reload.
- **Single fills:** each call settles one pair; there are no batch fills.
- **Liveness:** the operator matcher is a liveness dependency. A wallet alone cannot
  trigger fills.
- **No per-order privacy:** settlement doesn't hide orders from the other matched
  party.
