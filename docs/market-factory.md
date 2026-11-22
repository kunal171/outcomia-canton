# Market factory standard

Status: **steps 1–2 implemented** (standard package and Outcomia's factory);
eligibility enforcement and invite lists are next. Phase B of
[clubs and private markets](clubs-private-markets.md)).

Goal: every market is created through a factory, and the factory contract
shapes are an open, reusable standard (Apache-2.0) that any Canton operator can
run without depending on Outcomia's matching or custody code.

## Decisions

| Topic | Decision |
| --- | --- |
| Packaging | An interface-only standard package plus Outcomia's reference implementation behind it. |
| Scope | One factory choice creates the whole market bundle atomically: market, collateral reserve and order book. |
| `Protocol_CreateBinary` | Kept for admin-created public markets; the factory is a second, complete creation path. |
| Who runs factories | Any operator deploys the package and runs their own instances. Outcomia runs one public instance; clubs get their own instances. |
| Public creation | Each factory instance holds a creation policy: admins only, an allowlist, or any enrolled party. Outcomia starts with admins only. |
| Market numbering | A counter per factory instance. Creation consumes only that instance, so factories never contend with each other. |
| Trading eligibility | A pluggable `EligibilityPolicy` interface consulted on entry actions. Public access, invite lists and club membership are implementations. |
| First release modes | Public, club and invite-only markets. |

## Standard package: `canton-market-factory`

An interface-only Daml package (`contracts/factory`), depending only on
`daml-prim` and `daml-stdlib`. It never changes when an implementation
upgrades, so applications and indexers can rely on it.

**Identity.** `FactoryRef { operator, namespace, factoryId }` names one factory
instance; `MarketRef { factory, number }` names one market. Both are stable
application identifiers; contract IDs change on every consuming choice and are
never identities.

**Terms.** `MarketTerms` is the common core every implementation accepts:
question, outcome labels and per-outcome criteria, invalid criteria, evidence
requirements, rules URI and SHA-256, collateral instrument, trading cutoff,
earliest resolution time, review delay, price tick and quantity lot. Binary
markets have exactly two outcomes; multi-outcome implementations use more.
Implementations validate and map these terms to their own types.

**Interfaces.**

- `MarketFactory` — view: reference, creation policy, next market number,
  supported outcome counts. Choice `MarketFactory_Create` (controller: the
  creator) takes `MarketTerms` and an access choice, and returns the next
  factory revision and the created market.
- `Market` — view: reference, creator, question, outcome labels, cutoff,
  lifecycle status and access. Indexers (CantonGrid M2/M3) link a factory
  exercise to the markets it created and read stable references from the view.
- `EligibilityPolicy` — view: reference and kind. Nonconsuming choice
  `EligibilityPolicy_Check` (controller: the policy's operator) asserts that a
  party may take an entry action (place, split or fill), optionally using
  evidence contracts the party presents (such as a club membership).

Access is `Public` or `Restricted policyRef`. A market stores the stable policy
reference, and each entry action passes the current policy contract, whose view
must match that reference and whose signatory must be the market's operator.
Exits (cancel, merge, withdraw, redeem) never consult eligibility.

## Outcomia reference implementation

- `OutcomiaMarketFactory` (signatories: operator and vault) implements
  `MarketFactory`. One creation creates the `BinaryMarket`, its
  `MarketReserve` and its `OrderBook` with the next number, after checking the
  creation policy and the binary terms. A failure rolls back all three.
- Factory-created markets carry their `FactoryRef` in an upgrade-safe trailing
  optional field of `MarketKey`; markets from `Protocol_CreateBinary` keep
  `None`, so the two numbering spaces never collide.
- `InviteListPolicy` implements `EligibilityPolicy` for invite-only markets.
  Club membership becomes a second implementation in Phase C.
- Placement, split and matching call the market's policy for restricted
  markets. Matching checks both orders, so revoked eligibility stops fills.

## Delivery

1. **Done.** Standard package (interfaces, types, validation helpers), tested
   with independent toy templates.
2. **Done.** Outcomia factory: creation policy, admitted assets, per-factory
   numbering, atomic Open market/reserve/book creation and factory-admin
   management (close, propose, correct), isolated by scope from protocol-root
   markets and other factory instances. `Protocol_CreateBinary` is unchanged.
   Fee quotes still come from the protocol root's taker fee.
3. Eligibility enforcement on placement, split and matching, plus invite lists.
4. Clubs (Phase C) as factory instances with membership eligibility.

Each step runs the full contract suite; existing tests must pass unchanged.
