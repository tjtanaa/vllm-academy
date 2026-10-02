import json
from dataclasses import replace
import pytest
import torch
from labs.bigram import Bigram
from labs.naive_transformer import Config, NaiveDecoder
from labs.train_tiny import run
from labs.render_contract import Identity, render, accept, prefix_key
from labs.vision_path import patchify, fuse, demo as vision_demo
from labs.cache_lifecycle import Slot, identity
from labs.streaming import events
from labs.inspect_snapshot import audit

@pytest.fixture
def model():
    torch.manual_seed(2)
    return NaiveDecoder().eval()

@pytest.mark.parametrize('cut',[1,2,4,5])
def test_dense_and_cached_chunks_agree(model,cut):
    ids=torch.tensor([[1,3,5,7,2,4]])
    with torch.inference_mode():
        full,_,_=model(ids)
        _,past,_=model(ids[:,:cut])
        tail,_,trace=model(ids[:,cut:],past)
    torch.testing.assert_close(tail,full[:,cut:],atol=2e-6,rtol=2e-5)
    assert trace['layers'][0]['offset']==cut

@pytest.mark.parametrize('cut',[1,3,5])
def test_future_tokens_cannot_change_past_logits(model,cut):
    ids=torch.tensor([[1,3,5,7,2,4]])
    other=ids.clone();other[:,cut:]=9
    torch.testing.assert_close(model(ids)[0][:,:cut],model(other)[0][:,:cut])

@pytest.mark.parametrize('count',[1,3,5])
def test_greedy_cached_and_recompute_agree(model,count):
    ids=torch.tensor([[1,2,3]])
    assert torch.equal(model.generate(ids,count),model.generate(ids,count,cached=False))

@pytest.mark.parametrize('ids',[torch.tensor([[99]]),torch.tensor([[1.0]]),torch.empty(1,0,dtype=torch.long)])
def test_invalid_tokens_rejected(model,ids):
    with pytest.raises(ValueError): model(ids)

def test_inconsistent_layer_cache_rejected(model):
    _,past,_=model(torch.tensor([[1,2]]))
    past[1]=(past[1][0][:,:,:1],past[1][1][:,:,:1])
    with pytest.raises(ValueError): model(torch.tensor([[3]]),past)

def test_context_limit(model):
    with pytest.raises(ValueError):model(torch.ones(1,65,dtype=torch.long))

def test_train_on_shifted_targets():
    result=run(30)
    assert result['final_training_loss']<result['initial_loss']*.4
    assert result['inputs'][0][1:]==result['shifted_targets'][0][:-1]

def test_bigram_information_loss():
    m=Bigram([['cat','likes','fish'],['dog','likes','food']])
    assert m.predict(['cat','likes'])==m.predict(['dog','likes'])
    assert abs(sum(m.predict(['unseen']).values())-1)<1e-6

@pytest.fixture
def ident(): return Identity('m1','t1','chat-v1','p1','tenant-A')

def test_render_roundtrip(ident):
    original=render([{'role':'user','content':'Hello, 世界'}],ident)
    wire=json.loads(json.dumps(original))
    assert accept(wire,ident)==original['token_ids']

@pytest.mark.parametrize('field',['model','tokenizer','template','processor','tenant'])
def test_revision_or_tenant_mismatch(ident,field):
    record=render([{'role':'user','content':'hello'}],ident)
    with pytest.raises(ValueError):accept(record,replace(ident,**{field:'different'}))

def test_role_changes_serialization(ident):
    a=render([{'role':'user','content':'hello'}],ident)
    b=render([{'role':'assistant','content':'hello'}],ident)
    assert a['token_ids']!=b['token_ids']
    assert prefix_key(a)!=prefix_key(b)

def test_message_order_changes_serialization(ident):
    msgs=[{'role':'system','content':'a'},{'role':'user','content':'b'}]
    assert render(msgs,ident)!=render(msgs[::-1],ident)

def test_nontext_input_not_silently_ignored(ident):
    with pytest.raises(ValueError):render([{'role':'user','content':[{'type':'image'}]}],ident)

def test_patch_order():
    image=torch.arange(16).reshape(1,1,4,4)
    assert patchify(image,2).tolist()==[[[0,1,4,5],[2,3,6,7],[8,9,12,13],[10,11,14,15]]]

@pytest.mark.parametrize('indices',[[1],[1,1],[1,9]])
def test_placeholder_contract(indices):
    with pytest.raises(ValueError):fuse(torch.zeros(1,5,3),torch.ones(1,2,3),indices)

def test_fusion_preserves_other_positions():
    text=torch.zeros(1,5,3)
    result=fuse(text,torch.ones(1,2,3),[1,3])
    assert result[:,[0,2,4]].sum()==0
    assert result[:,[1,3]].sum()==6
    assert text.sum()==0

def test_complete_synthetic_vision_path():
    d=vision_demo()
    assert d['projected']==[1,4,24] and d['llm_logits']==[1,9,32]

def test_load_is_not_ready():
    s=Slot()
    with pytest.raises(RuntimeError):s.acquire()
    with pytest.raises(RuntimeError):s.recycle()

def test_reader_prevents_recycle():
    s=Slot();s.ready();s.acquire();s.acquire();s.release()
    with pytest.raises(RuntimeError):s.recycle()
    s.release();s.recycle();assert s.state=='recycled'
    with pytest.raises(RuntimeError):s.acquire()

def test_reference_underflow():
    with pytest.raises(RuntimeError):Slot().release()

def test_cache_stage_and_context_are_identity():
    assert identity('processor',b'x',revision='1')!=identity('encoder',b'x',revision='1')
    assert identity('kv',b'x',prefix='a')!=identity('kv',b'x',prefix='b')
    assert identity('encoder',b'x',revision='1')!=identity('encoder',b'y',revision='1')

@pytest.mark.parametrize('chunk_size',[1,2,3,7,100])
def test_sse_chunking_and_utf8(chunk_size):
    raw=':keep-alive\r\n\r\ndata: 你好\r\n\r\ndata: [DONE]\n\n'.encode()
    assert events([raw[i:i+chunk_size] for i in range(0,len(raw),chunk_size)])==['你好','[DONE]']

def test_incomplete_stream_is_not_success():
    with pytest.raises(ValueError):events([b'data: partial\n'])

def test_qwen_explicit_head_dimension():
    example={'hidden_size':1024,'num_attention_heads':16,'num_key_value_heads':8,'head_dim':128}
    d=audit(example)
    assert d['q_projection_width']==2048
    assert d['kv_projection_width']==1024
    assert not d['naive_division_would_match']

def test_inferred_head_dimension():
    assert audit({'hidden_size':32,'num_attention_heads':4})['head_dim']==8
