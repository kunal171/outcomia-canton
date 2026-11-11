# Outcomia Canton

- Deliver in small commits on feature branches; close each milestone with a PR and merge.
- This repository targets Canton prediction markets only. No spot or Solana implementation.
- Reuse Outcomia's visual design and financial invariants, not its Solana transaction builders.
- The connected Console Wallet party and network determine session identity.
- Never treat a URL, localStorage value or remembered party as proof of a wallet connection.
- Do not copy secrets, private keys or deployment credentials from sibling projects.
- Read current Canton 3.x docs, installed SDK types and relevant Next.js guides before implementation.
- Keep copy short. No fake markets, prices or settlement presented as live.
- Checkpoint 1 is wallet connectivity and the gated workspace; implement contracts in subsequent PRs.
