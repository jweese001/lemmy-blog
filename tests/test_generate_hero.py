from pathlib import Path

import scripts.generate_hero as generate_hero


def test_get_api_key_prefers_default_key_file_over_hermes_env(tmp_path, monkeypatch):
    default_key_file = tmp_path / "gemini.key"
    default_key_file.write_text("default-key\n", encoding="utf-8")

    hermes_env = tmp_path / "hermes.env"
    hermes_env.write_text("GEMINI_API_KEY=hermes-test-key\n", encoding="utf-8")

    monkeypatch.setattr(generate_hero, "PROJECT_DIR", tmp_path / "project")
    monkeypatch.setattr(generate_hero, "HERMES_ENV_FILE", hermes_env)
    monkeypatch.setattr(generate_hero, "DEFAULT_KEY_FILE", default_key_file)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY_FILE", raising=False)

    assert generate_hero.get_api_key() == "default-key"


def test_get_api_key_uses_hermes_env_when_repo_env_path_is_stale(tmp_path, monkeypatch):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / ".env").write_text("GEMINI_API_KEY_FILE=/missing/legacy.key\n", encoding="utf-8")

    hermes_env = tmp_path / "hermes.env"
    hermes_env.write_text("GEMINI_API_KEY=hermes-test-key\n", encoding="utf-8")

    monkeypatch.setattr(generate_hero, "PROJECT_DIR", project_dir)
    monkeypatch.setattr(generate_hero, "HERMES_ENV_FILE", hermes_env)
    monkeypatch.setattr(generate_hero, "DEFAULT_KEY_FILE", tmp_path / "default.key")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY_FILE", raising=False)

    assert generate_hero.get_api_key() == "hermes-test-key"


def test_get_api_key_uses_default_key_file(tmp_path, monkeypatch):
    default_key_file = tmp_path / "gemini.key"
    default_key_file.write_text("default-key\n", encoding="utf-8")

    monkeypatch.setattr(generate_hero, "PROJECT_DIR", tmp_path / "project")
    monkeypatch.setattr(generate_hero, "HERMES_ENV_FILE", tmp_path / "missing-hermes.env")
    monkeypatch.setattr(generate_hero, "DEFAULT_KEY_FILE", default_key_file)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY_FILE", raising=False)

    assert generate_hero.get_api_key() == "default-key"


def test_get_api_key_uses_repo_env_key_file_as_legacy_fallback(tmp_path, monkeypatch):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    key_file = tmp_path / "legacy.key"
    key_file.write_text("legacy-key\n", encoding="utf-8")
    (project_dir / ".env").write_text(f"GEMINI_API_KEY_FILE={key_file}\n", encoding="utf-8")

    monkeypatch.setattr(generate_hero, "PROJECT_DIR", project_dir)
    monkeypatch.setattr(generate_hero, "HERMES_ENV_FILE", tmp_path / "missing-hermes.env")
    monkeypatch.setattr(generate_hero, "DEFAULT_KEY_FILE", tmp_path / "missing-default.key")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY_FILE", raising=False)

    assert generate_hero.get_api_key() == "legacy-key"
