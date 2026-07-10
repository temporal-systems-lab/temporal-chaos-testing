# Release Checklist

## Before External Review

- [ ] CI passes on the release branch.
- [ ] Isolation prerequisites are explicit in `README.md` and scenario docs.
- [ ] No generated artifacts or downloaded kernels are tracked.
- [ ] No local paths, secrets or private endpoints are present.
- [ ] Scope still matches chaos/spatial lab only: no read-only audit duplicate, no pedagogical core duplicate.

## Before Public Announcement

- [ ] Tag matches the corresponding book edition across the three repositories.
- [ ] Changelog entry is complete.
- [ ] Security policy and contribution rules are visible.
- [ ] Release notes state clearly which scenarios require optional dependencies or downloads.