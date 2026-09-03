import pytest
torch=pytest.importorskip('torch')
from iscai.prediction.transformer import TrajectoryTransformer

def test_transformer_is_translation_invariant_in_eval_mode():
 torch.manual_seed(0); model=TrajectoryTransformer(d_model=16,nhead=4,layers=1,horizon=3).eval(); h=torch.randn(2,5,2); shift=torch.tensor([[[100.,-37.]]])
 with torch.no_grad():
  m1,s1=model(h); m2,s2=model(h+shift)
 assert torch.allclose(m1,m2,atol=1e-5,rtol=1e-5)
 assert torch.allclose(s1,s2,atol=1e-5,rtol=1e-5)

def test_transformer_rejects_bad_history_shape():
 model=TrajectoryTransformer(d_model=16,nhead=4,layers=1,horizon=3)
 with pytest.raises(ValueError): model(torch.randn(5,2))
