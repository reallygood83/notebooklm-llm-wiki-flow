from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class GeneratedFile:
    relative_path: str
    target_path: Path
    content: str


@dataclass(slots=True)
class PersistedOutputs:
    manifest_path: Path
    staging_dir: Path
    promoted_targets: list[Path] = field(default_factory=list)


def _sha256_text(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def persist_generated_outputs(
    *,
    notebook_id: str,
    artifacts_dir: Path,
    generated_files: list[GeneratedFile],
    created_at: str,
) -> PersistedOutputs:
    staging_dir = artifacts_dir / "staging"
    backup_dir = artifacts_dir / "backup"
    manifest_path = artifacts_dir / "manifest.json"

    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    staging_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    manifest_files: list[dict[str, object]] = []
    staged_paths: list[tuple[GeneratedFile, Path]] = []
    for generated_file in generated_files:
        staged_path = staging_dir / generated_file.relative_path
        staged_path.parent.mkdir(parents=True, exist_ok=True)
        staged_path.write_text(generated_file.content, encoding="utf-8")
        staged_paths.append((generated_file, staged_path))
        manifest_files.append(
            {
                "relative_path": generated_file.relative_path,
                "target_path": str(generated_file.target_path),
                "bytes": len(generated_file.content.encode("utf-8")),
                "sha256": _sha256_text(generated_file.content),
            }
        )

    moved_targets: list[Path] = []
    backups: list[tuple[Path, Path]] = []
    try:
        for generated_file, staged_path in staged_paths:
            target_path = generated_file.target_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if target_path.exists():
                backup_path = backup_dir / generated_file.relative_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(target_path), str(backup_path))
                backups.append((backup_path, target_path))
            shutil.move(str(staged_path), str(target_path))
            moved_targets.append(target_path)

        manifest = {
            "notebook_id": notebook_id,
            "created_at": created_at,
            "staging_dir": str(staging_dir),
            "files": manifest_files,
        }
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        for moved_target in reversed(moved_targets):
            if moved_target.exists():
                moved_target.unlink()
        for backup_path, target_path in reversed(backups):
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if backup_path.exists():
                shutil.move(str(backup_path), str(target_path))
        if manifest_path.exists():
            manifest_path.unlink()
        raise
    finally:
        if staging_dir.exists():
            shutil.rmtree(staging_dir)
        if backup_dir.exists():
            shutil.rmtree(backup_dir)

    return PersistedOutputs(
        manifest_path=manifest_path,
        staging_dir=staging_dir,
        promoted_targets=moved_targets,
    )
