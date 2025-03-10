import torch
import torch.utils
from base import IRTModelBase


class IRTModelScalar(IRTModelBase):
    def __init__(self, data, models, **kwargs):
        super().__init__(models=models, **kwargs)

        # normally distribute at the beginning
        # discrimination
        self.param_disc = torch.nn.Parameter(torch.randn(len(data)))
        # difficulty
        self.param_diff = torch.nn.Parameter(torch.randn(len(data)))
        # feasability
        self.param_feas = torch.nn.Parameter(torch.randn(len(data)))

        self.clamp_feas = True

    def get_irt_params(self, i_item, name):
        if name == "disc":
            return self.param_disc[i_item]
        elif name == "diff":
            return self.param_diff[i_item]
        elif name == "feas":
            return self.param_feas[i_item]

    def pack_irt_params_items(self):
        return [
            {
                "disc": disc.item(),
                "diff": diff.item(),
                "feas": feas.item(),
            }
            for disc, diff, feas in zip(self.param_disc, self.param_diff, self.param_feas)
        ]

    def load_irt_params(self, params):
        self.models = torch.nn.Parameter(torch.Tensor(params["models"]))
        self.param_disc = torch.nn.Parameter(torch.Tensor(params["items"]["disc"]))
        self.param_diff = torch.nn.Parameter(torch.Tensor(params["items"]["diff"]))
        self.param_feas = torch.nn.Parameter(torch.Tensor(params["items"]["feas"]))
