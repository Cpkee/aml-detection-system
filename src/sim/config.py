"""Load configs/sim.yaml and expose plain values.

Every setting in the YAML is a dict with a `value` key (plus source/strength/test).
`Cfg.get("normal.card_per_month")` returns just the value.
"""
from __future__ import annotations
import copy
import yaml


class Cfg:
    def __init__(self, path: str, overrides: dict | None = None):
        with open(path) as f:
            self.raw = yaml.safe_load(f)
        for key, val in (overrides or {}).items():
            self.set(key, val)

    def _node(self, dotted: str):
        node = self.raw
        for part in dotted.split("."):
            node = node[part]
        return node

    def get(self, dotted: str):
        node = self._node(dotted)
        if isinstance(node, dict) and "value" in node:
            return copy.deepcopy(node["value"])
        return copy.deepcopy(node)

    def set(self, dotted: str, value):
        parts = dotted.split(".")
        node = self.raw
        for part in parts[:-1]:
            node = node[part]
        leaf = node[parts[-1]]
        if isinstance(leaf, dict) and "value" in leaf:
            leaf["value"] = value
        else:
            node[parts[-1]] = value
