# Q8 · 第一個 PR 任務：從 fork 到「Merged」，而且不當*那種*貢獻者

**需要：** Linux（macOS 只適合純文件修改，或改用 CPU 從原始碼建置）、git、Python 3.11+；只有當你的修改涉及 kernel 時才需要 GPU · **時間：** 2 小時的環境設定，加上 review 等待時間 · **單元：** E23、E24、E26 · **XP：** +75（PR 合併後還有 🏅 Merged 徽章）
**[English](Q8-first-pr-quest.md)**

一個每個版本都有 300 多位貢獻者的專案，維護者們非常忙。他們會合併那些小而精、有測試、說明清楚又確實有需要的 PR，其他的就會很快關掉。這個任務會帶你走一遍最容易被合併的路徑。

> ⚠️ **尚未經維護者驗證。** vLLM 的貢獻指南才是最終依據：https://docs.vllm.ai/en/latest/contributing/ 。如果這裡的內容跟指南有出入，一律以指南為準。

## 1. 挑選真正有人需要的工作

從 `good first issue` 標籤、新手任務看板，或是你在 Q1/Q7 自己遇到的 bug 開始。把每則留言都讀完，再用 issue 編號搜尋目前開啟的 PR，避免跟別人重工。確認沒問題後，留言說你想接這個任務。

```text
/gfi        ← in Discord: open good first issues, fetched live
https://github.com/orgs/vllm-project/projects/6
```

> ✅ **檢查點：** 你已經在某個 issue 底下，用 2–3 句話留言說明你的做法，而且目前沒有其他人針對它開 PR。

## 2. Fork、clone，並建立純 Python 的開發環境

如果只改 Python 程式碼，你不需要自己編譯 CUDA kernel：用預先編譯好的 wheel，就能直接修改 Python 然後執行。`VLLM_USE_PRECOMPILED=1` 會沿用 Linux 預先編譯好的 wheel，所以只適用於 Linux；macOS 請改照貢獻指南用 CPU 建置。

```bash
git clone https://github.com/<you>/vllm.git && cd vllm
git remote add upstream https://github.com/vllm-project/vllm.git && git fetch upstream
uv venv --python 3.12 && source .venv/bin/activate
VLLM_USE_PRECOMPILED=1 uv pip install -e .
```

> ✅ **檢查點：** 執行 `python -c "import vllm; print(vllm.__file__)"` 會印出一個位於你 clone 資料夾內的路徑。

## 3. 開啟 linter

vLLM 在 CI 裡會跑 pre-commit hook（格式化、程式碼檢查、型別檢查）。先在本機跑過一遍，可以省下一輪來回修改的時間。

```bash
uv pip install pre-commit && pre-commit install
pre-commit run --all-files --show-diff-on-failure | tail -5
```

> ✅ **檢查點：** 在乾淨的 checkout 上，這些 hook 都能順利執行並通過。

## 4. 先重現問題，再寫出會失敗的測試

動手修之前，先重現那個 bug，並把它寫成最小的、會失敗的測試。想找對應的測試檔案，可以搜尋你要修改的那個模組有哪些測試。

```bash
git switch -c fix/<short-name>
git grep -ln "<function or class you're changing>" -- tests | head
python -m pytest -q tests/<area>/test_<thing>.py -k <your_test>
```

> ✅ **檢查點：** 你新寫的測試，會因為 issue 裡描述的那個原因而失敗。現在就先 commit，這樣 reviewer 可以清楚看到修改前和修改後的差別。

## 5. 做出能通過測試的最小修改

盡量少改：不要順手重構，也不要重新排版跟這次修改無關的程式碼。先跑你自己的測試，再跑同一個測試檔裡的其他測試。

```bash
python -m pytest -q tests/<area>/test_<thing>.py
pre-commit run --files $(git diff --name-only upstream/main)
```

> ✅ **檢查點：** 你的測試和該檔案原本的測試都通過了，而且 diff 小到五分鐘就能 review 完。

## 6. 加上 DCO 簽署並開啟 PR

每個 commit 都需要一行 `Signed-off-by`（用 `-s`）。PR 標題前面要加上所屬領域的前綴，例如 `[Bugfix]`、`[Doc]`、`[Frontend]`、`[Core]`、`[Model]` 或 `[CI/Build]`。範本也要填完整：目的、測試計畫、測試結果，以及 `FIX #<issue>`。

```bash
git commit -s -m "[Bugfix] Fix <what> when <condition>"
git push -u origin fix/<short-name>
gh pr create --repo vllm-project/vllm --web   # opens the PR template in your browser
```

> ✅ **檢查點：** DCO 檢查是綠燈，而且你的描述裡附上了能證明修復有效的那行完整指令。

## 7. 專業地面對 review

每一則留言都要回覆；review 期間除非對方要求，否則請用追加 commit 的方式更新，不要用 force-push 蓋掉歷史紀錄。如果 CI 在你沒碰過的地方失敗，先確認 `main` 是不是本來就紅燈，再開始 debug。安靜了好幾天之後，禮貌地提醒一下是沒問題的，忙碌的維護者不是在忽略你。

```text
Thanks! Addressed in a1b2c3d: moved the check into _validate() and added a test for the empty case.
```

> ✅ **檢查點：** 每一個 review 討論串都已經解決或回覆。把你的 PR 連結貼到 `#show-your-work`，讓社群一起幫你加油。

## 8. 領取你的徽章，繼續前進

PR 合併之後，把連結貼到 Discord，版主就會頒發 🏅 **Merged** 徽章給你（+200 XP）。接著為你的作品集（E26）寫三句話，說說你學到了什麼，下次再挑一個稍微大一點的 issue 吧。

```text
Merged: vllm-project/vllm#NNNNN — [Bugfix] … (reproduced, tested, fixed; 14 lines)
```

> ✅ **檢查點：** 你的名字出現在 vLLM 的 commit 歷史裡。歡迎加入這個俱樂部！

## 別當*那種*貢獻者

- 別對別人已經認領的 issue 開 PR。
- 別提交你無法逐行解釋的 AI 生成修改。
- 別把修 bug 和重構混在同一個 PR，也別為了充實個人檔案而開 10 個修錯字的 PR。
- 別跟 CI 吵架：在本機重現它。
