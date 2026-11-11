# Outcomia Canton

Canton contracts and services for Outcomia's limit-order prediction markets.
Binary markets come first, followed by multi-outcome markets, clubs/private
markets and governance-created markets. Multi-outcome markets initially have
exactly one winner. Canton spot trading is outside the current scope.

## Shared frontend

The UI lives in [`kunal171/outcomia/app`](https://github.com/kunal171/outcomia/tree/master/app).
There is no separate Canton frontend. That app uses the selected wallet to open
Solana markets or the Canton prediction workspace. Console Wallet must provide
an allocated primary party on the configured network (`canton:devnet` by default).

Run the shared app using [its setup guide](https://github.com/kunal171/outcomia/blob/master/app/README.md).
See [the wallet boundary](docs/wallet-gateway.md) and
[verification](docs/checkpoint-01-verification.md).

## Delivery

Use small commits, a feature PR, and a merge before the next checkpoint. See
[the plan](docs/delivery-plan.md). The shared wallet gateway,
[binary lifecycle](docs/binary-market-lifecycle.md) and
[Token Standard transfers](docs/collateral-transfers.md) are locally tested. The
[dedicated-vault balances](docs/collateral-custody.md) support deposits and withdrawals;
[complete sets](docs/complete-set-positions.md) support YES/NO split and merge.
Order matching, resolution and redemption remain. No Canton markets are deployed yet.

## Contracts

Use DPM SDK 3.7.1, Java 17 or newer and Python 3.10+. `make deps` fetches and
verifies pinned Token Standard interfaces. `make build` builds the production and
test DARs; `make test` runs the IDE-ledger suite. The production package does not
depend on `daml-script`. For checkouts with spaces, see the [DPM path issue
and explicit local override](docs/dpm-local-path-issue.md).
