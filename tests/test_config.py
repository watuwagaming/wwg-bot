"""Tests for config.py — BotConfig loading, getting, setting."""

import json
import asyncio
from pathlib import Path

import pytest

from config import BotConfig, DEFAULT_SETTINGS


@pytest.fixture
def tmp_config(tmp_path):
    """Create a BotConfig using a temp file."""
    cfg_path = tmp_path / "config.json"
    cfg = BotConfig(path=str(cfg_path))
    cfg.load()
    return cfg, cfg_path


class TestBotConfigLoad:
    def test_load_creates_file(self, tmp_config):
        cfg, path = tmp_config
        assert path.exists()

    def test_load_seeds_defaults(self, tmp_config):
        cfg, path = tmp_config
        for key, default_val, *_ in DEFAULT_SETTINGS:
            assert cfg.get(key) == default_val, f"Default missing for {key}"

    def test_load_preserves_saved_values(self, tmp_path):
        cfg_path = tmp_path / "config.json"
        # Write a custom value
        cfg_path.write_text(json.dumps({"feature.gn_police.enabled": False}))
        cfg = BotConfig(path=str(cfg_path))
        cfg.load()
        assert cfg.get("feature.gn_police.enabled") is False

    def test_load_adds_new_defaults_to_existing_file(self, tmp_path):
        cfg_path = tmp_path / "config.json"
        cfg_path.write_text(json.dumps({"custom_key": 42}))
        cfg = BotConfig(path=str(cfg_path))
        cfg.load()
        # custom_key preserved
        assert cfg.get("custom_key") == 42
        # defaults also present
        assert cfg.get("feature.troll_loop.enabled") is True


class TestBotConfigGet:
    def test_get_existing_key(self, tmp_config):
        cfg, _ = tmp_config
        assert cfg.get("feature.troll_loop.enabled") is True

    def test_get_missing_key_returns_default(self, tmp_config):
        cfg, _ = tmp_config
        assert cfg.get("nonexistent.key", "fallback") == "fallback"

    def test_get_missing_key_returns_none(self, tmp_config):
        cfg, _ = tmp_config
        assert cfg.get("nonexistent.key") is None


class TestBotConfigSet:
    def test_set_updates_in_memory(self, tmp_config):
        cfg, _ = tmp_config
        asyncio.get_event_loop().run_until_complete(cfg.set("feature.gn_police.enabled", False))
        assert cfg.get("feature.gn_police.enabled") is False

    def test_set_persists_to_file(self, tmp_config):
        cfg, path = tmp_config
        asyncio.get_event_loop().run_until_complete(cfg.set("feature.gn_police.chance", 0.99))
        data = json.loads(path.read_text())
        assert data["feature.gn_police.chance"] == 0.99


class TestBotConfigGrouped:
    def test_get_all_grouped_returns_categories(self, tmp_config):
        cfg, _ = tmp_config
        grouped = cfg.get_all_grouped()
        assert isinstance(grouped, dict)
        assert "GN Police" in grouped
        assert "Troll Loop" in grouped
        assert "Channels" in grouped

    def test_grouped_entries_have_required_fields(self, tmp_config):
        cfg, _ = tmp_config
        for category, entries in cfg.get_all_grouped().items():
            for entry in entries:
                assert "key" in entry
                assert "value" in entry
                assert "value_type" in entry
                assert "description" in entry

    def test_get_setting_meta(self, tmp_config):
        cfg, _ = tmp_config
        meta = cfg.get_setting_meta("feature.gn_police.enabled")
        assert meta is not None
        assert meta["value_type"] == "bool"
        assert meta["category"] == "GN Police"

    def test_get_setting_meta_missing(self, tmp_config):
        cfg, _ = tmp_config
        assert cfg.get_setting_meta("fake.key") is None


class TestGameDetectionCooldownDefaults:
    """Verify game and user cooldowns both default to 24 hours."""

    def test_game_cooldown_is_24h(self, tmp_config):
        cfg, _ = tmp_config
        assert cfg.get("feature.game_detection.game_cooldown_sec") == 86400

    def test_user_cooldown_is_24h(self, tmp_config):
        cfg, _ = tmp_config
        assert cfg.get("feature.game_detection.user_cooldown_sec") == 86400
