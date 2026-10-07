"""Every setting in configs/sim.yaml must either be read by the simulator or be listed in NOT_READ.

A setting the code ignores is a trap: changing it (or a sensitivity run using its `test` values) does nothing.
"""
import pathlib
import yaml

from sim.config import NOT_READ

ROOT = pathlib.Path(__file__).resolve().parents[1]
# config.py is left out: it names settings in NOT_READ without reading them
CODE = {p.name: p.read_text() for p in (ROOT / "src" / "sim").glob("*.py") if p.name != "config.py"}


def _settings(node, path=()):
    if isinstance(node, dict) and "value" not in node:
        for k, v in node.items():
            yield from _settings(v, path + (k,))
    else:
        yield ".".join(path)


def _is_read(key: str) -> bool:
    if any(f'"{key}"' in text or f"'{key}'" in text for text in CODE.values()):
        return True
    section, _, name = key.partition(".")
    # rules.py reads its settings through g("name") = cfg.get(f"rules.{name}")
    return section == "rules" and f'g("{name}")' in CODE["rules.py"]


def test_every_setting_is_read_or_listed():
    cfg = yaml.safe_load((ROOT / "configs" / "sim.yaml").read_text())
    unread = [k for k in _settings(cfg) if not _is_read(k) and k not in NOT_READ]
    assert not unread, f"settings the code never reads (read them or add to NOT_READ): {unread}"


def test_not_read_list_is_current():
    cfg = yaml.safe_load((ROOT / "configs" / "sim.yaml").read_text())
    keys = set(_settings(cfg))
    stale = [k for k in NOT_READ if k not in keys or _is_read(k)]
    assert not stale, f"NOT_READ entries that no longer exist or are now read: {stale}"
