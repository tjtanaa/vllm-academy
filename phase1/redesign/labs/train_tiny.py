"""Fit one synthetic periodic sequence. This is a training-mechanics lab."""
import json
import torch
from torch.nn import functional as F
from .naive_transformer import Config, NaiveDecoder

def run(steps: int = 50):
    if steps <= 0:
        raise ValueError('steps must be positive')
    torch.manual_seed(19)
    model = NaiveDecoder(Config(vocab=8,width=16,heads=2,layers=1,context=24))
    sequence = torch.tensor([[1,2,3,4]*5],dtype=torch.long)
    inputs, targets = sequence[:,:-1], sequence[:,1:]
    opt = torch.optim.AdamW(model.parameters(),lr=0.01)
    losses = []
    for _ in range(steps):
        opt.zero_grad(set_to_none=True)
        logits,_,_ = model(inputs)
        loss = F.cross_entropy(logits.reshape(-1,8),targets.reshape(-1))
        losses.append(float(loss.detach()))
        loss.backward(); opt.step()
    model.eval()
    with torch.inference_mode():
        after = float(F.cross_entropy(model(inputs)[0].reshape(-1,8),targets.reshape(-1)))
    return {'steps':steps,'initial_loss':losses[0],'final_training_loss':after,
            'inputs':inputs.tolist(),'shifted_targets':targets.tolist(),
            'interpretation':'memorizing a synthetic training sequence; not held-out generalization'}

if __name__ == '__main__':
    print(json.dumps(run(),indent=2))
