import json
from typing import Optional, Dict, List, Union


def get_whitelist(file_path: str = "data/data.json") -> List[Dict[str, int]]:
    with open(file_path, "r") as f:
        whitelist = json.load(f)["whitelist"]
    return whitelist


def add_to_whitelist(user: Dict[str, int], file_path: str = "data/data.json") -> None:
    with open(file_path, "r") as f:
        data = json.load(f)
    data["whitelist"].append(user)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


def del_in_whitelist(id: int, file_path: str = "data/data.json") -> None:
    with open(file_path, "r") as f:
        data = json.load(f)
    data["whitelist"] = list(filter(lambda x: x["id"] != id, data["whitelist"]))
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
