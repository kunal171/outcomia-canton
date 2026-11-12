# Checkpoint 1 verification

The wallet implementation now lives in the
[shared Outcomia app](https://github.com/kunal171/outcomia/tree/master/app).
This checkpoint verifies the wallet gateway, not Canton market contracts.

## Automated checks

In the shared app, TypeScript, production build and five Canton session tests
passed, along with the existing prediction, wallet, shared-trading, RPC, theme
and five-language translation checks.

Local browser checks used the real Console Wallet SDK with mocked extension
responses and a Solana wallet-standard fixture. They covered:

- Landing at 320, 390, 768 and 1440 px, without overflow.
- No chain reads or wallet requests before selection.
- Both wallet paths, switching in both directions and same-wallet reconnect.
- Reload verification and preservation of a requested Solana page.
- Rejected approval, wrong network and absent Console extension.
- Account changes and stale asynchronous party responses.
- Disconnect, wallet-side revocation and wrong-chain URLs.
- No Solana RPC reads while using Canton; queued requests stop on exit.

Existing Solana prediction and spot browser checks also passed, including
claims, cancellation after close, exact amounts, retained inputs, failed reads
and zero-balance withdrawal guards. No real signatures or transactions were
submitted. Fixtures and screenshots are local artifacts in the shared checkout's
ignored `target/ui-checks/`.

The shared lockfile audit still has 50 findings (53 on the previous master).
Next.js is updated to 16.4.6; remaining dependency work is separate from this
repository-ownership correction. The earlier standalone app's clean audit does
not describe the larger shared app.

## Real-wallet smoke still required

On the presentation machine, install Console Wallet and select an allocated
primary party on the configured network. Run the shared app, approve the
connection, inspect party/network, change accounts, switch wallets and disconnect.
Reject one connection request as well. Automated fixtures do not establish that
an actual installed extension approved a live account.

## Product boundary

The Canton workspace reports `Market deployment pending`. Market creation,
collateral, orders, matching, resolution and redemption are subsequent feature
PRs. The removed duplicate app remains available in Git history; the shared app
is the single frontend source.

## Loop follow-up: 12 November 2026

The shared app now supports Loop alongside Console (Outcomia PR 43). Its deployed
wallet picker and live devnet health request passed a public browser check. The
user confirmed connection to a real Loop devnet wallet and access to the Canton
pages. Funded balances and wallet-to-ledger market commands remain unverified;
the funding request is pending. This does not replace the Console extension
smoke check described above. No wallet secrets are kept in this repository.
