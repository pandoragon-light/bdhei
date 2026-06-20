# Release Checklist

Use this checklist before uploading the project to GitHub.

- [ ] Confirm the paper citation in `CITATION.cff` matches the final Springer metadata.
- [ ] Keep only example data that can be shared publicly.
- [ ] Run the example CSV command from `examples/README.md`.
- [ ] Run the single-station regression check against private legacy reference data.
- [ ] Run the full directory comparison against private legacy reference outputs.
- [ ] Confirm the maximum regression difference is acceptable and documented.
- [ ] Confirm `.deps/`, `output/`, `local/`, and generated workbooks are not committed.
- [ ] Confirm the public README does not contain private machine paths.
- [ ] Run `python tools\preflight_release.py` and confirm it passes.
- [ ] If Git is initialized, confirm `git add --dry-run .` only lists the preflight files.
- [ ] Decide whether the first GitHub release should be tagged `v0.1.0`.
