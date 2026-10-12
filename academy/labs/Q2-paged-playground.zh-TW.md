# Q2 · Paged Playground：親眼看看 PagedAttention 的記憶體妙招

**需要：** 只要 Python 3.10+（不需要 GPU、PyTorch，也不用 pip install） · **時間：** 15 分鐘 · **單元：** E08、E10、E21、E27 · **XP：** +75
**[English](Q2-paged-playground.md)**

vLLM 的核心創意，是把 KV cache 存成一塊塊固定大小的 **block**（分頁），而不是替每個請求配置一大塊連續的記憶體。這個想法一次帶來四個好處：更少的浪費、請求之間可以共用、prefix caching，以及 offloading。這個實驗會把這四件事全部動畫化給你看。

> 這個 playground 是 vLLM KV cache 管理器的教學模型。為了讓你看清楚每一個格子，它用 4 個 token 當一個 block；vLLM 的預設值是 16。下面所有數字都來自預設的執行結果，所以你跑出來的應該會一模一樣。

## 1. 執行基本情境

在 repo 的根目錄執行：

```bash
python academy/labs/paged_playground.py
```

> ✅ **檢查點：** Result 區塊顯示，22 個已儲存的 token 只用了 **24 paged slots**（浪費 8%），而以最大長度 32 預留連續空間的做法要 **64 slots**（浪費 66%）。

## 2. 讀懂 block table

往上捲到兩個請求都 decode 完之後的那個畫面。A 的 block table 是 `[0, 1, 4]`：它的邏輯 block 0、1、2 分別放在實體 block 0、1 和 4。實體記憶體不是連續的，也不需要連續。Attention kernel 會照著表去找資料，就像作業系統照著 page table 去找分頁一樣。

```text
A block table → [0, 1, 4]  (12 tokens, last block 4/4 full)
B block table → [2, 3, 5]  (10 tokens, last block 2/4 full)
```

> ✅ **檢查點：** 你可以解釋，為什麼一個請求最多只會浪費一個沒填滿的 block（`block_size - 1` 個格子）。

## 3. 共用 system prompt

兩場對話都以同一段 12 個 token 的 system prompt 開頭，剛好是 3 個完整的 block。

```bash
python academy/labs/paged_playground.py --scenario prefix
```

> ✅ **檢查點：** B 進來時顯示 `3 block(s) HIT on GPU`，格子圖上出現 `[A2]`（reference count 為 2），Result 則顯示 **24 prompt tokens reused**。就算 A 和 B 都結束了，C 還是能重複使用這些 block。

## 4. 像菜鳥一樣把快取搞壞

正式環境裡有個經典錯誤：把時間戳記或請求 ID 放在 prompt 的**最前面**。Block 的 hash 是鏈式的（每個 block 的 hash 都包含它前一個 block 的 hash），所以只要第一個 token 不一樣，後面所有的 hash 就全部跟著變。

```bash
python academy/labs/paged_playground.py --scenario prefix --break-prefix
```

> ✅ **檢查點：** 結果是 **0 tokens reused**，並且重新計算了 54 個 token。請寫一句話貼到 `#show-your-work`，說說動態內容應該放在 prompt 的哪個位置。

## 5. 記憶體吃緊時的 offload

GPU 只有 8 個 block。新的請求會依照 LRU 的順序把快取中的 block 踢出去；有 CPU 這一層的話，被踢出的 block 會先被複製出去，而不是直接丟掉。

```bash
python academy/labs/paged_playground.py --scenario offload
```

> ✅ **檢查點：** A2 進來時顯示 `1 block(s) HIT on GPU, 3 block(s) LOADED from CPU`。Result 顯示 **6 blocks offloaded** 以及 **12 tokens loaded back**，也就是這些 token 是被載回來的，不用重新計算。

## 6. 重播一場 agent 對話（E27）

Agent 每一輪都會把完整的歷史紀錄重送一次，而在兩輪之間，其他使用者會不斷把快取沖刷掉。針對同一場對話，比較開啟和關閉 offload 的差別：

```bash
python academy/labs/paged_playground.py --scenario agent
```

> ✅ **檢查點：** 最後的表格顯示，開啟 offload 時計算了 **74** 個 prefill token，關閉時則是 **214** 個。第 4 輪只需要重算 9 個 token，而不是 73 個。

## 7. 轉動旋鈕

真正的 vLLM 使用 16 個 token 的 block。用更大的 block 重跑基本情境，看看浪費比例怎麼變化。接著再給 agent 情境更多的 GPU 記憶體。

```bash
python academy/labs/paged_playground.py --block-size 16
python academy/labs/paged_playground.py --scenario agent --gpu-blocks 40
```

> ✅ **檢查點：** 用 16 個 token 的 block 時，paged 的浪費上升到 **31%**。你能說明其中的取捨：block 越大，metadata 越少、kernel 效率越好，但內部浪費越多，prefix 比對的粒度也越粗。

## 8. 在真正的 vLLM 裡找到它

在 Discord 裡執行 `/code`，打開 KV cache 那一區：`kv_cache_manager`、`block_pool`、`free_queue` 和 `prefix_hash`。每個項目都是一條 permalink，直接連到固定版本的 vLLM commit。接著用 `/hunt` 挑戰 H3–H5 這幾個尋寶任務。

```text
/code entry:block_pool
/hunt hunt:H5
```

> ✅ **檢查點：** 你能說出 vLLM 裡哪個 class 扮演的是這個 playground 裡 `PagedKV.free` 的角色（這就是尋寶任務 H5）。

## 學到了什麼

- 分頁讓每個請求的 KV 浪費不到一個 block，所以能同時塞進更多請求。
- 填滿的 block 會得到鏈式 hash；相同的 prefix 透過 reference count 共用實體 block。
- 釋放掉的 block 在被踢出之前都還留在快取裡（LRU），這就是 prefix caching 會是「免費加速」的原因。
- Offloading 把一次踢出變成一次便宜的複製，而不是一次昂貴的重算，其中最受惠的就是 agent。
