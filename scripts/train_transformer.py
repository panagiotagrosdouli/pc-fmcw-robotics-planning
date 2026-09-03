"""Train the uncertainty-aware Transformer on CMHT trajectory windows."""

import argparse
import sys
from pathlib import Path
import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from iscai.data.cmht_loader import extract_object_positions
from iscai.prediction.trajectory_dataset import make_windows
from iscai.prediction.transformer import TrajectoryTransformer, gaussian_nll


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--labels", type=Path, required=True)
    p.add_argument("--history", type=int, default=8)
    p.add_argument("--horizon", type=int, default=12)
    p.add_argument("--epochs", type=int, default=30)
    p.add_argument("--batch-size", type=int, default=128)
    p.add_argument("--lr", type=float, default=2e-4)
    p.add_argument("--output", type=Path, default=Path("artifacts/trajectory_transformer.pt"))
    args = p.parse_args()

    samples = make_windows(extract_object_positions(args.labels), args.history, args.horizon)
    ids = np.unique([s["object_id"] for s in samples])
    if len(ids) < 2:
        raise RuntimeError("Need at least two object IDs")
    split = max(1, int(.8 * len(ids)))
    train_ids = set(ids[:split])
    train = [s for s in samples if s["object_id"] in train_ids]
    test = [s for s in samples if s["object_id"] not in train_ids]
    if not test:
        raise RuntimeError("Object-disjoint test split is empty")

    X = torch.tensor(np.stack([s["history"] for s in train]), dtype=torch.float32)
    Y = torch.tensor(np.stack([s["future"] for s in train]), dtype=torch.float32)
    loader = DataLoader(TensorDataset(X, Y), batch_size=args.batch_size, shuffle=True)
    model = TrajectoryTransformer(horizon=args.horizon)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)

    model.train()
    for epoch in range(args.epochs):
        total = 0.0
        for history, future in loader:
            target_delta = future - history[:, -1:, :]
            mean, log_sigma = model(history)
            loss = gaussian_nll(mean, target_delta, log_sigma)
            opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
            total += float(loss) * len(history)
        print(f"epoch={epoch+1:03d} train_nll={total/len(loader.dataset):.6f}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"state_dict": model.state_dict(), "history": args.history, "horizon": args.horizon}, args.output)
    print(f"saved={args.output} train_windows={len(train)} test_windows={len(test)}")


if __name__ == "__main__":
    main()
