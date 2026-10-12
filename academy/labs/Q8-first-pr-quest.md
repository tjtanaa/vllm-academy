# Q8 · First PR Quest: from fork to "Merged" without being *that* contributor

**Needs:** Linux (macOS works for docs-only changes, or with a CPU source build), git, Python 3.11+; a GPU only if your change touches kernels · **Time:** 2 h of setup plus review time · **Episodes:** E23, E24, E26 · **XP:** +75 (and the 🏅 Merged badge when it lands)
**[繁體中文](Q8-first-pr-quest.zh-TW.md)**

Maintainers of a project with 300+ contributors per release are busy. They merge PRs that are small, tested, clearly explained and wanted, and they close the rest quickly. This quest walks the path that gets you merged.

> ⚠️ **Not yet validated by a maintainer.** vLLM's contributing guide is the source of truth: https://docs.vllm.ai/en/latest/contributing/ . If anything here disagrees with it, the guide wins.

## 1. Pick work that's actually wanted

Start from the `good first issue` label, the onboarding project board, or a bug you hit yourself in Q1/Q7. Read every comment, then search open PRs for the issue number so you don't duplicate someone. Then comment that you'd like to take it.

```text
/gfi        ← in Discord: open good first issues, fetched live
https://github.com/orgs/vllm-project/projects/6
```

> ✅ **Checkpoint:** you've commented on one issue with your plan in 2–3 sentences, and nobody else has an open PR for it.

## 2. Fork, clone and set up a Python-only dev install

For Python-only changes you don't need to compile CUDA kernels: `VLLM_USE_PRECOMPILED=1` reuses the prebuilt Linux wheel's compiled parts, so you can edit the Python and run it. On macOS, follow the CPU build in the contributing guide instead.

```bash
git clone https://github.com/<you>/vllm.git && cd vllm
git remote add upstream https://github.com/vllm-project/vllm.git && git fetch upstream
uv venv --python 3.12 && source .venv/bin/activate
VLLM_USE_PRECOMPILED=1 uv pip install -e .
```

> ✅ **Checkpoint:** `python -c "import vllm; print(vllm.__file__)"` prints a path inside your clone.

## 3. Turn on the linters

vLLM runs pre-commit hooks (formatting, linting, typing) in CI. Running them locally saves you a round trip.

```bash
uv pip install pre-commit && pre-commit install
pre-commit run --all-files --show-diff-on-failure | tail -5
```

> ✅ **Checkpoint:** the hooks run (and pass) on a clean checkout.

## 4. Reproduce, then write the failing test

Before you fix anything, reproduce the bug and capture it in the smallest test that fails. Find the right test file by searching for tests of the module you're touching.

```bash
git switch -c fix/<short-name>
git grep -ln "<function or class you're changing>" -- tests | head
python -m pytest -q tests/<area>/test_<thing>.py -k <your_test>
```

> ✅ **Checkpoint:** your new test fails for the reason described in the issue. Commit it now so reviewers can see the before and after.

## 5. Make the smallest fix that passes

Change as little as possible, with no drive-by refactors and no reformatting unrelated code. Run your test, then the surrounding test file.

```bash
python -m pytest -q tests/<area>/test_<thing>.py
pre-commit run --files $(git diff --name-only upstream/main)
```

> ✅ **Checkpoint:** your test and the file's existing tests pass, and the diff is small enough to review in five minutes.

## 6. Commit with a DCO sign-off and open the PR

Every commit needs a `Signed-off-by` line (`-s`). Prefix the PR title with its area, e.g. `[Bugfix]`, `[Doc]`, `[Frontend]`, `[Core]`, `[Model]` or `[CI/Build]`. Fill in the template: purpose, test plan, test results, and `FIX #<issue>`.

```bash
git commit -s -m "[Bugfix] Fix <what> when <condition>"
git push -u origin fix/<short-name>
gh pr create --repo vllm-project/vllm --web   # opens the PR template in your browser
```

> ✅ **Checkpoint:** the DCO check is green and your description includes the exact command that proves the fix.

## 7. Handle review like a pro

Reply to every comment and push follow-up commits rather than force-pushing over history mid-review, unless asked. If CI fails in an area you didn't touch, check whether `main` is red before you debug. After a few quiet days, a polite ping is fine. Busy maintainers are not ignoring you.

```text
Thanks! Addressed in a1b2c3d: moved the check into _validate() and added a test for the empty case.
```

> ✅ **Checkpoint:** every review thread is resolved or answered. Post your PR link in `#show-your-work` so the community can cheer it on.

## 8. Claim your badge and keep going

When it merges, post the link in Discord and a moderator grants the 🏅 **Merged** badge (+200 XP). Then write three sentences about what you learned for your portfolio (E26), and pick a slightly bigger issue next time.

```text
Merged: vllm-project/vllm#NNNNN — [Bugfix] … (reproduced, tested, fixed; 14 lines)
```

> ✅ **Checkpoint:** your name is in vLLM's commit history. Welcome to the club.

## Don't be *that* contributor

- Don't open a PR for an issue someone else already claimed.
- Don't ship AI-generated changes you can't explain line by line.
- Don't mix a fix with a refactor, or open 10 typo PRs to pad a profile.
- Don't argue with CI: reproduce it locally.
