# Security Policy

This repository contains lab scenarios and injected demonstrations. The default
examples must still avoid mutating production services, but they may emulate
rollback, drift or external data downloads inside an isolated environment.

If you find a vulnerability, exposed secret, unsafe command, or a scenario that
can accidentally escape an isolated environment and affect real infrastructure,
report it through GitHub Security Advisories or by opening an issue without
including exploit details or secret values.

When reporting a possible secret, include only the file path, commit, and a
redacted prefix/suffix. Treat any real secret as compromised until rotated.
