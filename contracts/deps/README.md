# Token Standard dependencies

`token-standard.lock.json` pins three official Splice interface DARs by source
commit and SHA-256. `make deps` downloads them into ignored `target/deps/` and
checks every file. A valid cache works offline. Failed downloads cannot replace
cached files.

These are the published interface artifacts, not copies rebuilt with our SDK.
Rebuilding them could change their package IDs and break compatibility with
registry contracts. The production package imports the metadata, Holding V2 and
TransferInstruction V2 interfaces. It contains no test token implementation.

Source: [canton-network/splice at c961df87](https://github.com/canton-network/splice/tree/c961df87ba6943a8647911e7911f010938bfdd0b/token-standard).
License: [Apache 2.0](LICENSE-Splice.txt), copyright Digital Asset (Switzerland) GmbH
and/or its affiliates. Keep the license with redistributed contract artifacts.

A dependency update must review the source, hashes and interface compatibility.
The lockfile does not establish that a particular live asset registry supports
these interfaces; that requires a separate integration check.
