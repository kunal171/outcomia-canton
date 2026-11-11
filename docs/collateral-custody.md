# Collateral custody

Status: decision pending. There are no deposit balances or outcome positions yet.

The next contracts must hold real collateral before issuing YES/NO positions.
Our [transfer adapter](collateral-transfers.md) verifies unlocked transfers; it
does not reserve tokens or prevent their owner from spending them later.

## The choice

| Model | Who holds the tokens? | What we must verify |
| --- | --- | --- |
| Trader-owned reservations | The trader, with registry-enforced restrictions | The chosen registry supports the allocation/lock operations and allows settlement and safe exits. |
| Separate vault party | A party dedicated to Outcomia custody | Its signing and hosting policy, approved registry code, and the authority delegated to market contracts. |

A vault party is not a Solana PDA. Anyone controlling its signing authority may
be able to transfer its holdings directly through the registry, bypassing our
accounting. Separating that party from the operator helps organize authority;
it does not remove custody risk. Multi-hosting can distribute that authority,
but must be configured and verified rather than assumed.

Trader-owned reservations also need more than a `lock` field in a holding view.
The registry must enforce who can spend, release or expire the reservation.
The current adapter deliberately rejects locked holdings. Removing that check
would not implement a reservation system.

No public registry, asset or hosting arrangement has been selected for this
checkpoint. Local test holdings are not evidence of public-network support.

## Rules for either model

- A deposit credits a balance only when the same transaction secures the exact
  amount of the approved asset. A fetched holding alone is not a receipt.
- One collateral unit creates one YES and one NO contract unit. Splitting 5
  collateral creates 5 YES and 5 NO; it does not create 10 collateral of backing.
- Merging 3 YES and 3 NO destroys both positions and releases 3 collateral in
  one transaction. A single outcome cannot use this merge path.
- Before resolution, outstanding YES supply equals outstanding NO supply and
  equals the collateral reserved for complete sets. Trading changes ownership,
  not total backing. Final redemption needs its own accounting rules.
- Reusing consumed holdings, positions or old account revisions must fail.
- New splits require an open market before its cutoff. A pause or cutoff must
  not prevent free withdrawals or otherwise valid complete-set merges.
- Revoking asset admission blocks new funding. It must not, by itself, block
  exits using the saved approved factory. Issuer freezes and factory retirement
  still need an explicit exit policy.
- Balances use stable party/asset identity. Positions and reserves use stable
  market identity, not the contract ID replaced by an open/close operation.

Deposits and trading remain disabled in the UI until the selected custody flow
is tested with the actual registry, wallet and network deployment.

## Sources

- [CIP-0112](https://github.com/canton-foundation/cips/blob/main/cip-0112/cip-0112.md)
  describes Token Standard V2, including prefunded trading allocations. It does
  not establish support by our eventual registry.
- [OpenZeppelin's Canton lending architecture](https://github.com/OpenZeppelin/canton-specs/blob/main/docs/reference-architectures/lending.md)
  describes a separate venue party and the residual authority of its hosts.
  This is a reference design, not a deployed dependency of Outcomia.
