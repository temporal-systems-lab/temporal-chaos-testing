# Contributing

Contributions should keep the repository explicit about isolation requirements.

- Document whether a scenario is safe-lab, lab-only or lab-download.
- Prefer injected clocks, `libfaketime`, containers or disposable VMs to any
  direct mutation of the host clock.
- Keep destructive host-level procedures out of the default path.
- Add tests for rollback, forward jumps, suspend/resume assumptions and missing
  optional dependencies.
- Do not commit generated artifacts, downloaded kernels, `__pycache__`, logs,
  secrets or local machine paths.

Before opening a pull request:

```bash
make verify
```
