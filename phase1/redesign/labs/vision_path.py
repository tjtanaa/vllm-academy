"""Random-weight ViT/projector shape lab; not a trained VLM or mini-vLLM feature."""
import json
import torch
from torch import nn

def patchify(image: torch.Tensor, patch: int) -> torch.Tensor:
    if image.ndim != 4 or patch <= 0:
        raise ValueError('Expected [batch,channels,height,width] and positive patch size')
    b,c,h,w=image.shape
    if h%patch or w%patch:
        raise ValueError('Use dimensions divisible by patch size in this lab')
    return (image.unfold(2,patch,patch).unfold(3,patch,patch)
            .permute(0,2,3,1,4,5).contiguous().reshape(b,(h//patch)*(w//patch),c*patch*patch))

class TinyVision(nn.Module):
    def __init__(self, patch=4, vision_width=12, text_width=24, num_patches=4):
        super().__init__()
        self.patch=patch
        self.patch_embed=nn.Linear(3*patch*patch,vision_width)
        self.position=nn.Parameter(torch.zeros(1,num_patches,vision_width))
        self.encoder=nn.TransformerEncoderLayer(vision_width,3,4*vision_width,
            dropout=0.0,batch_first=True,norm_first=True)
        self.projector=nn.Linear(vision_width,text_width)
    def forward(self,image):
        patches=patchify(image,self.patch)
        if patches.shape[1] != self.position.shape[1]:
            raise ValueError('This synthetic model has a fixed patch grid')
        embedded=self.patch_embed(patches)+self.position
        # Bidirectional image self-attention; no language causal mask here.
        features=self.encoder(embedded)
        return self.projector(features), {'patch_vectors':list(patches.shape),
                'vision_features':list(features.shape)}

def fuse(text_embeddings: torch.Tensor, image_features: torch.Tensor,
         placeholder_indices: list[int]) -> torch.Tensor:
    if text_embeddings.ndim!=3 or image_features.ndim!=3:
        raise ValueError('Expected batched sequences of embeddings')
    if (text_embeddings.shape[0],text_embeddings.shape[2]) != (image_features.shape[0],image_features.shape[2]):
        raise ValueError('Batch/embedding width mismatch')
    if len(placeholder_indices)!=image_features.shape[1] or len(set(placeholder_indices))!=len(placeholder_indices):
        raise ValueError('One distinct placeholder per feature is required')
    if any(type(i) is not int or i<0 or i>=text_embeddings.shape[1] for i in placeholder_indices):
        raise ValueError('Invalid placeholder position')
    out=text_embeddings.clone()
    out[:,placeholder_indices,:]=image_features
    return out

def demo():
    torch.manual_seed(11)
    model=TinyVision().eval()
    image=torch.arange(192,dtype=torch.float32).reshape(1,3,8,8)/191
    with torch.inference_mode():
        features,trace=model(image)
        text=torch.randn(1,9,24)
        merged=fuse(text,features,[2,3,4,5])
        # A standalone causal decoder block consumes this embedding sequence.
        decoder=nn.TransformerEncoderLayer(24,3,48,dropout=0.0,batch_first=True).eval()
        causal=torch.ones(9,9,dtype=torch.bool).triu(1)
        hidden=decoder(merged,src_mask=causal)
        logits=nn.Linear(24,32)(hidden)
    return {'image':list(image.shape),**trace,'projected':list(features.shape),
            'llm_embeddings':list(merged.shape),'llm_logits':list(logits.shape),
            'scope':'synthetic tensors and random weights; no semantic image understanding'}

if __name__=='__main__':
    print(json.dumps(demo(),indent=2))
