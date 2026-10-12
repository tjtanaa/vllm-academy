# vLLM Academy

**從零理解推論，親手打造 mini-vLLM，完成第一個有價值的 PR，並持續理解 vLLM 的演進。**

> 🎓 **全新：[vLLM Academy Quest（繁體中文）](academy/README.zh-TW.md)**：建立在本課程之上的社群版。28 集雙語短課程、9 個實作關卡（其中三個任何筆電都能用純 Python 跑）、面試準備、🔮 大膽預測法庭，以及會出題、打分、幫你升級的 [Discord 機器人](discord_bot/README.md)。60 秒上手：`python academy/labs/batching_arena.py`

本專案有三個階段：[Phase 1](phase1/README.md) 是穩定的入門課程；[Phase 2](phase2/README.md) 解釋各個已研究版本的抽象、最佳化方法與取捨；[Phase 3](phase3/README.md) 將重要的新 engine/core/runner 概念，逐步帶進易讀的教學引擎。

目前提供英文課程草稿、CPU 可執行的教學引擎、測試及 CUDA/ROCm 實驗腳本。GPU 腳本尚未附上實機驗證；歷代版本分析與後續引擎改版尚未完成。這一頁是繁體中文入口，不是完整翻譯，也不代表官方 vLLM 課程。

先閱讀 [英文首頁](README.md)、[課綱](SYLLABUS.md)、[實作里程碑](labs/MILESTONES.md) 與 [專案路線圖](ROADMAP.md)。執行 `python -m pytest -q` 和 `python -m mini_vllm.demo` 可測試教學實作。請依首頁建立獨立的 CPU 環境，不要直接覆蓋既有的 GPU 環境。

教學引擎的版本與上游 vLLM 版本分開管理，對應關係記錄於 [版本清單](versions/manifest.json)。CPU 測試通過不等於生產環境相容，也不等於 CUDA 與 ROCm 效能相同。
