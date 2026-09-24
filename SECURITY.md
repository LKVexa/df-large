# Security scope

Use dedicated state directories and keep source and executable files under trusted
local ownership. Integrity checks reject traversal, duplicate evidence and file
links; they assume the tree is not concurrently modified by an attacker.

Only explicitly labeled development fixtures are shipped. Never reuse test keys
or the fixture trust hierarchy for deployment. Native C tests and sanitizers are
regression evidence, not a formal proof of sandbox isolation or production readiness.
Signing uses a caller-selected trusted brctl executable; subprocess success and
image shape checks do not establish the signer's independent authenticity.

NumPy and OpenSSL are installed separately under their upstream licenses. Consult
their own security advisories when selecting a deployment environment. Report
reproducible repository issues to the GitHub owner without uploading private keys.
