# Collateral custody

Decision: use a dedicated vault party for the first version. Its signer/hosting
trust remains explicit. Outcome positions are the next part of this checkpoint.

The custody contracts hold real collateral before issuing YES/NO positions.
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

## Available balances

`VaultAuthority` is signed by the operator and a distinct vault party. A trader
enrolls once per asset using an active admission. Enrollment consumes the current
authority revision, so two enrollments for the same trader/asset cannot succeed
within that lineage. Clients must pin one configured root: joint operator/vault
signers could create another root. The prototype index holds at most 1,024
enrollments. This bounds contract size but serializes onboarding and exposes
enrolled keys to subsequent enrollees; it is unsuitable for private club accounts
without a separate privacy/uniqueness design.

`AssetBalance` is signed by the trader and vault. Its available amount is backed
by one vault-owned holding. A zero account has no holding. No account is tied to
a particular market, and neither operator nor trader alone can forge a funded
account. Joint vault/trader signers remain trusted.

Deposits use an active admission matching the enrolled operator, asset and exact
factory. A pinned transfer choice performs these checks without granting the
trader operator authority. Wallet inputs move to the vault and are consolidated
with existing backing in the same transaction. For example, 2 available plus a
deposit of 3 produces one holding of 5 and a new balance revision. Wallet change
is returned separately.

Only the owner can withdraw through the balance choice. It consumes backing and
creates the successor with exact change, using the saved factory even after
admission revocation. Both paths check the old holding amount against the signed
balance; stale accounts and consumed holdings cannot be reused.

Consolidation must return one receiver holding with no change. Withdrawal must
return at most one change holding. Fragmenting registries are unsupported by
this custody adapter even when their transfers satisfy the generic standard.
The existing transfer limit is 16 inputs, including old backing during
consolidation. Unsupported output shapes roll back the entire operation.

Clients still need registry context and visibility/disclosures for referenced
contracts. Local tests use issuer read access to supply visibility; that is not
a production wallet integration or permission to sign as the issuer.

Ten custody scripts cover deposits, consolidation, partial/full withdrawals,
owner authorization, duplicate/stale enrollment, invalid amounts, receipt
replay, revoked admission, asset/factory/operator isolation, faulty registry
rollback, mismatched backing, capacity limits and the smallest Decimal amount.
The complete suite passes 31 Daml scripts and four dependency-integrity tests.
The production DAR also passes validation. These are local ledger checks.

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
