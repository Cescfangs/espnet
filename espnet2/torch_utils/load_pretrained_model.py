from pathlib import Path
from typing import Any
from typing import Union

import torch
import torch.nn
import torch.optim


def load_pretrained_model(
    pretrain_path: Union[str, Path],
    model: torch.nn.Module,
    pretrain_key: str = None,
    map_location: str = "cpu",
    ignore_not_existing_keys: bool = True,
):
    """Load a model state and set it to the model.

    Examples:
        >>> load_pretrained_model("somewhere/model.pth", model)
        >>> load_pretrained_model("somewhere/encoder.pth", model, "encoder")
    """
    if pretrain_key is None:
        obj = model
        key_prefix = ""  
    else:

        def get_attr(obj: Any, key: str):
            """Get an nested attribute.

            >>> class A(torch.nn.Module):
            ...     def __init__(self):
            ...         super().__init__()
            ...         self.linear = torch.nn.Linear(10, 10)
            >>> a = A()
            >>> assert A.linear.weight is get_attr(A, 'linear.weight')

            """
            key_prefix = []
            if key.strip() == "":
                return obj
            for k in key.split("."):
                obj = getattr(obj, k)
                key_prefix.append(k)
            key_prefix = ".".join(key_prefix) + "."
            return obj, key_prefix

        obj, key_prefix = get_attr(model, pretrain_key)

    state_dict = obj.state_dict()
    pretrained_dict = torch.load(pretrain_path, map_location=map_location)
    if ignore_not_existing_keys:
        # Ignores the parameters not existing in the train-model
        pretrained_dict = {k: pretrained_dict[key_prefix + k] for k in state_dict if key_prefix + k in pretrained_dict}
    state_dict.update(pretrained_dict)
    obj.load_state_dict(state_dict)
