# DF Large

**1.0.1** (`DF-PA21.2-1.0.1`) by **RUSSELL PHILIP SMITHSON**.

DF Large provides the `N_LARGE` classical VM node for the PA-LCTL distributed
fabric. It embeds the BOTTLE ROCKET 4.7.0 BR/1.1 VM, its columned LCTL compiler,
local adapters, conformance tests and historical evidence. This repository is
the separate delivery of the supplied `DF_Large` folder.

## Setup and verification

Use Python 3.10+ and install the declared NumPy dependency in a virtual environment:

```sh
python -m pip install --only-binary=:all: -r REQUIREMENTS.txt
python -B tools/validate_release.py
python -B adapter/dfabric/cli.py node-verify
```

The portable validator checks inventories, the payload pin, signing regressions
and compiler/static tests. Native checks additionally require a POSIX host with
a C11 compiler, GNU make, OpenSSL development headers/libcrypto and sha256sum.
The node verifier builds and tests a scratch copy, leaving the sealed release
files unchanged. Missing native prerequisites are explicitly SKIPPED.

On a Linux development host, run `python -B tools/validate_native.py` for VM
acceptance tests, AddressSanitizer/UndefinedBehaviorSanitizer checks and host I/O
regressions. CI exercises portable checks on Windows/Linux and native tests on Linux.

To build the local node for use, run `python -B adapter/dfabric/cli.py node-build`.
Build outputs go under the embedded VM's `.build` directory. The distribution
ships source and fixtures, with original machine-specific binaries excluded.
See the [historical assembly guide](README_START_HERE.md) for command examples.

## Security and scope

Host loading is bounded; malformed key arguments fail closed; key generation
creates owner-only files exclusively and refuses existing paths. Choose new paths
for both key files. A failed second-file write can leave the new private key at
its requested path; inspect the command result before using a pair.

Compiler signing completes before replacing an output image. Signing failures
preserve the prior image and do not publish unsigned fallback output. Generated
key material must never be committed. The explicitly named
`tests/keys/DEV_ONLY_DO_NOT_DEPLOY` key is a public test fixture, not a deployment key.

This is a local reference VM. Production trust provisioning, hardware/TPM/device
qualification, Windows native execution and cross-host federation require separate
validation. No physical quantum execution is claimed. Node-registry pins in other
DF repositories must be deliberately updated before binding this derived release.

## Provenance and license

The VM host, compiler and file adapter were hardened; original payload inventories
and per-file changes are retained under `provenance/`. Runtime ISA/ABI version labels
remain 4.7.0; the audited distribution version is 1.0.1. The pinned PA-LCTL reference
core is unchanged. In-package hashes detect drift, not independent authenticity.

See [AUDIT.md](AUDIT.md), [SECURITY.md](SECURITY.md), [LICENSE](LICENSE) and
[NOTICE](NOTICE). Copyright 2026 **RUSSELL PHILIP SMITHSON**, Apache License 2.0.
