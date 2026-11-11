# Outcomia Canton

A limit-order prediction market for Canton Network.

The product starts with binary YES/NO markets, followed by markets with multiple
outcomes, clubs/private markets and governance-created markets. Multi-outcome
markets initially have exactly one winning outcome. Spot trading and Solana
integration are outside this repository's current scope.

The UI reuses Outcomia's design from `kunal171/outcomia` at commit `60309a9`.
No private environment files, keys or deployment credentials were copied.

## Delivery

Each checkpoint uses small commits on a feature branch, one pull request, and a
merge before the next checkpoint begins. See [the plan](docs/delivery-plan.md).

## App

Use Node 24 (`nvm use`), then:

```bash
cd app
npm ci
cp .env.example .env.local  # First setup only.
npm run dev -- --port 3012
```

The wallet must have an allocated primary party on the configured Canton
network (`canton:devnet` by default). See [the app guide](app/README.md) and
[wallet boundary](docs/wallet-gateway.md).

## Checkpoint status

The Console Wallet gateway is implemented. Canton market contracts are not yet
deployed. See [verification and the real-wallet smoke step](docs/checkpoint-01-verification.md).
