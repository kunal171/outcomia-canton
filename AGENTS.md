# Outcomia Canton

- Deliver in small commits on feature branches; close each milestone with a PR and merge.
- This repository targets Canton prediction markets only. No spot or Solana implementation.
- The single frontend lives in `kunal171/outcomia/app`; add Canton UI there. Do not scaffold another app here.
- Keep contracts and UI in sync: every contract feature ships with its matching UI feature in the shared app, in the same milestone. A milestone is not complete until both sides are done and tested.
- Reuse financial invariants, not Solana transaction builders. This repository owns only Canton contracts, services and their documentation.
- The connected Loop or Console Wallet party and network determine session identity.
- Wallet integration always follows CIP-0103 (Canton dApp Standard): use the wallet's standard provider (`request`/`on`), `prepareExecute` with `txChanged` for submission, `ledgerApi` for reads and the standard error codes. Adapt vendor SDKs behind that provider instead of calling their own methods.
- Never treat a URL, localStorage value or remembered party as proof of a wallet connection.
- Do not copy secrets, private keys or deployment credentials from sibling projects.
- Read current Canton 3.x docs, installed SDK types and relevant Next.js guides before implementation.
- Keep copy short. No fake markets, prices or settlement presented as live.
- Binary lifecycle contracts are in `contracts/main`; their separate tests are in `contracts/test`. Run `make test` before merging contract changes.
- The shared UI must keep Canton trading disabled until contracts, wallet submission and network deployment are verified.
