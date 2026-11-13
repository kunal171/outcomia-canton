# Binary redemption

A final result fixes the outcome. It does not pay anyone by itself.

1. The operator finalizes the proposal after its review delay.
2. The operator binds that exact `FinalResolution` to the market reserve.
3. Each trader claims their own available position lots.
4. The claim credits their Outcomia asset balance. Withdrawal sends tokens to their wallet.

## Reserve transition

`MarketReserve_BindResolution` consumes the live reserve and creates a
`SettledReserve`. It checks the market key, creator, terms and creation time
against the final snapshot, plus the actual backing holding. Split and merge
can no longer use the consumed live reserve.

The settled reserve tracks outstanding YES, outstanding NO and remaining
collateral. A position cannot claim against another market or vault.
Open orders are not automatically canceled. Owners can still cancel them after
resolution: sell cancellation releases outcome lots; buy cancellation returns
collateral. Released lots can then be claimed.

## Payouts

| Final result | One YES | One NO |
| --- | --- | --- |
| YES wins | 1 collateral | 0 |
| NO wins | 0 | 1 collateral |
| Invalid | 0.5 collateral | 0.5 collateral |

For example, 3 YES and 2 NO pay 3 for YES, 2 for NO, or 2.5 for Invalid.
The invariant is `remainingCollateral = payout(outstandingYES, outstandingNO)`.
Fees already earned by the order book are separate and cannot fund claims.

Collateral precision is pinned when the reserve is initialized. Half a contract
lot must be representable in that asset, so a whole-unit collateral token needs
an even contract lot. Book creation must match the reserve's precision. No
rounding loss is silently charged to the last claimant. Counts are converted to
Decimal before addition so two large Int64 supplies do not overflow their sum.

## Claim rules

`SettledReserve_Redeem` requires the position owner. It accepts 1–16 distinct,
owned lots for this market/vault and the owner's matching asset balance. It
consumes all supplied lots, including losing outcomes, and decreases outstanding
counts. Reusing an old lot or reserve ID fails. Multiple batches are needed for
more than 16 lots.

Positive payouts repartition actual reserve tokens into the trader balance.
Zero payouts only clear positions; they do not request a zero-value token
transfer. A failed transfer rolls back the reserve, lots and balance together.
The jointly signing operator/vault remain trusted, as in the existing custody
model. This transition does not remove that trust or guarantee operator liveness.

## Verification

`RedemptionTest.daml` has 12 scripts. The full suite has 178 passing Daml scripts,
four Python checks, and independent fee arithmetic checks. Redemption coverage
includes YES/NO/Invalid trading-to-withdrawal lifecycles, exact total cash
conservation, zero payouts, replay, ownership, malformed batches, foreign final
snapshots, invalid precision, canceled sell escrow and faulty transfer rollback.
The production DAR validates with 39 packages.

The shared UI now builds typed wallet commands for funding, orders, operator
matching, resolution and claims. Its deployment configuration remains disabled.
No public-network deployment or live wallet smoke test was performed in this
feature. See the shared app's Canton trading setup guide for the read-only
catalog and registry-context adapter boundaries.
