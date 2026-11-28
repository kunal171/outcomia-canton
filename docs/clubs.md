# Market factory and clubs

Principle: **authorization lives on the ledger.** The indexer and the UI never
grant rights, and a private club is not a frontend filter.

## Market factory standard

`contracts/factory` is an interface-only package (Apache-2.0) that any Canton
operator can implement. It depends only on `daml-prim` and `daml-stdlib`, so it
never changes when an implementation upgrades.

- **Identity:**
  - `FactoryRef { operator, namespace, factoryId }` names a factory instance;
  - `MarketRef { factory, number }` names one of its markets;
  - each instance numbers its own markets, so factories never contend with each other.
- **`MarketTerms`** hold the question, 2–8 outcome labels with criteria, invalid
  criteria, evidence requirements, the rules URI and hash, collateral, cutoff,
  earliest resolution, review delay, tick and lot. Exactly `YES, NO` creates a
  binary market (`NO, YES` is rejected); any other list creates a multi-outcome market.
- **Interfaces:**

  | Interface | What it does |
  | --- | --- |
  | `MarketFactory` | `MarketFactory_Create`, which can take an optional creation proof |
  | `Market` | A view indexers read |
  | `EligibilityPolicy` | `EligibilityPolicy_Check` on entry actions (place, split, fill, create market). Its pure `excludes` method lets the operator clear orders of parties who lost access. |

- **Access:**
  - **Rules:** a market is `Public` or `Restricted policyRef`. Exits (cancel, merge,
    withdraw, redeem) never consult eligibility.
  - **Creation policies:** admins only, an allowlist, any enrolled party, or
    `ByPolicy` (for example, club membership).

**Outcomia's implementation.**
- **`OutcomiaMarketFactory`** (operator and vault) creates the market, its reserve and
  its book atomically. Its markets carry the `FactoryRef` in `MarketKey.scope`;
  markets from `Protocol_CreateBinary` have `None`.
- **`InviteListPolicy`** provides invite-only markets.
- **Factory admins** close, propose and correct the factory's markets.

## Clubs

| Contract | Signatories / observers | Purpose |
| --- | --- | --- |
| `ClubRegistry` | operator, vault | Numbers clubs, counts clubs per owner and holds the club rules; `ClubRegistry_CreateClub` (any party) creates the club and its own factory |
| `Club` | operator, owner / members, invitees | The whole roster, invitations, market policy, listing and caps; it implements `EligibilityPolicy` |
| Club factory | operator, vault / club admins | An `OutcomiaMarketFactory` with `ByPolicy` the club; its admins stay in sync with the club |

- **Roles:**
  - **Owner:** manages admins and transfers ownership in two steps (nominate, then
    accept).
  - **Admins:** invite, remove members and run club markets; current admins resolve
    them.
  - **Members:** anyone except the owner may leave.
- **Joining:**
  - **Invites:** expire after 7 days, and the invitee must accept.
  - **Listed clubs:** a verified request-to-join listing also admits join requests
    (140-character note, 7 days, approved by an admin). A verified open listing lets
    anyone join with `Club_JoinOpen`.
- **Markets:** admins (or every member, by policy) create them. Each is members-only
  or public.
- **Removal:**
  - **Entry:** every fill re-checks both owners against the current `Club`, so a
    removal and a concurrent fill are ordered by the ledger.
  - **Clearing orders:** `OrderBook_CancelIneligible` (operator) clears a departed
    member's resting orders and returns their backing. Strangers can't see these
    orders, unlike on Solana.
  - **Exits:** they never need membership.
- **Why one contract:** the roster lives on one contract so members see their club
  without a disclosure service. Each change consumes the club, so changes within one
  club serialize. Limits: 256 members, 64 admins and 64 pending invitations.

## Rules and listings

These match Solana's club rules
(outcomia `docs/clubs.md`, club rules).

| Rule | Canton |
| --- | --- |
| Type | `PrivateClub` or `PublicClub`, fixed at creation; only public clubs can be listed |
| Member caps | `publicMemberCap` / `privateMemberCap`, capped at 256 until membership moves to per-member contracts; every join path checks the cap |
| Admin cap | `maxClubAdmins` (owner included), checked on promotion and ownership transfer |
| Owned clubs | `ClubRegistry.owned`; creation and `ClubRegistry_AcceptOwnership` are refused at `maxOwnedClubs` |
| Rule changes | `ClubRegistry_SetRules` applies to new clubs and `Club_ApplyRules` to an existing one; lowering a cap removes nobody |
| Listing | `Club_SetListing`: request-to-join or open, a 1–32 character topic and up to 280 characters of description; any change clears verification |
| Verification | `Club_VerifyListing` by a protocol-root admin; club-scoped roles are rejected, so a club can't verify itself |
| Fee share | See [trading](trading.md#fees) |

**Discovery:** the app's operator service discloses only verified public clubs.
Disclosure hands over the whole club contract, including the roster. Private clubs
are never disclosed. Requesters see the club only while their request is pending.

## Visibility

| Data | Who receives it |
| --- | --- |
| Club, roster, invitations | Operator, owner, admins, members and invitees |
| Club market terms and book | Eligible traders, through operator disclosure. `OrderReference` has no owner, so the book reveals prices and sizes, not who placed them. |
| Orders, positions, balances | Their owner, the vault and the operator |

Members who are removed keep any data they already received. Club security
deposits, disputes and penalties (Solana milestones 2–4) are not built on Canton yet.
