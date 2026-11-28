# Outcomia Canton

Daml contracts for Outcomia's limit-order prediction markets on Canton. The UI
lives in the shared app, [`kunal171/outcomia/app`](https://github.com/kunal171/outcomia/tree/master/app);
there is no separate Canton frontend.

**What is built** (each locally tested, with its UI in the shared app):

- binary markets: lifecycle, collateral custody, complete sets, limit orders,
  direct and complementary matching, fees, resolution and redemption;
- the market factory standard, clubs (membership, roles, rules, listings, club
  fee share) and invite-only markets;
- multi-outcome markets (2–8 outcomes) with full-set matching;
- on-ledger profile claims that link a Canton party to an Outcomia profile.

**Not done:** public-network deployment and a live wallet smoke test. Canton
trading stays disabled in the app until both are verified.

## Docs

| Doc | Covers |
| --- | --- |
| [Architecture](docs/architecture.md) | Roles and trust, collateral custody, complete sets, visibility |
| [Trading](docs/trading.md) | Orders, matching, settlement and fees |
| [Resolution](docs/resolution.md) | Proposals, corrections, finalization and redemption |
| [Clubs](docs/clubs.md) | Market factory standard, clubs, eligibility, rules and listings |
| [Multi-outcome markets](docs/multi-outcome-markets.md) | 2–8 outcomes, full-set matching, limits |
| [Wallets](docs/wallets.md) | Loop and Console through CIP-0103 |
| [Development](docs/development.md) | Build, tests, dependencies and the DPM path workaround |

## Build

DPM SDK 3.7.1, Java 17+ and Python 3.10+.

```bash
make deps    # fetch and verify the pinned Token Standard interfaces
make build   # production and test DARs
make test    # IDE-ledger suite
```

Checkouts whose path contains spaces need the workaround in
[development](docs/development.md).

## License

Apache License 2.0; see [LICENSE](LICENSE) and [NOTICE](NOTICE). It covers this
repository's contracts, scripts and docs, not access to any hosted Outcomia
service, credentials or deployment.
