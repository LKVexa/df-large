# DF Large 1.0.1 audit

Work was performed in a separate copy of the supplied DF_Large folder.

## Repairs

- Reused the verified shared-manifest hardening after confirming the original
  adapter files matched DF Fabric: canonical contained paths, no links/reparse
  points, nonempty evidence, strict hashes/counts and duplicate rejection.
- Bounded host image/key reads to the VM's update ceiling, limited reads to
  regular files and cleaned allocations on malformed inputs. Fixed double fclose
  after buffered write failure. Key creation now refuses existing paths and opens
  files with mode 0600; secret cleanup uses OPENSSL_cleanse.
- Explicit invalid trust keys now stop recovery/serve instead of falling back.
  APDU text parsing requires both characters of each byte to be hexadecimal.
- Closed file descriptors if fdopen fails and on truncated monotonic-state reads.
  Production source remains 60,986 bytes, below the strict 61,000-byte boundary.
- Signed compilation uses temporary staging, a timeout and signed-image shape
  validation before replacing an existing image. Failed or malformed signer
  output leaves the previous image intact.
- Fixed Python executable selection, UTF-8 and LF handling in compiler tests;
  shell sanitizer dispatch works without executable bits in a Windows ZIP.
- Quarantined original .build outputs outside the release. Refreshed payload
  and root inventories, retaining original inventory evidence and a change map.
  Added Apache-2.0 LICENSE/NOTICE and README under RUSSELL PHILIP SMITHSON.

## Validation scope

Local Python 3.12: 15 integrity/signing regressions (14 pass; one filesystem-link
creation case skipped because the Windows account lacks the privilege), plus
19 compiler semantic checks, two expression tests and 14 device/static checks.
The original Windows expression test exposed canonical-LF handling before repair.

Native Linux CI builds the VM with its warning-as-error flags, executes its
acceptance gate and adapter battery, checks the source size, runs ASan/UBSan,
and exercises new host I/O regressions with leak detection. Review the actual
workflow result for native outcomes; the local host has no C toolchain.

The ISA/ABI and pinned PA-LCTL reference core are unchanged. Historical package
evidence is retained as history, not asserted as newly obtained certification.
Physical devices, hardware trust anchors, real key ceremonies, native Windows
execution and cross-host federation remain outside this release's validation.
Hashes provide integrity only within a stable trusted local filesystem.
