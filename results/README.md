# Validation evidence

`cpu-test-log.txt`: actual local pytest output, 30 passed.

`environment.json`: actual CPU environment (Python 3.13.5, PyTorch 2.10.0+cpu); vLLM is not installed.

`toy-trace.json`: actual logical scheduling and prefix-reuse trace. It is not a GPU timing result or a production service trace.

`validation.json`: executed and unexecuted checks, source baseline and material status.

`course-check.json`: structure and local-link checks. External URLs were researched separately and may change.

Generated real-vLLM experiments should use separate run directories and preserve exact commands and raw outputs. No real-vLLM benchmark results were generated for this archive.

## Academy bootstrap

The seed records retain their original dates and describe the earlier package. `bootstrap-validation.json` and `bootstrap-test-log.txt` record the new local checks performed while preparing the vLLM Academy import. They do not report a GitHub Actions result or GPU execution.
