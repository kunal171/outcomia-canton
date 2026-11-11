# Outcomia Canton app

```bash
npm ci
cp .env.example .env.local  # First setup only.
npm run dev -- --port 3012
```

Install Console Wallet, select the configured network, then connect from the
landing page. The default is `canton:devnet`. An allocated primary party is
required. No transaction is signed just to connect.

```bash
npm run typecheck
npm test
npm run build
```

`/` is the wallet gateway. `/markets` is gated by the live wallet session. The
Canton market deployment is not implemented in this checkpoint; the workspace
reports that state and does not render mocked markets.

The application holds public party/network identity only. Console Wallet owns
approvals and signing. The session gate is a UI boundary, not server-side
identity authentication or a replacement for Daml authorization checks.
