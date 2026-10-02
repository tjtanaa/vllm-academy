"""Run with python -m mini_vllm.demo; emits a scheduling trace, not a benchmark."""
import argparse
import json
from pathlib import Path
import torch
from .engine import Engine
from .model import TinyDecoder


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', choices=['cpu', 'cuda'], default='cpu', help='ROCm PyTorch also uses cuda')
    parser.add_argument('--output', default='results/toy-trace.json')
    args = parser.parse_args()
    if args.device == 'cuda' and not torch.cuda.is_available():
        parser.error('No CUDA/HIP device available')
    torch.set_num_threads(1)
    model = TinyDecoder().to(args.device)
    prompt = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    reference = model.generate_dense(prompt, 5)
    with Engine(model, token_budget=6, prefill_chunk=4) as engine:
        engine.add('cold', prompt, 5)
        engine.run()
        engine.add('warm', prompt, 5)
        engine.add('other', [9, 8, 7], 3)
        outputs = engine.run()
        assert outputs['cold'] == outputs['warm'] == reference
        report = {'device':args.device, 'torch':torch.__version__,
                  'kind':'educational trace, not a performance measurement',
                  'outputs':outputs, 'warm_reused_tokens':engine.requests['warm'].reused_tokens,
                  'trace':engine.trace}
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'outputs':outputs, 'warm_reused_tokens':report['warm_reused_tokens'],
                      'dense_reference_matches':True, 'trace_file':str(path)}, indent=2))


if __name__ == '__main__':
    main()
