"""Inspect config without downloading weights or assuming a standard head_dim."""
import argparse
import json
from pathlib import Path

def audit(config: dict) -> dict:
    c=config.get('text_config',config)
    h=c.get('hidden_size'); heads=c.get('num_attention_heads')
    if type(h) is not int or type(heads) is not int or min(h,heads)<=0:
        raise ValueError('Missing positive hidden_size and num_attention_heads')
    explicit=c.get('head_dim')
    if explicit is None and h%heads:
        raise ValueError('Cannot infer head_dim')
    d=explicit if explicit is not None else h//heads
    kv=c.get('num_key_value_heads',heads)
    if type(d) is not int or type(kv) is not int or min(d,kv)<=0 or heads%kv:
        raise ValueError('Invalid head dimensions for this MHA/GQA inspector')
    return {'hidden_size':h,'query_heads':heads,'kv_heads':kv,'head_dim':d,
            'head_dim_source':'explicit' if explicit is not None else 'inferred',
            'q_projection_width':heads*d,'kv_projection_width':kv*d,
            'naive_division_would_match':h//heads==d,
            'model_type':c.get('model_type'),'rope_scaling':c.get('rope_scaling')}

def main():
    p=argparse.ArgumentParser(); p.add_argument('snapshot',type=Path)
    p.add_argument('--tokenize',action='store_true',help='Optional installed Transformers; local files only')
    a=p.parse_args(); result=audit(json.loads((a.snapshot/'config.json').read_text()))
    for name in ['tokenizer_config.json','generation_config.json']:
        path=a.snapshot/name
        result[name]={'present':path.exists()}
    if a.tokenize:
        from transformers import AutoTokenizer
        tok=AutoTokenizer.from_pretrained(str(a.snapshot),local_files_only=True,trust_remote_code=False)
        messages=[{'role':'user','content':'Explain KV caching.'}]
        ids=tok.apply_chat_template(messages,tokenize=True,add_generation_prompt=True,enable_thinking=False)
        result['rendered_token_count']=len(ids)
        result['rendered_ids']=ids
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
