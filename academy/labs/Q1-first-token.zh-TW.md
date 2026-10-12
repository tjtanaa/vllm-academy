# Q1 · 第一個 Token：15 分鐘架好你自己的 vLLM 伺服器

**需要：** 免費的 Google Colab GPU，或任何已安裝 vLLM 的 NVIDIA/AMD GPU · **時間：** 15 分鐘 · **單元：** E01、E02、E28 · **XP：** +75
**[English](Q1-first-token.md)**

做完這個實驗，你會擁有一台可以直接使用的 OpenAI 相容伺服器，親眼看著 token 一個一個冒出來，還會知道啟動記錄（log）裡把 KV cache 大小藏在哪一行。

> ⚠️ **尚未由維護者在 Colab 上驗證過。** vLLM 更新非常快，如果某個步驟失敗了，請把 `server.log` 的最後 20 行貼到 `#labs-help`。完全沒有 GPU 嗎？先去做 Q2–Q4 吧，它們在任何筆電上都能執行。

## 1. 準備一張 GPU

在 Colab 裡，打開 **Runtime → Change runtime type → T4 GPU**，然後執行下面這個儲存格。如果用自己的電腦，直接在終端機執行即可。

```bash
!nvidia-smi --query-gpu=name,memory.total,compute_cap --format=csv
```

> ✅ **檢查點：** 你會看到一張 GPU 和它的記憶體大小，例如 `Tesla T4, 15360 MiB, 7.5`。T4 不支援 BF16，所以後面我們會加上 `--dtype half`。

## 2. 安裝 vLLM

這一步會下載好幾 GB 的 wheel 套件，大約需要 3–5 分鐘。建議使用全新的執行環境（runtime）。

```bash
!pip install -q vllm openai
!python -c "import vllm; print('vLLM', vllm.__version__)"
```

> ✅ **檢查點：** 畫面會印出版本號，例如 `vLLM 0.31.0`。記得寫下來，因為你之後的實驗結果會跟版本有關。

## 3. 啟動伺服器並計時

我們選用 Qwen3-0.6B，因為它小到幾乎哪裡都跑得動。伺服器會在背景執行，並把輸出寫進 `server.log`。請記下開始的時間：E28 就是在講為什麼啟動需要這麼久。

```bash
!date +%T && nohup vllm serve Qwen/Qwen3-0.6B --dtype half --max-model-len 4096 --gpu-memory-utilization 0.85 > server.log 2>&1 &
!sleep 90; grep -E "KV cache|startup complete|Error" server.log | tail -5; date +%T
```

> ✅ **檢查點：** log 裡出現 `Application startup complete`，以及一行標示 GPU KV cache 大小（以 token 為單位）的訊息。把那個數字和啟動花了幾秒都記下來。如果兩個都沒看到，再等 30 秒後重新執行一次 `grep`。

## 4. 送出第一個請求

這台伺服器說的是 OpenAI API，所以任何 OpenAI 用戶端都能直接連。我們先從最單純的 `curl` 開始。Qwen3 預設會先「思考」一大段，所以我們把 thinking 關掉，直接拿到簡短的回答。

```bash
!curl -s localhost:8000/v1/chat/completions -H 'Content-Type: application/json' -d '{"model":"Qwen/Qwen3-0.6B","messages":[{"role":"user","content":"In one sentence, what is vLLM?"}],"max_tokens":60,"chat_template_kwargs":{"enable_thinking":false}}' | python -m json.tool | head -30
```

> ✅ **檢查點：** 你會拿到一份 JSON，裡面有 `choices[0].message.content`，還有一個 `usage` 區塊，記錄了 `prompt_tokens` 和 `completion_tokens` 的數量。

## 5. 看 token 一個一個流出來（E01）

ChatGPT 說穿了就是一個 for 迴圈：跑一次 forward pass，吐出一個 token。串流（streaming）可以讓這件事變得肉眼可見。下面的程式會印出每個 token 抵達的時間，讓你直接看到首個 token 時間（TTFT）和 token 之間的間隔（ITL）。

```python
import time
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8000/v1", api_key="none")
t0 = last = time.perf_counter()
stream = client.chat.completions.create(model="Qwen/Qwen3-0.6B", stream=True, max_tokens=40,
    messages=[{"role": "user", "content": "Count from 1 to 10 in English."}],
    extra_body={"chat_template_kwargs": {"enable_thinking": False}})  # Qwen3 "thinks" by default
for i, chunk in enumerate(stream):
    now = time.perf_counter()
    text = chunk.choices[0].delta.content or ""
    print(f"{(now - t0) * 1000:7.1f} ms  (+{(now - last) * 1000:5.1f})  {text!r}")
    last = now
```

> ✅ **檢查點：** 第一行的時間就是你的 TTFT。後面每一行的 `+` 間隔應該很小而且很穩定，那就是 decode。請把你的 TTFT 和典型間隔貼到 `#show-your-work`。

## 6. Tokenizer 遊樂場（E02）

模型從來沒看過「字母」。來比較一下，同一個意思用英文和中文表達，各自要花多少 token。

```python
from transformers import AutoTokenizer
tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
for s in ["How many r's are in strawberry?", "strawberry 裡有幾個 r？", "推論引擎決定了你的帳單。", "The inference engine decides your bill."]:
    ids = tok.encode(s)
    print(len(ids), [tok.decode([i]) for i in ids])
```

> ✅ **檢查點：** 你可以看出「strawberry」並不是被拆成一個個字母，也能解釋為什麼模型可能會數錯 r 的數量。

## 7. 偷看一下 metrics

正式環境的工程師天天都在看 `/metrics`（Prometheus 格式）。先多送幾個請求，再來看看引擎回報了哪些關於執行中請求、KV 使用量和 prefix caching 的資料。

```bash
!curl -s localhost:8000/metrics | grep -E "^vllm:(num_requests|kv_cache_usage|prefix_cache|prompt_tokens|generation_tokens)" | head -20
```

> ✅ **檢查點：** 你會看到一些 `vllm:` 開頭的 metrics，而且 token 計數器的值不是 0。找找看哪一個指標告訴你 KV cache 用了多滿。

## 8. 暖啟動重來一次，比較差異（E28）

把伺服器關掉，再用同樣的指令啟動一次。第二次啟動會重複使用 torch.compile 的快取，權重檔案也很可能還留在作業系統的檔案快取裡。

```bash
!pkill -f "vllm serve"; sleep 5; date +%T
!nohup vllm serve Qwen/Qwen3-0.6B --dtype half --max-model-len 4096 --gpu-memory-utilization 0.85 > server2.log 2>&1 &
!sleep 60; grep -E "startup complete|compile|graph" server2.log | tail -5; date +%T
```

> ✅ **檢查點：** 暖啟動明顯比步驟 3 快。你能說出哪些階段變便宜了、為什麼：權重直接從本機的 Hugging Face 快取讀取，不用再下載；torch.compile 也重複使用了它的快取。CUDA graph 擷取不會被快取，所以還是會再跑一次。

## 學到了什麼

- 只要一行指令，vLLM 就能給你一台 OpenAI 相容的伺服器。
- 輸出是一步一個 token：TTFT 由 prefill 決定，token 之間的間隔則由 decode 決定。
- 啟動 log 會告訴你實際拿到多少 KV cache（E07 會帶你算這筆帳）。
- 啟動本身也分成好幾個階段，而且值得量測（E28）。

**下一步：** E03 會帶你蓋出剛剛跟你對話的那個 Transformer。想繼續動手玩？Q2 會讓你看到 KV cache 內部長什麼樣子。
