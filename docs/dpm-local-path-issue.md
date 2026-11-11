# DPM local DAR path issue

## Observed failure

The installed DPM reports
`1.1.1-snapshot-20261102.208.0.v13b5087`; the SDK is 3.7.1 with compiler 3.7.0.
On Linux, a local `data-dependencies` entry in a checkout containing spaces is
resolved as an escaped URL path:

```text
expected: /.../New Volume2/Rust learnings/.../outcomia-markets-0.1.0.dar
actual:   /.../New%20Volume2/Rust%20learnings/.../outcomia-markets-0.1.0.dar
```

The actual DAR exists. `dpm build --all` fails because the compiler tries to open
the escaped filename. A separate `--enable-multi-package=no` build reproduces it.
This is different from running `--package-root` outside a package, which is
already discussed in [DPM issue 12](https://github.com/digital-asset/dpm/issues/12).

## Minimal reproduction

Run with the installed SDK; use a fresh destination:

```bash
mkdir -p 'target/repro with spaces'
dpm new 'target/repro with spaces/example' --template skeleton
cd 'target/repro with spaces/example'
dpm build --all
```

The generated skeleton already has separate main/test packages and a local DAR
dependency. No Outcomia contracts or credentials are needed to reproduce this.

## Source and candidate

The public source is [digital-asset/dpm](https://github.com/digital-asset/dpm).
The investigation starts from upstream commit `79bf2d7`.

- `pkg/damlpackage/locations.go` parses a filesystem path as a URL string. Literal
  `%`, `#` and `?` can be interpreted as URI syntax instead of filename characters.
- `pkg/resolver/deepresolver.go` calls `URL.String()` and strips `file://`, leaving
  percent-encoded spaces/Unicode in the path passed to the compiler.

The candidate constructs the file URL from its path field and returns decoded
filesystem paths for local dependencies. It keeps builtin dependency handling
separate and retains compatibility with drive-prefixed and UNC-shaped URLs.

The sibling checkout `../dpm-upstream` contains the focused branch
`fix/local-dar-filesystem-paths` at commit `12879cb`. The [portable patch](../tools/patches/dpm-local-dar-paths.patch)
is included for reproducibility. Regression tests fail before the fix and pass
after it. The complete parser/resolver package tests pass. The same locally built
candidate allows this project's normal multi-package build in its existing path.

The full upstream Go suite still fails `TestComponentDependencyPaths` and
`TestDpmAddGitDarCommand` in this path with spaces. Both failures also reproduce
on unchanged upstream `79bf2d7`; they are not reported as passing or fixed by
this patch. Other package suites, including the Git puller, pass.

The reproduction is published as [upstream issue #340](https://github.com/digital-asset/dpm/issues/340),
with the candidate fix in [PR #341](https://github.com/digital-asset/dpm/pull/341)
from [kunal171/dpm](https://github.com/kunal171/dpm). The fresh SDK skeleton fails
with the original binary and builds with the candidate, independently of Outcomia
source. Cached builds can hide this failure; always use a fresh reproduction.

## Local use

The candidate executable is in ignored `target/tools/dpm`. The installed SDK and
DPM were not replaced. Pass it explicitly:

```bash
make DPM="$PWD/target/tools/dpm" test
```

To reproduce in a **fresh** sibling checkout, using Go 1.26.10:

```bash
# From outcomia-canton; choose a destination that does not already exist.
git clone https://github.com/digital-asset/dpm.git ../dpm-path-review
git -C ../dpm-path-review checkout 79bf2d7
git -C ../dpm-path-review apply "$PWD/tools/patches/dpm-local-dar-paths.patch"
mkdir -p target/tools
outcomia_root="$PWD"
(cd ../dpm-path-review && go build -o "$outcomia_root/target/tools/dpm" ./cmd/dpm)
make DPM="$PWD/target/tools/dpm" test
```

Keep the source revision, patch and test results with any report.
This is a temporary local tool override, not a new Outcomia runtime dependency.
