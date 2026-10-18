# Replaying this verification

Use the maintained repository entry point, from any checkout:

```sh
uv run --with playwright python docs/verify/rerun-ds-code-blocks.py --kind all --output /tmp/ds-code-blocks-replay
```

The output directory must be empty. It reads published source HTML, fragments and HTML paths relative to the selected repository, verifies their hashes, reconstructs verifier input layout only in scratch, and requires all current question IDs. It never reads the original RUN/stage paths and never overwrites approval evidence. Independent mode requires a C compiler; browser/all needs Playwright Chromium. Saved verify-code-blocks.py is archival input for this entry point and deliberately rejects zero source inputs. The archival replay script may also be used with explicit --repo.
