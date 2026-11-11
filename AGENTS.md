# Outcomia Canton

- Deliver in small commits on feature branches; close each milestone with a PR and merge.
- This repository targets Canton prediction markets only. No spot or Solana implementation.
- The single frontend lives in `kunal171/outcomia/app`; add Canton UI there. Do not scaffold another app here.
- Reuse financial invariants, not Solana transaction builders. This repository owns only Canton contracts, services and their documentation.
- The connected Console Wallet party and network determine session identity.
- Never treat a URL, localStorage value or remembered party as proof of a wallet connection.
- Do not copy secrets, private keys or deployment credentials from sibling projects.
- Read current Canton 3.x docs, installed SDK types and relevant Next.js guides before implementation.
- Keep copy short. No fake markets, prices or settlement presented as live.
- Checkpoint 1 is wallet connectivity and the gated workspace; implement contracts in subsequent PRs.
