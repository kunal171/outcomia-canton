# Clubs and private markets

Status: **design agreed, not implemented** (Phase A). There are no club,
invitation, membership, factory or private-trading contracts yet, and no working
Canton UI flow for them. Market creation still requires protocol admin
authority through `Protocol_CreateBinary`.

This design follows the product rules already shipped for Outcomia on Solana
(see `kunal171/outcomia` `docs/clubs-private-markets.md`), changed only where
Canton's privacy model requires it. Clubs start with **binary** markets;
multi-outcome club markets follow checkpoint 6. Everything here applies to the
contracts in this repository; the shared UI lives in `kunal171/outcomia/app`.

Principle: **authorization lives on the ledger; indexing and UI never grant
rights.** A private club is not a frontend filter, and CantonGrid can only show
what a caller is already entitled to see.

## Decisions

| Topic | Decision |
| --- | --- |
| Creating a club | Any enrolled party, through the operator's club factory. The creator becomes the club **owner**. Club roles never grant protocol-admin authority, and protocol admins gain no club authority from their protocol role. |
| Roles | **Owner** adds/removes admins and transfers ownership (two-step: nominate, then the nominee accepts). **Admins** manage invitations, members and club markets. Any member may leave; the owner must transfer ownership first. |
| Joining | An admin **invites** a party; the party joins only by **accepting**. Invitations expire after **7 days**; admins can revoke earlier and the invitee can decline. |
| Creating club markets | Per-club policy: **admins only** (default) or **any member**. |
| Who trades | Per market: **members-only** or **public** (anyone eligible trades; the club curates and resolves). |
| Removal | A removed member cannot place, split or have resting orders fill. Their resting orders are cancelled by the operator service (funds return to the owner), and matching rejects them regardless. |
| Exits | Cancel, withdraw, merge and redeem never require membership. Removal never confiscates or strands a position. |
| Resolution | Any **current club admin** proposes or corrects under the existing windows, review delay and correction deadline. No fallback resolver for club markets. Finalization stays as today (see issue #18). |
| Fees | Traders pay the normal taker fee. A protocol-wide **club share** of it accrues to the club; only the owner withdraws it. Not part of the first club release. |
| License | Apache-2.0 (PR #23), before the factory is presented as reusable. |

### What differs from Solana, and why

- **Departed-member orders.** On Solana anyone can cancel them because every
  account is public. On Canton a stranger cannot see a member's order, so the
  operator service cancels them, and matching independently rejects any order
  whose membership is no longer active.
- **Membership proof.** Solana checks a PDA that exists only while the wallet
  is a member. Daml 3 has no contract keys, so a party proves membership by
  presenting its active `ClubMembership` contract; matching re-fetches it, and
  an archived membership fails the transaction.
- **Privacy is real but bounded.** Canton restricts who receives contracts, but
  the operator and vault host and process club contracts, explicit disclosure
  hands contracts to the parties a service chooses, and a removed member cannot
  be made to forget data already received.

## Identity

- **Clubs:** `ClubId = { operator, protocolName, clubNumber }`. A
  `ClubRegistry` (operator-signed) allocates `clubNumber`; club creation is
  rare, so this one consuming counter is acceptable.
- **Club markets:** keep the market identity `MarketKey { operator,
  protocolName, marketId }` and add an upgrade-safe trailing
  `scope : Optional ClubId` (`None` means a public market). Club market numbers
  are allocated per club by that club's market factory, so clubs never share a
  write lock with each other or with public creation (issue #21).
- **Never** use a `ContractId` as an external identity: markets, clubs and
  memberships are archived and recreated by consuming choices.

## Contracts (Phase C, built on the market factory)

Clubs reuse the [market factory standard](market-factory.md) instead of a
separate market path:

| Contract | Signatories / observers | Purpose |
| --- | --- | --- |
| `ClubRegistry` | operator, vault / — | Allocates club numbers and admitted collateral. `ClubRegistry_CreateClub` (any party) creates the club, the owner's membership and the club's own `OutcomiaMarketFactory`. |
| `Club` | operator, owner / admins | Name, owner, pending owner, admin list, market-creation policy and stable references. **Implements `EligibilityPolicy`**: it admits current members to place, split and fill, and admits market creation by admins (or any member under the any-member policy). Consumed only by owner/admin/policy changes, never by joining or leaving. |
| `ClubMember` | operator, member / — | Active membership, **implements `EligibilityEvidence`**. Archived on leave or removal; a rejoin is a new contract. |
| `ClubInvite` | operator, inviter / invitee | Seven-day invitation: accept (creates the membership), decline, revoke by an admin, clear after expiry. |
| Club factory | operator, vault / club admins | An `OutcomiaMarketFactory` whose creation policy is `ByPolicy` the club and whose admins the `Club` keeps in sync, so club admins manage club markets. |

- **Members-only markets** are created with `Restricted clubPolicyRef`; public
  club markets with `Public`. Either way the club curates and resolves.
- **Membership proof** is the member's `ClubMember` contract, presented as
  evidence. Fills re-check both parties with their current memberships, so a
  removed member's resting order cannot fill.
- **Admins** are listed on `Club` (owner always included); promotion, demotion,
  removal of an admin and ownership transfer update the club factory's admins in
  the same transaction, using the operator's signature on both contracts.
- **Standard extension:** `CreationPolicy` gains `ByPolicy PolicyRef`,
  `EntryAction` gains `CreateMarket`, and `MarketFactory_Create` takes an
  optional creation proof, so any implementation can gate creation on
  credentials (club membership, KYC, token holdings).
- `ClubRemoval` and `OrderBook_CancelDeparted` (operator cleanup of departed
  members' orders) remain Phase E.

Every club choice fetches the current `Club`, so revoked rights stop at once.

## Visibility matrix

| Data | Who receives it |
| --- | --- |
| Club name and policy | Owner, admins; members through operator-provided disclosure. No public listing unless the club opts in later. |
| Members and invitations | The member or invitee, the owner, and admins through disclosure. No cross-club enumeration. |
| Club market terms and book | Current members (members-only) or eligible traders (public), through explicit disclosure by the operator service. |
| Orders and positions | Owner, vault and operator, as today. `OrderReference` carries no owner, so book disclosure reveals prices and sizes, not who placed them. |
| Factory → market lineage | Only callers who can see the creating exercise and the market (CantonGrid M2/M3 rules). |
| Exit after removal | The member's own orders, positions and balances. The operator cancels resting orders, so a departed member needs no new book data. |

Known existing exposure, not introduced by clubs: `VaultAuthority.accounts`
lists every enrolled `(party, instrument)` and is disclosed to each enrolling
party, revealing protocol participation (not club membership). Replacing it
with per-owner enrollment is tracked separately (issue #21).

## Removal and matching

1. On placement in a members-only club market, `LimitOrder` records the
   placer's active `ClubMembership` contract ID.
2. `OrderBook_MatchBest` fetches both orders' recorded memberships. If either
   was archived (left or removed), the fill fails: removal and a concurrent fill
   are ordered by the ledger, not by an off-ledger cache.
3. Removal archives the membership and creates a `ClubRemoval`. A new
   `OrderBook_CancelDeparted` choice (controller: operator) cancels an order
   whose recorded membership is named in a `ClubRemoval`, releasing its backing
   to the owner exactly like owner cancellation.
4. A rejoined member gets a new membership; their old orders stay unfillable
   and are cancelled the same way.
5. Owner cancellation, withdrawal, merge and redemption never check membership.

Splitting collateral into a complete set is an entry action and requires an
active membership in members-only markets.

## Market creation (Phase B factory)

The general factory standard (interfaces, numbering, eligibility and the
reference implementation) is specified in [market factory](market-factory.md);
the club factory is one instance of it.


`Protocol_CreateBinary` consumes the single `Protocol` contract for every
market, which serialises all creation. Phase B keeps it unchanged for public
markets (existing tests must pass untouched) and adds `ClubMarketFactory`.
The club factory checks the creator against the live `Club` policy, uses the
operator's authority from its own signature, and never touches `Protocol`'s
admin list. Club markets record the creator as `resolver` for history only;
resolution checks current club adminship.

## Delivery phases

Each phase ships its contracts **and** the matching UI in the shared app
(`kunal171/outcomia`, `app/canton`) together. Live trading stays behind the
existing deployment gate until Phase F.

| Phase | Contracts | UI (same phase) | Gate |
| --- | --- | --- | --- |
| A — Define | This document | — | Reviewed |
| B — Factory | Standard package, `MarketKey.scope`, Outcomia factory, eligibility, invite lists; public creation unchanged | Create markets through the factory (policy shown, public or invite-only access), factory-admin close/propose, eligibility evidence on orders and splits | Existing binary tests unchanged; factory and UI command tests |
| C — Clubs | `ClubRegistry`, `Club`, `ClubAdmin`, `ClubInvitation`, `ClubMembership`, club factory instances | Club pages: create, invite/accept/decline, members and roles, club market creation | Club lifecycle works without trading; negative authorization tests |
| D — Lineage | Factory exercise → market evidence; LocalNet scripts | Market and club provenance shown from indexed data | CantonGrid M2 verified-tree and M3 declared-link acceptance |
| E — Trading | Membership on orders, matching checks, `ClubRemoval`, `OrderBook_CancelDeparted`, club resolution | Membership-aware trading, departed-member state, club resolution | Removal/fill race, exit and multi-party disclosure tests |
| F — Harden | Club fee share, deployment, multi-outcome clubs | Remove the deployment gate after a wallet smoke test | Controlled-network acceptance |

## Acceptance tests (minimum)

- Existing admin-controlled binary creation passes unchanged after Phase B.
- An accepted invitation creates an active membership; a non-member cannot
  create, split, place or fill in a members-only market.
- Two clubs keep separate markets, policies, orders and totals.
- Losing a role stops new market creation without touching protocol-admin rights.
- A removed member holding stale contract IDs cannot place or fill, and can
  cancel, withdraw, merge and redeem.
- A removal racing a fill is resolved on the ledger, with rollback.
- Multi-party LocalNet tests confirm the actual disclosure graph before any
  claim of club privacy.

## Open questions

- Does the club owner need to see every membership (observer), or only through
  disclosure? Observer status is simpler but ties membership contracts to owner
  changes.
- Club discovery for public club markets: an opt-in, operator-published listing,
  or invite links only?
- Should club markets reuse the shared per-market `OrderBook` disclosure, or
  move to member-scoped book views before Phase E?
