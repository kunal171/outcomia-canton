# Checkpoint 1 verification

Verified on 2026-11-11 with Node 24.21.0, Next.js 16.4.6 and Console Wallet SDK
3.0.0. This report covers the wallet gateway, not market contracts or settlement.

## Automated checks

- TypeScript check and production build: passed.
- Five identity/network tests: passed.
- `npm audit` after compatible fixes: zero known vulnerabilities reported.
- Browser at 320, 390, 768 and 1440 px: no page overflow; screenshots reviewed.
- Light/dark appearance and cookie restoration: passed.
- No wallet requests before the user initiates connection: passed.
- Unconnected direct navigation to `/markets`: returns to the gateway.
- Successful connection, reload verification, rejected approval, wrong network,
  missing extension, account changes and stale account reads: passed.
- Manual disconnect and wallet-side revocation clear the gated workspace.
- The browser fixture used the real SDK with mocked extension postMessage
  responses. No external requests, signatures or transactions were issued.

The browser fixture and screenshots are local validation artifacts in ignored
`target/`; they are not a production wallet implementation or shipped mock.
The committed identity tests run with `cd app && npm test`.

## Real-wallet smoke test still required

On the presentation machine, install Console Wallet and select the configured
network (`canton:devnet` by default) with an allocated primary party. Start the
app, approve connection, inspect the displayed party, change accounts, then
disconnect. Check rejection once as well. No real extension account or key was
available in the automated browser, so live wallet approval is not claimed here.

## Current product boundary

The app reports `Market deployment pending`. Daml market creation, collateral,
orders, matching, resolution and redemption are subsequent feature PRs. No mock
market listings or successful settlements are displayed.
