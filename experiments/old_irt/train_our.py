import subset2evaluate.utils as utils
import torch
import torch.utils
import lightning as L
import argparse
from scalar import IRTModelScalar
from sklearn.model_selection import train_test_split

args = argparse.ArgumentParser()
args.add_argument("--metric", default="score")
args.add_argument("--train-size", type=float, default=0.9)
args.add_argument("--epochs", type=int, default=5000)
args.add_argument("--out", default="/dev/null")
args = args.parse_args()

# WMT: 1k items, 15 models
data_wmt = utils.load_data_wmt(normalize=True, binarize=False)
# data_wmt = utils.load_data_squad(n_items=10_000, n_models=15)

models = list(data_wmt[0]["scores"].keys())
model = IRTModelScalar(len(data_wmt), models)

data_loader = [
    ((sent_i, model_i), sent["scores"][model][args.metric])
    for sent_i, sent in enumerate(data_wmt)
    for model_i, model in enumerate(models)
]

# subsample training data
assert args.train_size > 0.0 and args.train_size <= 1.0
if args.train_size == 1.0:
    data_train = data_loader
    data_test = []
else:
    data_train, data_test = train_test_split(data_loader, random_state=0, train_size=args.train_size)

data_train = torch.utils.data.DataLoader(
    data_train,
    batch_size=len(data_train),
    num_workers=24,
    shuffle=True,
    # fully move to GPU
    pin_memory=True,
    # don't kill workers because that's our bottleneck
    persistent_workers=True,
)
data_test = torch.utils.data.DataLoader(
    data_test,
    batch_size=len(data_test),
    num_workers=24,
    shuffle=False,
    # fully move to GPU
    pin_memory=True,
    # don't kill workers because that's our bottleneck
    persistent_workers=True,
)

trainer = L.Trainer(
    max_epochs=args.epochs,
    log_every_n_steps=1,
    check_val_every_n_epoch=100,
    enable_checkpointing=False,
    logger=False,
)
trainer.fit(
    model=model,
    train_dataloaders=data_train,
    val_dataloaders=data_test,
)

model.save_irt_params(args.out)
