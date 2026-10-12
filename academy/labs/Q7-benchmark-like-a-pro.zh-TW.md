# Q7 · 像職業玩家一樣做 Benchmark：TTFT、ITL，以及「平均值」的謊言

**需要：** 一張安裝好 vLLM 的 GPU（建議 24 GB 以上） · **時間：** 45 分鐘 · **單元：** E17、E24 · **XP：** +75
**[English](Q7-benchmark-like-a-pro.md)**

「快 2 倍」如果沒有說明工作負載（workload）、基準線（baseline）和百分位數，其實什麼都不代表。這個實驗會帶你做一次誠實的 A/B 實驗：prefix caching 關閉 vs. 開啟，然後用效能工程師的寫法把結果整理成報告。這種報告就是作品集的好素材，也是拿到面試機會的敲門磚。

> ⚠️ **尚未經維護者驗證。** 不同版本的 vLLM 參數常常會變，請先用 `vllm bench serve --help` 確認你這個版本支援哪些旗標。請務必記下你的 vLLM 版本、GPU、驅動程式版本和完整指令，少了這些，數字就沒有任何意義。

## 1. 先寫下你的假設

測之前，先決定你預期會看到什麼。我們的工作負載是：200 個請求，每個請求有 1,536 個 token 的共用前綴（shared prefix），加上 512 個各自獨有的 token，輸出 128 個 token，速率為每秒 8 個請求。

```text
Hypothesis: with prefix caching ON, TTFT p50 and p99 drop sharply because 75% of every prompt is reused;
output throughput rises modestly; median ITL barely changes (decode work is the same), but p99 ITL may
drop because smaller prefill chunks share steps with decode.
```

> ✅ **檢查點：** 你的假設要寫清楚是哪個指標、往哪個方向變，還有*為什麼*。請從 vllm-academy repo 複製 `templates/EXPERIMENT_REPORT.md`，把假設貼進去。

## 2. 記錄執行環境

沒辦法描述的環境，就沒辦法重現結果。

```bash
python -c "import vllm, torch; print('vllm', vllm.__version__, 'torch', torch.__version__)"
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv  # or: rocm-smi --showproductname
```

> ✅ **檢查點：** 版本資訊和 GPU 型號都已經貼進你的報告。

## 3. 實驗 A：關閉 prefix caching

先把伺服器以關閉快取的方式啟動，再從第二個終端機執行 benchmark。請固定亂數種子（seed），這樣兩次實驗送出的 prompt 才會完全相同。

```bash
vllm serve Qwen/Qwen3-8B --no-enable-prefix-caching --max-model-len 4096 --port 8000
# second terminal:
vllm bench serve --model Qwen/Qwen3-8B --dataset-name random --random-prefix-len 1536 --random-input-len 512 --random-output-len 128 --num-prompts 200 --request-rate 8 --seed 0 --percentile-metrics ttft,tpot,itl,e2el --metric-percentiles 50,90,99 --save-result --result-filename off.json
```

> ✅ **檢查點：** `off.json` 已經產生，而且終端機顯示了 TTFT、TPOT、ITL 的 p50、p90、p99，以及輸出 token 的 throughput。

## 4. 實驗 B：開啟 prefix caching

**一定要重啟伺服器。** 不然實驗 A 留下來的快取會汙染實驗 B 的結果。Prefix caching 預設就是開啟的。

```bash
vllm serve Qwen/Qwen3-8B --max-model-len 4096 --port 8000
# second terminal: same bench command, different file name
vllm bench serve --model Qwen/Qwen3-8B --dataset-name random --random-prefix-len 1536 --random-input-len 512 --random-output-len 128 --num-prompts 200 --request-rate 8 --seed 0 --percentile-metrics ttft,tpot,itl,e2el --metric-percentiles 50,90,99 --save-result --result-filename on.json
```

> ✅ **檢查點：** `on.json` 已經產生。再看一眼 `/metrics` 裡 prefix cache 的命中（hit）計數器，確認快取真的有發揮作用。

## 5. 像職業玩家一樣比較結果

把兩次結果的差異並排印出來。要看百分位數，不要只看平均值；如果時間允許，每組實驗各跑 3 次，這樣你才知道自己的雜訊（noise）有多大。每次重跑前都要重啟伺服器（或換一個 `--seed`），不然第二次會連整段 prompt 都命中快取，把進步幅度灌水。

```python
import json
a, b = json.load(open("off.json")), json.load(open("on.json"))
for k in ["output_throughput", "p50_ttft_ms", "p99_ttft_ms", "p50_itl_ms", "p99_itl_ms"]:
    if k in a and k in b:
        print(f"{k:<20} off={a[k]:>9.1f}  on={b[k]:>9.1f}  change={100 * (b[k] - a[k]) / a[k]:+6.1f}%")
```

> ✅ **檢查點：** 你手上有一張變化幅度的表格。TTFT 的變化方向跟你預測的一樣嗎？如果 ITL 變動很大，你能解釋為什麼嗎？

## 6. 試著推翻自己的結論

一個你推不倒的結論，才值得信任。這次只改**一個**變因：把共用前綴降到 0，或是把請求速率加倍，然後觀察哪個指標有動、哪個沒動。兩台伺服器（快取關閉與開啟，中間記得重啟）都要跑一次。

```bash
vllm bench serve --model Qwen/Qwen3-8B --dataset-name random --random-prefix-len 0 --random-input-len 2048 --random-output-len 128 --num-prompts 200 --request-rate 8 --seed 0 --save-result --result-filename noprefix.json
```

> ✅ **檢查點：** 沒有共用前綴時，開啟快取不會讓 TTFT 變好，這就證明先前的進步來自「重複利用」，而不是隨機雜訊。

## 7. 加分題：speculative decoding（E17）

改用 n-gram drafter 重啟伺服器（不需要額外的模型），重跑 benchmark，然後比較 ITL 和 throughput。隨機 token 組成的 prompt 幾乎讓 n-gram 比對無從發揮，請說明為什麼這樣的測試並不公平，以及什麼樣的工作負載才算公平（例如程式碼編輯、RAG）。

```bash
vllm serve Qwen/Qwen3-8B --max-model-len 4096 --speculative-config '{"method": "ngram", "num_speculative_tokens": 4, "prompt_lookup_max": 4}'
```

> ✅ **檢查點：** 你能用自己跑出來的數字當證據，說明為什麼加速幅度取決於接受率（acceptance rate）和工作負載。

## 8. 發表你的報告

把範本填完整：假設、環境、完整指令、原始 JSON、比較表、一張圖表、讓你意外的發現，以及可能影響結論的因素（threats to validity）。把它貼到 `#show-your-work`，也可以放到 Gist 或寫成部落格文章，然後把連結放進你的履歷（E26）。

```text
Title: Prefix caching on Qwen3-8B: TTFT p99 −X% on a 75%-shared-prefix workload (vLLM 0.31, 1× <GPU>)
```

> ✅ **檢查點：** 社群裡的其他人只要照著你報告裡的指令，就能完整重現你的實驗。

## 學到了什麼

- 先寫假設，一次只改一個變因，每次實驗之間要重啟，種子要固定。
- 百分位數（p50/p99）才是真正說故事的指標；平均值會把使用者真正感受到的長尾藏起來。
- 每個「加速」都綁著一個工作負載。講清楚是哪一種，否則這個說法就毫無意義。
