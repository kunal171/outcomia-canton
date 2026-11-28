# Wallets

The wallet gateway lives in the shared app. The landing page lets the user choose
a Solana wallet, Console Wallet or Loop Wallet. Either Canton wallet opens the
Canton workspace at `/canton/markets`.

Both Canton wallets are used through the **CIP-0103** dApp Standard provider:

| CIP-0103 call | Used for |
| --- | --- |
| `status` / `getPrimaryAccount` | Identity |
| `ledgerApi` | Reads |
| `prepareExecute` with `txChanged` events | Submission |
| Standard error codes | Failures |

- **Loop** uses `@fivenorth/loop-sdk` 0.16.0's native provider (hosted wallet or QR).
- **Console** (`@console-wallet/dapp-sdk` 3.0.0, browser extension) is adapted to
  the same provider. Console mobile QR is not enabled.
- **Signing** stays in the wallet; no keys or tokens enter the app's session.

Rules:

- **Networks must agree:** the configured CAIP-2 network, the active network and the
  account's network must match. The app targets `canton:testnet`
  (`NEXT_PUBLIC_CANTON_NETWORK_ID`); Solana stays on devnet.
- **Live verification:** a remembered wallet only triggers live verification and
  never authenticates a party. Account changes hide the old session while the new
  one is checked.
- **The UI is not authorization:** contracts and services still enforce permissions,
  collateral ownership and settlement rights.

**Status:**
- **Verified:** a real Loop devnet wallet connected, and the Canton pages loaded
  (12 November 2026).
- **Not verified:** a funded testnet balance read, a registry transfer, contract
  submission, and a live Console extension smoke test.
