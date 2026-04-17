from pathlib import Path

from notebooklm_llm_wiki_flow.config import load_config


def test_load_config_prefers_nlwflow_environment_variables(monkeypatch, tmp_path: Path):
    config_path = tmp_path / "project.yaml"
    config_path.write_text(
        "project_name: from-file\nobsidian_vault: ~/VaultFromFile\nqmd_command: qmd-file\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("NLWFLOW_PROJECT_NAME", "from-env")
    monkeypatch.setenv("NLWFLOW_OBSIDIAN_VAULT", str(tmp_path / "VaultFromEnv"))
    monkeypatch.setenv("NLWFLOW_QMD_COMMAND", "qmd-env")

    cfg = load_config(config_path)

    assert cfg.project_name == "from-env"
    assert cfg.obsidian_vault == (tmp_path / "VaultFromEnv").resolve()
    assert cfg.qmd_command == "qmd-env"


def test_load_config_reads_dotenv_from_config_directory(monkeypatch, tmp_path: Path):
    monkeypatch.delenv("NLWFLOW_PROJECT_NAME", raising=False)
    monkeypatch.delenv("NLWFLOW_NOTEBOOKLM_COMMAND", raising=False)
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / ".env").write_text(
        "NLWFLOW_PROJECT_NAME=from-dotenv\nNLWFLOW_NOTEBOOKLM_COMMAND=notebooklm-dotenv\n",
        encoding="utf-8",
    )
    config_path = config_dir / "project.yaml"
    config_path.write_text("project_name: from-file\n", encoding="utf-8")

    cfg = load_config(config_path)

    assert cfg.project_name == "from-file"
    assert cfg.notebooklm_command == "notebooklm-dotenv"
