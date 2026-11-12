# Trading-fee rules

The [pure arithmetic helpers](../contracts/main/daml/Outcomia/Fees.daml) are
implemented and locally tested. The protocol now controls the rate, and orders
store approved fee snapshots. Actual fee funding/collection is not integrated:
placement accepts only zero-rate orders and settlement still charges zero.
No public Canton trading is enabled by this work.

## Who pays

- Only an executed trade earns a protocol fee. Placement, cancellation,
  self-trade prevention, deposits, withdrawals, split/merge and reward claims do
  not earn trading fees. Canton network charges are separate.
- The lower acceptance ID is maker; the newer order is taker. Maker fee is zero,
  with no rebates. An order can be maker in one fill and taker in another.
- The taker pays in the market's collateral asset, on execution price times
  filled quantity. Do not calculate fees on the full remaining order or payout.
- The protocol operator controls the default rate: initially 0, with a prototype
  range of 0–1,000 basis points. One basis point is 0.01%; 25 bps is 0.25%.
  An ordinary market creator or future club admin cannot change this rate.
- Each order snapshots the active rate at placement. The taker's own snapshot
  determines its charge. Updates affect new orders only. Placement must verify
  the policy revision/rate in the signed quote; a stale quote fails for review.

## Asset precision and rounding

The asset's vetted configuration must specify its settlement precision `d`, from
0 to 10 decimal places. Its smallest transferable unit is `u = 10^-d`. Neither
a ticker nor wallet-display metadata is proof of registry precision. Verify the
configuration against the selected registry before admitting it.

Deposits, withdrawals and transfers must respect that unit. Require
`priceTick × quantityLot` to be a multiple of `u`; every valid price times valid
whole-contract quantity can then settle exactly. A fractional contract price is
possible even for a whole-unit asset if its lot makes the cash amount integral.
An unsupported precision or registry fee model is rejected, not silently rounded.

Round protocol fees **down** to `u`, in the trader's favor:

```text
F(n) = floor((n × rateBps / 10,000) / u) × u
```

An order stores cumulative taker notional `T`. A taker fill with gross value `g`
charges `F(T + g) − F(T)` and advances `T`. A maker fill charges zero and leaves
`T` unchanged. Partial successors preserve this accumulator and the original
rate; they must not restart rounding. Recorded paid fees must equal `F(T)`.

This makes the total independent of how a given taker execution is split into
fills. For a six-decimal asset at 25 bps, two taker fills of 0.0002 charge 0 then
0.000001, the same total as one fill of 0.0004. A later fill can catch up earlier
rounding, but cannot charge more than that fill's quantum-aligned gross proceeds
at these rates. Seller net proceeds may be zero; zero transfers must be skipped.

Separate orders reset their own accumulators. The protocol can therefore collect
less than one smallest unit below the exact fee per order, including a cancelled
partial order. Tiny-order splitting can exploit that bounded undercollection.
This is a deliberate rounding tradeoff, not a claim of split-proof economics;
minimum-notional/lot policy is separate work before public nonzero-fee trading.
There is no hidden minimum fee or upward rounding on cancellation.

## Buy funding

A buy reserves its limit notional plus the maximum remaining taker fee under its
snapshot. Reserving trade cost alone would let a later fill need money that the
trader has already withdrawn or used in another market.

For limit price `L`, remaining quantity `Q`, cumulative taker notional `T`:

```text
feeReserve(T, Q) = F(T + L × Q) − F(T)
buyEscrow       = L × Q + feeReserve(T, Q)
```

At placement `T = 0`. The check and transfer of the entire escrow must commit
with the order and book update. Insufficient free collateral rejects placement.
The reserve is user-owned escrow, not earned protocol revenue.

After filling `q` at `P`, set `Q' = Q − q` and update `T` only if this buy is taker:

```text
feeThisFill     = F(T') − F(T)
newFeeReserve   = F(T' + L × Q') − F(T')
releasedBudget = oldFeeReserve − feeThisFill − newFeeReserve
buyerRefund    = (L − P) × q + releasedBudget
newBuyEscrow   = L × Q' + newFeeReserve
```

Both refunds must be nonnegative. Reserve against the **cumulative** base, not
`F(L × Q')` alone: earlier fractional rounding can affect the next charge.
A maker buy also releases unused fee budget for its filled quantity, even though
its trading fee is zero. Therefore a maker fill can revise the buyer's free
account despite having no price improvement. At `Q' = 0`, no escrow remains.

Example: six-decimal collateral, 25 bps, buy 5 at 0.60 against an older sell of
3 at 0.40:

| Cash use | Amount |
| --- | ---: |
| Initial buy escrow | 3.0075 |
| Seller's gross proceeds | 1.20 |
| Earned buy-taker fee | 0.003 |
| Buyer refund: price improvement + unused fee budget | 0.6015 |
| Remaining buy escrow: 1.20 trade cost + 0.003 fee reserve | 1.203 |

The last four amounts sum to 3.0075. The refund is not just the 0.60 price
improvement: it also returns 0.0015 of unneeded fee budget.

## Sell funding

A sell locks only its outcome contracts. If it is taker, deduct its cumulative
fee delta from gross proceeds before crediting its free collateral balance:

```text
sellerNet = executionPrice × filledQuantity − sellerTakerFee
```

The buyer does not pay the seller's fee. A maker sell receives the full gross
amount. For example, a newer sell fills 3 contracts against an older buy at 0.60:
at 25 bps it receives 1.7955 and the protocol receives 0.0045 from the 1.80 gross.
The maker buy pays no fee and receives any released buy-fee reserve.

The fee delta must be between zero and gross proceeds. A negative net rejects
settlement. A zero net leaves the seller account unchanged instead of submitting
a zero transfer. No additional seller wallet funds may be debited.

## What the trader signs

The placement quote shows the policy revision, snapshotted rate, asset precision
and exact collateral amounts. For a buy, show the maximum total debit
`L × originalQuantity + F(L × originalQuantity)`, including its reserved fee.
It must not depend on a later wallet top-up.

For a sell, show gross and estimated net if fully filled at its limit. The fee
amount at the sell limit is an estimate, not a maximum: a better execution price
can increase both gross proceeds and the fee. A conservative whole-order fee
bound is `F(originalQuantity)`, because each contract executes below one
collateral unit. No cash is reserved by the sell, and a rounding catch-up can
leave one tiny fill with zero net. The cumulative order fee still never exceeds
the agreed rate times its cumulative taker notional.

## Collection, exits and authority

Use one backed fee pool per market, pinned to its market key, protocol, vault,
asset and exact factory. This avoids a global same-asset fee account serializing
otherwise independent markets. Each market already serializes on its book.
The live pool revision is verified inside settlement; a name alone cannot prove
its configured lineage. Zero-fee fills do not consume the pool unnecessarily.

Fees, seller net proceeds, buyer refunds, residual escrow, outcome delivery and
the new book/receipt must commit together. A later registry failure rolls back
the fee too. Do not accumulate a numeric credit without an actual disjoint holding.

```text
vault cash = available trader cash
           + complete-set reserve backing
           + buy escrow (trade cost + unearned fee reserve)
           + earned protocol fee pools
```

Buy cancellation, including automated self-trade prevention, refunds its entire
remaining trade-and-fee escrow. Sell cancellation returns only its remaining
outcome contracts. Fees already earned on earlier fills remain earned. Cancelling
an order and replacing it creates a new ID, priority and fee snapshot; a partial
fill does not. A later invalid-market outcome does not automatically reverse
executed trading fees. Any rebate would need a separate funded policy.

Only the protocol operator may withdraw earned fees. The initial destination is
the operator's own wallet; the vault-signed pool supplies vault authority. A
future different recipient needs explicit recipient authorization under the token
adapter, not an arbitrary destination argument. Withdrawals must use exact
transfers and canonical change, consume the current pool and respect its asset.
They cannot access user balances, order escrows or outcome reserve backing.
These are contract-choice rules, not protection from the raw vault signer, which
remains trusted as described in [custody](collateral-custody.md).
Market closure does not delete a nonempty pool; terminal cleanup must retain it
or empty it through an authorized withdrawal.

## Implementation sequence

1. **Done:** precision-aware cumulative fee helpers and exact arithmetic tests.
2. **Done:** operator policy, vetted book precision and immutable order snapshots.
3. **Prepared, zero rates only:** signed fee history and helper-based buy funding,
   refunds and cancellation. Nonzero activation waits for steps 4 and 5.
4. Collect one taker fee into a market pool within atomic settlement.
5. Add authorized fee withdrawal and conservation/rollback tests.
6. Show the rate, reserve, maximum debit and refund in the shared UI only when
   deployment, registry compatibility and submission are verified.

During this staged rollout, accept only zero-rate orders until the snapshot,
full buy reserve, fee collection and cancellation paths are integrated together.
Adding a configurable policy or snapshot field alone must not enable a nonzero-
fee order backed only by the old trade-cost escrow. Keep public trading gated.

Signed order state now includes original/remaining quantity, snapshotted rate and
precision, cumulative taker notional and paid fee. Reject inconsistent paid-fee
or reserve values, negative quantities and arithmetic overflow. The original
quantity bounds accumulated notional, including when maker and taker fills mix.

Do not first divide in `Decimal` and then round: `Decimal` has only ten fractional
digits and could lose the fraction being accounted for. The implemented helper
widens the bounded order notional to `Numeric 14` before multiplying by basis
points and dividing by 10,000. Four extra fractional digits make that ratio exact.
Round to asset precision by separating whole and fractional units; do not scale
an entire large notional into Int64 smallest units. That can overflow.
See [Daml numeric types](https://archived.docs.digitalasset.com/build/3.5/reference/daml/stdlib/Prelude.html).

Run `python3 scripts/check-fee-policy.py` for the exact-rational reference check.
It exercises 4,400 buy-order lifecycles and 57,510 buy/sell fill checks, mixed
maker/taker fills, asset precisions 0–10 and rates 0/1/25/1,000 bps. It checks
nonnegative reserve release, cash conservation, bounded seller deductions and
maximum-Int intermediate bounds. This checks the design equations; it is not a
Daml implementation, registry test or public-deployment result.

## Implemented arithmetic boundary

`FeeTerms` is a pure input record, not proof of a configured rate or registry
precision. Placement now binds it to the live protocol and pinned book precision.
`BuyFeeState` is reconstructed from the signed order's original/remaining quantity,
limit and cumulative history. Settlement binds it to actual backing.
Settlement must derive maker/taker role from verified acceptance IDs and bind
gross amounts to the actual fill. A caller-supplied role flag is not authority.
Settlement now uses `buyFunding`, `buyFillFunding` and `sellFillFunding`, but
explicitly rejects a nonzero fee movement until atomic collection is implemented.

The module validates rate/precision bounds, original and remaining quantities,
transferable cash, cumulative paid-fee consistency and bounded taker history.
Its outputs cover remaining buy funding, per-fill fee/refund breakdown, and sell
net proceeds. It rejects invalid maker-buy prices and handles a zero-net seller
fill without issuing any transfer. Only validated public functions are exported.

Fourteen arithmetic scripts, twelve policy scripts and six funding/history scripts
pass alongside existing contracts: 128 Daml scripts and four Python dependency
checks. The helper matches 308
checked-in expected fees generated from the independent exact-Fraction reference.
The Daml conservation grid covers 792 precision/rate/price/quantity/role cases.
Nonzero rates are tested in pure arithmetic only; this is not evidence of
nonzero-fee ledger settlement or fee withdrawals.

Regenerate expected vectors with `python3 scripts/generate-fee-vectors.py`;
`python3 scripts/generate-fee-vectors.py --check` verifies the tracked fixture.
Run `make DPM="$PWD/target/tools/dpm" test` for the Daml checks. Contract integration
must still test fee-backed escrow, fee-pool conservation and registry rollback.

## Implemented policy and quote boundary

The configured `Protocol` lineage carries `takerFeeBps` and `feeRevision`.
Bootstrap it with both fields zero. Only the operator can exercise
`Protocol_SetTakerFee`, with a rate from 0 through 1,000 bps. Every successful
update consumes the old protocol and increments the revision, including an
update to the same rate. Revision exhaustion rejects without changing state.
Admin and market-ID fields are preserved.

Placement supplies the live protocol ID, expected fee revision and expected
`FeeTerms`. The book checks operator/namespace and compares that quote against
the active rate and its own pinned precision before touching cash or positions.
A revoked ID, changed revision/rate/precision or another namespace rejects the
whole placement. The accepted order stores `feeTerms` and `feeRevision`; partial
successors preserve them. Matching and cancellation do not fetch current policy.
Existing zero-fee orders can therefore settle or exit after an operator raises
the rate, while new orders at that nonzero rate are blocked.

This reuses the existing protocol root rather than introducing a second global
configuration contract. The cost is that an admin update or market creation also
changes the protocol ID and requires clients to refresh it. Rate revisions alone
do not identify that full contract revision. Services must pin the configured
lineage, as they already do for creator authorization: an operator deliberately
creating a second root is outside the trust boundary.

`Protocol_ApproveAsset` now records vetted `assetDecimals` (0..10). Book creation
checks the admission against the reserve's operator, instrument and factory,
requires `priceTick × quantityLot` to align to that precision, and stores it.
Changing or archiving admission cannot reinterpret an existing book's units.
For example, a 0.001 tick with a one-contract lot is rejected for a two-decimal
asset. A 0.01 tick is accepted. Matching checks each order's precision against
the book. This does not yet add precision validation to deposits/withdrawals;
registry compatibility and exact output checks still govern those paths.

Both placement and the `LimitOrder` template enforce zero fees for now. Raising
the configured rate is a configuration test, not activation of fee trading.
Funding paths use the full helper result, whose fee reserve is zero under the
current gate. No fee pool or fee withdrawal exists yet.
The production contract schema changed locally; no public upgrade or migration
has been performed.

## Signed funding and execution history

`LimitOrder` stores `originalQuantity`, `takerNotional` and `paidFee` in addition
to its remaining quantity and fee terms. Placement initializes history to zero.
Partial successors preserve original quantity and acceptance ID. Only a verified
taker fill increases that order's notional; becoming maker later does not reset
or increase its previous taker total. Self-trade cancellation accrues nothing.

Buy placement and cancellation use `buyFunding.totalEscrow`. Settlement uses
`buyFillFunding` for the buyer's refund and remaining escrow, and
`sellFillFunding` for seller proceeds/history. The actual remaining holding must
match the helper result. Fees remain zero: policy, template and settlement
movement guards all prevent accidental nonzero activation without collection.

For example, a buy of 5 at 0.60 taking an older sell of 3 at 0.40 keeps original
size 5, remaining size 2 and cumulative taker notional 1.20. Its 3.00 escrow pays
1.20, refunds 0.60 and retains 1.20. Cancelling returns that remaining 1.20.
If the same buy later executes as maker, its 1.20 taker history stays unchanged.
A sell can execute above its own limit; its history bound is filled contracts
at the maximum one-unit payout, rather than filled contracts at its sell limit.

Six registry-backed scripts check initialization, partial buy/sell history,
maker/taker continuation, cancellation and impossible signed-history rejection.
Existing settlement tests still check wrong backing and registry failures after
credits/refunds, now through these helper-based paths. Fee-pool transfers and
nonzero-fee cancellation/refunds must be tested when collection is integrated.
