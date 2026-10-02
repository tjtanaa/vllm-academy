# Validation and limits

The standalone CPU suite completed with **44 passing tests**. All seven self-contained demo commands completed, and Python compilation plus both optional tools' help commands completed. Exact commands, package versions, elapsed times and source hashes are recorded in [results/validation.json](results/validation.json); raw outputs are adjacent.

Tests cover future-token invariance, dense/cached chunk agreement, cached/recomputed greedy generation, malformed input, a synthetic training loop, rendering identity and roundtrip behavior, patch ordering, placeholder alignment, vision/decoder shape flow, cache readiness/lifetime, arbitrary UTF-8/SSE chunk boundaries, and explicit head-dimension handling.

The tiny training result measures only fit to a synthetic training sequence. The vision result uses random weights. The rendering and lifetime examples are local mechanism tests, not deployed services. The test count is specific to this supplement, not a new total for Academy main.

Actual Llama/Qwen checkpoint execution, native-patch integration, real-tokenizer loading, GPU correctness/performance, distributed transport, full production tracing and instructional pilot review were **not performed**. The local source reader was compiled and its help command run; its checked-out-source path was not exercised because that checkout is not available in this runtime.

The four SVG/PNG figures were rendered and visually inspected. Documentation links and HTML internal anchors are checked by the packaging script; external source availability is not guaranteed by that local check.

A Chromium screenshot attempt was blocked by its local-file navigation policy. The handbook received static content/link checks, not a completed browser visual check. The diagrams were inspected separately as rendered PNGs.

## Publication recheck

The publication preparation independently reran the standalone suite: **44 tests passed**. Python compilation, the seven self-contained demos and the local handbook/link checks also passed. Fresh evidence is in [results/publish-validation.json](results/publish-validation.json). Original preparation records are retained separately. The hosted workflow status must be read from GitHub Actions; no GPU or actual checkpoint run is inferred from these CPU checks.
