# Clubs and private markets

Status: planned, not implemented. There are no club, invitation, membership,
private-trading or governance contracts or corresponding working Canton UI flows.
Existing market creation requires protocol admin authority; it is not yet a
permissionless user-created market feature.

## What exists first

The shared UI connects Loop or Console Wallet. Canton contracts have locally
tested binary creation/open/close, shared per-asset balances, complete-set
split/merge, funded orders, cancellation and one-pair atomic matching, funded fee collection and operator fee withdrawal. Resolution, reward redemption and multi-outcome markets remain.
No public Canton market deployment or wallet-to-ledger trading is verified.

The current roadmap places clubs/private markets after resolution/redemption
and multi-outcome markets, then governance. Clubs can technically start with
binary markets; multi-outcome support is not an inherent dependency. Safe exits,
permission checks and a reviewed disclosure model are prerequisites.

## Required work

- A permanent club identity, club admins and separately scoped creator roles.
  Club roles must not silently grant global protocol-admin authority.
- Wallet-party invitations and active/revoked memberships, checked by contracts.
  A remembered wallet or hidden frontend route does not grant permission.
- Explicit visibility and trading rules for each restricted market.
- Membership checks on new orders and new exposure. Define removal behavior for
  resting orders: they must not keep trading merely because the frontend hides
  them. Revocation and a concurrent fill need ledger-level ordering checks.
- Exit rights independent of active membership: cancellation, withdrawal,
  valid complete-set merge and eventual redemption. Removal must not confiscate
  or strand an existing position. Market resolution remains available.
- Privacy tests for onboarding, order placement, matching, member removal and
  exit. Include a former member who already knows old contract IDs.
- Discovery, invitations and club administration in the original shared UI.
  Leaderboards/history must use authorized data rather than a global exposure
  of private member activity.

## Current disclosure constraints

Canton can restrict contract disclosure, but it does not make an arbitrary
application private automatically. Authorized hosts and the trusted custody
operators still have access to the contracts they process. Revoking membership
cannot erase information a member has already received.

The current matching choice fetches the full bounded order index and its order
contracts inside a transaction visible to the matched traders. The account
registry also contains a shared enrollment list. Those designs must be reviewed
before using them for private clubs; a `private` flag is insufficient.

Owner cancellation currently needs the current book. A removed member must be
able to exit without receiving unrelated new private order data. Design the exit
authorization/disclosure path before promising both privacy and unrestricted
exits. The [settlement design](binary-settlement.md) documents the present scope.

Fee pools may remain per market when clubs arrive. Club revenue sharing or fee
overrides are not part of the first fee implementation and cannot be inferred
from club-admin status.
