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
[the plan](docs/delivery-plan.md). The shared wallet gateway is implemented;
Canton market contracts, collateral, order matching and settlement are next.
No Canton markets are deployed yet.
