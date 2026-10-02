"""Render original, exact labeled diagrams. Requires the Graphviz `dot` executable."""
from pathlib import Path
import shutil
import subprocess

P=Path(__file__).resolve().parent
BASE='''
graph [bgcolor="white", fontname="DejaVu Sans", fontsize=16, pad=0.28, nodesep=0.30, ranksep=0.46, compound=true];
node [shape=box, style="rounded,filled", fillcolor="#EFF6FB", color="#536C83", fontname="DejaVu Sans", fontsize=12, margin="0.16,0.13", penwidth=1.2];
edge [color="#536C83", fontname="DejaVu Sans", fontsize=10, arrowsize=0.75];
'''
SOURCES={
'01-model-and-system':r'''
digraph G { rankdir=TB;
LABEL_BASE
label="01  /  A model is one component of a serving system"; labelloc=t;
subgraph cluster_service {
  label="SERVICE RESPONSIBILITIES  /  conceptual boundaries, not process count"; color="#BACAD8"; style="rounded";
  api [label="API / request contract\nMessages, parameters, errors"];
  render [label="Prepare inputs\nTemplate • tokenizer • processor"];
  sched [label="Organize execution\nRequests • budgets • state ownership"];
  api -> render -> sched;
  subgraph cluster_model {
    label="NAIVE DECODER-ONLY MODEL  /  original lab simplification";
    color="#72ADA4"; bgcolor="#F5FBF9"; style="rounded";
    emb [label="IDs + positions → embeddings\n[B,T] → [B,T,D]",fillcolor="#E6F5EE"];
    attn [label="Causal Q/K/V attention\nFuture positions are masked",fillcolor="#E6F5EE"];
    mlp [label="Residuals + normalization + FFN\nRepeat decoder blocks",fillcolor="#E6F5EE"];
    logits [label="Vocabulary projection\nLogits [B,T,V]",fillcolor="#E6F5EE"];
    emb -> attn -> mlp -> logits;
  }
  select [label="Choose next token\nSampling policy + stop conditions"];
  output [label="Return the result\nDetokenize • format • stream"];
  sched -> emb [label="scheduled tensor work"];
  logits -> select [label="last relevant logits"];
  select -> output;
  select -> sched [label="continue with new token",style=dashed,constraint=false];
}
origin [shape=note,fillcolor="#FFF7E5",label="2017 Transformer: encoder + decoder + cross-attention.\nThis lab chooses a smaller decoder-only path.\nRandom-weight logits are not a language-quality result."];
output -> origin [style=invis];
}
''',
'02-request-boundaries':r'''
digraph G { rankdir=TB;
LABEL_BASE
label="02  /  Follow the request and the return path"; labelloc=t;
client [label="Client / application\nMay own conversation state and tool execution",fillcolor="#F1EFFA"];
subgraph cluster_front {
label="FRONTEND RESPONSIBILITIES";style="rounded";color="#BACAD8";
api [label="API router + serving adapter\nProtocol validation • task intent • cancellation"];
renderer [label="Renderer + modality processor\nTemplate • token IDs • tensors • metadata"];
input [label="Engine input processing / client\nTask limits • core request • transport"];
api -> renderer [label="messages / prompt / media"];
renderer -> input [label="model-consistent input representation"];
}
subgraph cluster_core {
label="ENGINE RESPONSIBILITIES";style="rounded";color="#72ADA4";bgcolor="#F5FBF9";
core [label="Engine core\nOrchestration",fillcolor="#E6F5EE"];
sched [label="Scheduler + cache management\nToken/encoder work • state availability",fillcolor="#E6F5EE"];
core -> sched [label="request progress + budgets"];
}
subgraph cluster_exec {
label="EXECUTION RESPONSIBILITIES  /  selection depends on configuration";style="rounded";color="#CDB794";
exec [label="Model executor / worker(s)\nPer-device or per-rank execution",fillcolor="#FFF7E5"];
runner [label="Selected model runner\nPersistent state → per-step inputs\nAttention/backend/graph helpers",fillcolor="#FFF7E5"];
model [label="Model-specific implementation\nVision tower where applicable • LLM layers",fillcolor="#FFF7E5"];
exec -> runner -> model;
}
post [label="Sampling or pooling + output handling\nTokens / vectors • finish metadata",fillcolor="#F1EFFA"];
derender [label="Derender / response formatting\nText • structured fields • stream events",fillcolor="#F1EFFA"];
client -> api; input -> core;
sched -> exec [label="scheduled work, not raw HTTP"];
model -> post [label="hidden states / logits"];
post -> core [style=dashed,label="execution progress",constraint=false];
post -> derender -> client [label="response",constraint=false];
{rank=same;client;derender;}
legend [shape=note,fillcolor="white",label="Logical map, not a universal call graph.\nA box need not be its own process.\nOffline and separated-render paths can enter differently."];
post -> legend [style=invis];
}
''',
'03-multimodal-path':r'''
digraph G {rankdir=TB;
LABEL_BASE
label="03  /  From media bytes to language-model state";labelloc=t;
bytes [label="Validated media input
Compressed bytes or a local image"];
pixels [label="Decode + model-specific preprocessing
Pixels / processor tensors"];
patch [label="Patch embedding + vision encoder
Bidirectional image representation",fillcolor="#E6F5EE"];
project [label="Learned projector / merger
Language-compatible features",fillcolor="#E6F5EE"];
tokens [label="Text-side contract
Rendered IDs • placeholders
Ordered item/grid metadata"];
merge [label="Aligned decoder input
Check feature count and positions",fillcolor="#FFF7E5"];
llm [label="Causal language-model computation
Contextual hidden states / KV",fillcolor="#FFF7E5"];
out [label="Logits → tokens → response"];
bytes -> pixels -> patch -> project -> merge -> llm -> out;
tokens -> merge;
pcache [shape=note,label="Processor-result cache",fillcolor="#F9F9F9"];
ecache [shape=note,label="Encoder-feature cache",fillcolor="#F9F9F9"];
kvcache [shape=note,label="Decoder prefix KV cache",fillcolor="#F9F9F9"];
pixels -> pcache [style=dashed,arrowhead=none];
project -> ecache [style=dashed,arrowhead=none];
llm -> kvcache [style=dashed,arrowhead=none];
{rank=same;pixels;pcache;}
{rank=same;tokens;project;ecache;}
{rank=same;llm;kvcache;}
note [shape=note,fillcolor="#F1EFFA",label="LLaVA-like teaching example, not every VLM.\nIdentity ≠ readiness ≠ ownership.\nThe CPU lab uses random weights: shapes, not image understanding."];
out -> note [style=invis];
}
''',
'04-placement':r'''
digraph G {rankdir=TB;
LABEL_BASE
label="04  /  Placement choices are not the same as model parallelism";labelloc=t;
subgraph cluster_a {
label="A  /  CO-LOCATED RESPONSIBILITIES";style="rounded";color="#BACAD8";
a [label="Render → Encode if needed → Prefill → Decode\nTransfers may remain within a process or host"];
}
subgraph cluster_b {
label="B  /  RENDERER SEPARATED";style="rounded";color="#72ADA4";
b1 [label="Render service(s)",fillcolor="#E6F5EE"];
b2 [label="Combined inference service\nE where needed + P + D"];
{rank=same;b1;b2;}
b1 -> b2 [label="IDs + parameters + MM payload / metadata"];
}
subgraph cluster_c {
label="C  /  FURTHER SEPARATION  —  model and connector support required";style="rounded";color="#CDB794";
r [label="R\nRender",fillcolor="#E6F5EE"];
e [label="E\nEncode",fillcolor="#E6F5EE"];
p [label="P\nPrefill",fillcolor="#FFF7E5"];
d [label="D\nDecode",fillcolor="#FFF7E5"];
{rank=same;r;e;p;d;}
r -> e [label="encoder input"];
e -> p [label="encoder features\n+ metadata"];
p -> d [label="decoder KV\n+ execution metadata"];
r -> p [label="rendered IDs / parameters / metadata",style=dashed,constraint=false];
}
legend [shape=note,fillcolor="#F1EFFA",label="R/E/P/D: where work stages are placed.\nTP/PP/DP/EP: tensor, pipeline, data and expert parallelism.\nThese are different axes and can be combined where supported.\nRenderer replicas handle requests; this does not imply distributed Jinja evaluation."];
a -> b1 [style=invis];a -> b2 [style=invis];b1 -> r [style=invis];b2 -> d [style=invis];p -> legend [style=invis];
}
'''
}

def main():
    dot=shutil.which('dot')
    if dot is None: raise SystemExit('Install Graphviz to regenerate diagrams')
    for name,source in SOURCES.items():
        path=P/(name+'.dot');path.write_text(source.replace('LABEL_BASE',BASE))
        for fmt in ['svg','png']:
            subprocess.run([dot,'-T'+fmt,str(path),'-o',str(P/(name+'.'+fmt))],check=True)
    print('Rendered',len(SOURCES),'original diagrams as SVG and PNG')

if __name__=='__main__':main()
