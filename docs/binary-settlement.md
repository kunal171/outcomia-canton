# Atomic binary settlement

`OrderBook_MatchBest` executes one same-outcome fill, or cancels the newer order
in a self-cross. The operator submits the command. Traders sign placement once;
they do not need to approve each later fill of that resting order.

This is locally tested, not deployed on public Canton. There is no live matcher
service or verified wallet-to-ledger market submission yet. Canton trading stays
disabled in the shared UI.

## Transaction flow

```mermaid
sequenceDiagram
  participant Operator
  participant Book as Current OrderBook
  participant Buy as Signed buy order
  participant Sell as Signed sell order
  participant Cash as Token holdings and balances
  Operator->>Book: MatchBest(market, outcome, current accounts)
  Book->>Buy: SettleBuy with selected sell
  Buy->>Sell: SettleSell with actual buyer as controller
  Sell->>Book: Fetch full index; verify orders; recompute plan
  Sell->>Cash: Credit seller; refund buyer's improvement
  Sell->>Sell: Deliver buyer's outcome lot; recreate partial orders
  Sell->>Buy: Archive old buy
  Sell->>Book: Archive old book; create successor references
  Note over Sell: Old sell is consumed when its choice finishes
  Sell-->>Operator: Successor IDs and fill receipt through nested calls
```

The market must be Open and ledger effective time strictly before cutoff. The
book must match its original market ID, creator, creation time and immutable
terms. Every indexed contract is fetched and checked against its reference,
market, vault, asset and factory. The planner then recomputes best-price/FIFO;
the caller cannot submit a price or fill quantity to override it.

The selected buy's actual holding must equal its limit price times remaining
quantity. Both accounts must belong to the correct traders and the same
operator, vault, asset, protocol and pinned factory.

## Cash and position changes

For a buy of 5 at 0.60 matching an older sell of 3 at 0.40:

| State | Before | After |
| --- | ---: | ---: |
| Buy escrow | 3.00 | 1.20 |
| Seller's available balance | unchanged baseline | baseline + 1.20 |
| Buyer's available balance | unchanged baseline | baseline + 0.60 |
| Remaining buy quantity | 5 | 2 |
| Remaining sell quantity | 3 | 0 |
| Buyer's delivered YES or NO | 0 | 3 |

The seller credit consumes the buy escrow and the seller account's old backing.
Its change still belongs to the buy. The buyer refund then consumes that change
and the buyer account's backing, leaving exactly the partial buy's limit escrow.
A zero refund leaves the buyer account ID unchanged and skips the zero transfer.
Empty accounts are supported. Fees remain zero.

The sell's escrowed outcome quantity is removed by consuming its order. Exactly
the filled quantity becomes the buyer's position lot. Any partial buy/sell keeps
its original price, owner, acceptance ID and timestamp; its contract ID changes.
Complete-set reserves and total YES/NO supply do not change.

If any registry transfer, exact-output check, account check or contract creation
fails, the entire transaction rolls back. This includes the case where the seller
credit has executed but the later buyer refund fails. No partial credit, delivered
position, receipt or revised book remains.

## Why the nested choices matter

Daml choices authorize their consequences using their controllers and the signed
contract. The book supplies operator/vault authority. The signed buy contributes
its owner; that actual buyer is an explicit controller of the nested sell. The
signed sell then contributes its owner. Both account credits and the buyer's new
position are therefore authorized within that one nested settlement body.

The book and buy entry choices are nonconsuming so the inner choice can fetch
their active contracts. The sell is postconsuming for the same reason. Its body
explicitly archives the old buy and book, and the old sell is consumed when the
body finishes. A successful call therefore invalidates all affected old IDs even
though the entry choices themselves say `nonconsuming`.

The internal buy choice needs both operator and vault. The internal sell also
needs the actual buyer; substituting another party fails against the fetched buy.
An ordinary trader, the operator alone, or the vault alone cannot invoke these
internal choices directly. The normal operator-only book command obtains the
necessary authority from the signed contracts, without fresh trader signatures.
See [Daml choice composition](https://docs.digitalasset.com/build/3.4/tutorials/smart-contracts/compose.html).

The dedicated vault remains trusted custody. This does not remove the signing
trust documented in [the custody model](collateral-custody.md), or prove a root's
authenticity from its protocol name. Services must pin the configured lineage.

## Self-trades and exits

When the best crossing pair has one owner, cancel only its newer order. Both
account parameters must reference that owner's same current account. A buy gets
all remaining escrow back; a sell gets its remaining outcome contracts back.
There is no fill receipt and no transfer to another trader. The older order and
acceptance counter remain unchanged. Matching can resume from the successor book.

Automated self-trade cancellation uses the same Open/cutoff gate as matching.
Owner cancellation remains available after cutoff or administrative closure.
Revoked admission does not block a resting fill through its saved factory; close
the market to stop trading. Registry freezes or retirement can still prevent cash
movement. A full book or exhausted acceptance counter does not block settlement.

## Returned state and records

For a fill, `SettlementResult.balances` contains the buyer then seller account
IDs. `position` is the buyer's delivered lot; `receipt` is a `TradeFill` contract.
The decision contains the executed plan, and `book` contains the successor index.
Use that index for any partial-order contract IDs. For self-trade cancellation,
`balances` contains one owner account, `position` is any returned sell lot, and
`receipt` is absent. Always use returned IDs rather than replaying old inputs.

A `TradeFill` is an operator/vault-signed audit record visible to buyer and seller.
It is not collateral, a deposit credit or a redeemable outcome. Its contract ID
identifies the fill; multiple partial fills may share order IDs. Indexers must
retain ledger history if the signers later archive the receipt.

## Limits and remaining work

Each call verifies at most 128 references and executes one pair. It does not batch
fills. One market book serializes matching, placement and cancellation. Concurrent
requests may conflict and must reload/recompute, preserving command deduplication
when a submission outcome is uncertain. The operator matcher is a liveness
dependency; a wallet connection alone does not run it.

Matched traders see the nested settlement transaction, including the fetched
book/order data. This version does not promise per-order privacy from other
matching participants. Private clubs will need an explicit disclosure design.

Public-network deployment, actual registry compatibility, read/submission
services, fees, cross-outcome matching, resolution and redemption remain separate
milestones. Only the production DAR is deployable; the test DAR includes the
fault-injecting registry and `daml-script`.

## Verification

`make DPM="$PWD/target/tools/dpm" test` passes 96 Daml scripts, including 20
settlement scripts, plus four Python dependency checks. Production DAR validation
passes with 38 packages.

The settlement scripts reconcile actual cash holdings, free accounts, buy
escrows, reserve backing and both outcome supplies. They cover maker direction,
partial and full fills, refunds into empty accounts, FIFO continuation, cancelled
remainders, owner/keeper authorization, stale inputs, foreign markets, incorrect
escrow, altered references and rollback at both registry-credit stages. A genuinely
funded 128-order book still matches; an exhausted acceptance counter does not
freeze existing fills. Self-trade cancellation, closure/cutoff exits and fills
through the pinned factory after admission revocation are also checked.

These are IDE-ledger tests against the pinned Token Standard interface and a
fault-injecting registry. They do not establish public-network throughput,
provider compatibility, wallet submission or deployment readiness.
