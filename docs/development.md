# Development

## Build and test

DPM SDK 3.7.1, Java 17+ and Python 3.10+.

```bash
make deps    # fetch and verify the pinned Token Standard interface DARs
make build   # production and test DARs
make test    # Daml Script suite on the IDE ledger
python3 scripts/generate-fee-vectors.py --check
```

Only the production DAR is deployable. The test DAR adds `daml-script` and a test
token registry, which also injects faults (short outputs, failed transfers) to
check rollbacks.

- **Suite size:** 253 Daml scripts passed as of 2026-11-27.
- **Message limit:** the test package raises the script-service message limit to
  32 MiB, because the 128-order capacity test returns a large history. This is a
  test transport setting, not a ledger limit.

**What the tests cover:**
- **Covered:** every money-moving choice is checked against actual holdings, so
  exact cash conservation, replay, stale IDs, authorization and registry rollback.
- **Not covered:** multi-participant behaviour, public-network throughput, live
  registries and wallet signing.

## Dependencies

[`contracts/deps`](../contracts/deps/README.md) pins three official Splice Token
Standard interface DARs by commit and SHA-256: metadata, Holding V2 and
TransferInstruction V2. They are used as published, never rebuilt, because
rebuilding would change their package IDs.

## Checkouts with spaces in the path

DPM 3.7.1 URL-encodes local DAR paths, so `make build` fails when the checkout
path contains spaces: for example, it looks for `Rust%20learnings/...` instead of
`Rust learnings/...`. This is fixed upstream in
[digital-asset/dpm#341](https://github.com/digital-asset/dpm/pull/341), merged on
2026-11-13, but not yet in the installed SDK. Until a release includes it, either
use a path without spaces or build the patched DPM once:

```bash
git clone https://github.com/digital-asset/dpm.git ../dpm-path-review
git -C ../dpm-path-review checkout 79bf2d7
git -C ../dpm-path-review apply "$PWD/tools/patches/dpm-local-dar-paths.patch"
mkdir -p target/tools
(cd ../dpm-path-review && go build -o "$OLDPWD/target/tools/dpm" ./cmd/dpm)
make DPM="$PWD/target/tools/dpm" test
```

This is a local tool override, not a runtime dependency.

## Working rules

See [AGENTS.md](../AGENTS.md):
- **Branches:** small commits on feature branches, merged by PR.
- **Contract and UI together:** each contract feature ships with its UI in the
  shared app.
- **Wallets:** wallet flows follow CIP-0103.
- **Trading gate:** Canton trading stays disabled in the UI until deployment is
  verified.
