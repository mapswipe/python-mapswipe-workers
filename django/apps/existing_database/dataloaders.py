from typing import List
from collections import defaultdict

from asgiref.sync import sync_to_async
from strawberry.dataloader import DataLoader


def load_data(keys: List[int]):
    # TODO: Dummy data loader remove this.
    _map = defaultdict(int)
    return [_map[key] for key in keys]


class ExistingDatabaseDataLoader():
    load_data = DataLoader(load_fn=sync_to_async(load_data))
