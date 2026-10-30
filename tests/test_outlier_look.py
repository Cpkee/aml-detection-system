"""The guard on the outlier appendix's one look (src/evaluation/outlier_look.py): it runs only once, only after the
settings are frozen and committed, and only while the code and model files still equal the frozen ones. No data
needed: the folder, the current settings and git are replaced by fakes."""
import json

import pytest

from evaluation import outlier_look

FROZEN = {"outlier": {"top_k": 3}, "models": {"bank_label": {"lgbm.txt": "abc"}}}


@pytest.fixture
def setup(tmp_path, monkeypatch):
    monkeypatch.setattr(outlier_look, "folder", lambda out: str(tmp_path))
    monkeypatch.setattr(outlier_look, "current", lambda out: dict(FROZEN))
    committed = {"yes": True}
    monkeypatch.setattr(outlier_look.manifest, "_git",
                        lambda *a: ("" if committed["yes"] else None) if a[0] in ("ls-files", "status") else "c0ffee")
    (tmp_path / "settings.json").write_text(json.dumps({**FROZEN, "frozen": "2026-11-03 10:00"}))
    return tmp_path, committed, monkeypatch


def test_allowed_when_frozen_committed_and_unchanged(setup):
    assert outlier_look.problems("data/x") == []


def test_refused_without_settings(setup):
    tmp_path, _, _ = setup
    (tmp_path / "settings.json").unlink()
    assert "freeze the settings first" in outlier_look.problems("data/x")[0]


def test_refused_when_not_committed(setup):
    _, committed, _ = setup
    committed["yes"] = False
    assert any("not committed" in p for p in outlier_look.problems("data/x"))


def test_refused_when_settings_or_models_changed(setup):
    _, _, monkeypatch = setup
    monkeypatch.setattr(outlier_look, "current", lambda out: {**FROZEN, "models": {"bank_label": {"lgbm.txt": "new"}}})
    assert outlier_look.problems("data/x") == ["`models` differs from the frozen settings"]


@pytest.mark.parametrize("marker", ["LOOK_STARTED.json", "LOOK.json"])
def test_runs_once(setup, marker):
    tmp_path, _, _ = setup
    (tmp_path / marker).write_text("{}")
    assert any("runs once" in p for p in outlier_look.problems("data/x"))
    with pytest.raises(SystemExit, match="not allowed"):
        outlier_look.look("data/x")


def test_freeze_only_once(setup):
    with pytest.raises(SystemExit, match="frozen once"):
        outlier_look.freeze("data/x")
