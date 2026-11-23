# Complementary binary matching

Direct matching ([binary matching](binary-matching.md)) fills YES buys against YES
sells and NO buys against NO sells. A YES buy at 0.60 and a NO buy at 0.40 never
trade, although together they fully fund a new YES+NO pair. Complementary
matching lets orders on the **same side of the two outcomes** trade through the
complete set, so both books share liquidity. It brings Canton in line with the
Solana program ([Solana rules](https://github.com/kunal171/outcomia/blob/master/docs/complementary-matching.md)).

This is locally tested, not deployed on public Canton. Canton trading stays
disabled in the shared UI until deployment and a wallet smoke test pass.

## Rules

Each contract pays 1 collateral unit, so a complete set costs 1.

| Pair (best of each queue) | Crosses when | Effect per contract |
| --- | --- | --- |
| YES buy at `y` and NO buy at `n` | `y + n >= 1` | **Mint**: 1 unit enters the market reserve; one YES and one NO are created |
| YES sell at `y` and NO sell at `n` | `y + n <= 1` | **Merge**: one YES and one NO burn; 1 unit leaves the reserve |

- **Maker and taker:** as in direct matching, the order with the lower
  acceptance ID is the maker. It trades at its own price `q`. The taker trades
  at `1 − q`, which is never worse than its limit.
- **Fees:** the taker fee applies to the taker's notional `(1 − q) × n`, using
  that order's snapshotted rate, and accrues to the book's fee pool. Makers pay
  no fee.
- **Priority:** each order must be the best-price/FIFO head of its own queue.
  The operator cannot pick a deeper order. Price-time priority inside each
  queue is unchanged.
- **Direct or complementary:** when a head can trade both ways, the operator
  service chooses. Both routes execute within both limits. The service should
  prefer the route that gives the taker the better price and direct liquidity
  on ties, the same rule the Solana client applies. The contracts do not rank
  routes against each other.
- **Self-trade:** if both heads have the same owner, the newer one is cancelled
  and its backing restored, as in direct matching.
- **Lifecycle and eligibility:** only while the market is Open and before
  cutoff. On restricted (club) markets both owners must still be eligible to
  fill.
- **Placement:** unchanged. Canton books may hold crossed resting orders until
  the operator matches them, for both routes.

## Transaction flow

`OrderBook_MatchComplement(market, reserve, side, yesBalance, noBalance)` is
operator-controlled and nonconsuming at the entry, like `OrderBook_MatchBest`.
It delegates through the signed orders so the inner body holds both owners'
authority:

```mermaid
sequenceDiagram
  participant Operator
  participant Book as Current OrderBook
  participant Yes as Signed YES order
  participant No as Signed NO order
  participant Reserve as MarketReserve
  Operator->>Book: MatchComplement(market, reserve, side, accounts)
  Book->>Yes: SettleComplementYes with selected NO order
  Yes->>No: SettleComplement with YES owner as controller
  No->>Book: Fetch full index; verify orders; recompute plan
  No->>Reserve: Mint: add 1 per pair from both escrows / Merge: release 1 per pair
  No->>No: Fees, refunds or proceeds; positions; partial successors
  No->>Book: Archive old book and reserve; create successors and a receipt
```

The settlement rebuilds the plan from the fetched book. The caller supplies no
price or quantity. The reserve must belong to the same market key, creator,
creation time and terms, and its holding must equal its complete-set count.

## Mint example

25 bps taker fee, 6-decimal asset. A NO buy rests at 0.40 × 5 (maker, older).
A YES buy at 0.65 × 3 arrives (taker). They cross (0.65 + 0.40 ≥ 1) and mint 3
pairs; the taker pays 1 − 0.40 = 0.60.

| State | Before | After |
| --- | ---: | ---: |
| YES buy escrow (taker) | 1.954875 | 0 (complete) |
| NO buy escrow (maker) | 2.005 | 0.802 (2 contracts remain) |
| Market reserve | R | R + 3.00 |
| Fee pool | F | F + 0.0045 |
| YES owner's available balance | baseline | + 0.150375 |
| NO owner's available balance | baseline | + 0.003 |
| YES owner's position | 0 | 3 YES |
| NO owner's position | 0 | 3 NO |

The taker's 1.954875 splits into 1.80 cost, 0.0045 fee and a 0.150375 refund
(0.15 price improvement plus unused fee budget). The maker's 2.005 splits into
1.20 cost, a 0.003 fee-budget release and 0.802 remaining escrow. 1.80 + 1.20
enter the reserve, so its backing still equals its complete-set count.

## Merge example

A YES sell rests at 0.45 × 4 (maker). A NO sell at 0.50 × 4 arrives (taker).
They cross (0.45 + 0.50 ≤ 1) and merge 4 pairs; the taker sells at 0.55.
4.00 leaves the reserve: 1.80 to the maker, 2.20 gross to the taker, of which
0.0055 is the fee and 2.1945 is credited. The escrowed YES and NO contracts
burn with the orders, so YES supply, NO supply and the reserve fall by 4.

## Invariants

- **Reserve:** backing = complete sets, before and after every fill.
- **Escrow:** each buy's old escrow = cost + fee + refund + remaining escrow,
  using the existing fee helpers.
- **Supply:** a mint adds `n` YES, `n` NO and `n` complete sets; a merge removes
  the same three amounts.
- **Atomicity:** every transfer, position, order and book change happens in one
  transaction; any failure rolls back all of them.

## Records

Each fill creates a `ComplementFill` receipt (operator and vault signatories,
both owners observe) with the plan, fee and refunds. Like `TradeFill`, it is an
audit record and never spendable. The indexer needs a matching update before
Canton history shows complementary fills.
