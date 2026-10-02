"""Capture only technical reproducibility fields, never the whole environment."""
import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
import platform
from pathlib import Path
import subprocess


def version(name):
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expect', choices=['cpu', 'cuda', 'rocm'])
    parser.add_argument('--source-dir', help='Optional vLLM git checkout; record exact HEAD')
    parser.add_argument('--output', default='results/environment.json')
    args = parser.parse_args()
    report = {'recorded_at':datetime.now(timezone.utc).isoformat(),
              'python':platform.python_version(), 'os':platform.platform(),
              'packages':{n:version(n) for n in ['vllm', 'torch', 'triton', 'aiter', 'transformers', 'pytest']},
              'gpu_runtime':'unknown', 'devices':[]}
    try:
        import torch
        report.update(torch_cuda_build=torch.version.cuda, torch_hip_build=torch.version.hip,
                      accelerator_available=torch.cuda.is_available())
        report['gpu_runtime'] = 'rocm' if torch.version.hip else ('cuda' if torch.version.cuda else 'cpu')
        for i in range(torch.cuda.device_count()):
            p = torch.cuda.get_device_properties(i)
            report['devices'].append({'index':i, 'name':p.name,
                                      'total_memory_bytes':p.total_memory,
                                      'gcn_arch':getattr(p, 'gcnArchName', None),
                                      'capability':list(torch.cuda.get_device_capability(i))})
    except ImportError:
        report['torch_error'] = 'PyTorch is not installed'
    if args.source_dir:
        try:
            report['vllm_source_commit'] = subprocess.check_output(
                ['git', '-C', args.source_dir, 'rev-parse', 'HEAD'], text=True, timeout=10).strip()
            report['vllm_source_dirty'] = bool(subprocess.check_output(
                ['git', '-C', args.source_dir, 'status', '--porcelain'], text=True, timeout=10).strip())
        except (OSError, subprocess.SubprocessError) as exc:
            report['git_error'] = str(exc)
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    if args.expect and report['gpu_runtime'] != args.expect:
        parser.exit(2, f"Expected {args.expect}; detected {report['gpu_runtime']}. Check your wheel/image.\n")
    if args.expect in ('cuda', 'rocm') and not report.get('accelerator_available'):
        parser.exit(2, 'The requested runtime is installed but no usable accelerator is visible.\n')


if __name__ == '__main__':
    main()
