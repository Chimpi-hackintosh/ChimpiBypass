"""Safe per-application Mesa3D file installation and rollback helpers."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

MANIFEST = ".chimpibypass.json"
BACKUP_DIR = ".chimpibypass-backup"
FILES = ("opengl32.dll", "libgallium_wgl.dll")
SYSTEM_PARTS = {"windows", "system32", "syswow64"}


def _application_directory(executable: Path) -> Path:
    exe = Path(executable).resolve()
    if not exe.is_file() or exe.suffix.lower() != ".exe":
        raise ValueError("Selecione um .exe válido")
    if any(part.lower() in SYSTEM_PARTS for part in exe.parts):
        raise ValueError("Não modifique pastas do sistema Windows")
    return exe.parent


def install_mesa_files(executable: Path, source_folder: Path) -> Path:
    app_dir = _application_directory(executable)
    folder = Path(source_folder).resolve()
    if not folder.is_dir():
        raise ValueError("Selecione uma pasta Mesa3D válida")

    manifest = app_dir / MANIFEST
    backup = app_dir / BACKUP_DIR
    if manifest.exists() or manifest.is_symlink():
        raise ValueError("Já há uma instalação ChimpiBypass nesta pasta")
    if backup.exists() or backup.is_symlink():
        raise ValueError("Pasta de backup já existe: restaure ou remova manualmente após verificar")

    sources = []
    for name in FILES:
        source = folder / name
        if source.is_symlink():
            raise ValueError(f"A DLL de origem não pode ser um link simbólico: {name}")
        if source.is_file():
            sources.append(source)
    if not sources or not (folder / FILES[0]).is_file():
        raise ValueError("Pasta Mesa3D precisa conter opengl32.dll")

    backup.mkdir()
    installed = []
    try:
        for source in sources:
            destination = app_dir / source.name
            if destination.is_symlink():
                raise ValueError(f"Destino é link simbólico e foi recusado: {destination.name}")
            if destination.exists():
                if not destination.is_file():
                    raise ValueError(f"Destino não é arquivo: {destination}")
                shutil.copy2(destination, backup / source.name)
            # Register before copying so a partially written destination is rolled back
            if source.name not in installed:
                installed.append(source.name)
            shutil.copy2(source, destination)

        manifest.write_text(
            json.dumps({"files": installed, "backup": BACKUP_DIR}, indent=2),
            encoding="utf-8",
        )
        return manifest
    except Exception:
        for name in installed:
            destination = app_dir / name
            original = backup / name
            if destination.is_symlink():
                destination.unlink()
            if original.is_file() and not original.is_symlink():
                shutil.copy2(original, destination)
            elif destination.exists():
                destination.unlink()
        shutil.rmtree(backup, ignore_errors=True)
        raise


def restore_mesa_files(executable: Path) -> None:
    app_dir = _application_directory(executable)
    manifest = app_dir / MANIFEST
    if manifest.is_symlink() or not manifest.is_file():
        raise ValueError("Nenhuma instalação ChimpiBypass válida encontrada")

    record = json.loads(manifest.read_text(encoding="utf-8"))
    if not isinstance(record, dict) or record.get("backup") != BACKUP_DIR:
        raise ValueError("Manifesto inválido")
    names = record.get("files")
    if not isinstance(names, list) or not names or any(name not in FILES for name in names):
        raise ValueError("Lista de arquivos inválida no manifesto")
    if len(set(names)) != len(names):
        raise ValueError("Lista de arquivos duplicada no manifesto")

    backup = app_dir / BACKUP_DIR
    if backup.is_symlink() or not backup.is_dir() or backup.resolve().parent != app_dir.resolve():
        raise ValueError("Backup inválido")

    # Validate every path before restoring any file
    for name in names:
        destination = app_dir / name
        previous = backup / name
        if destination.is_symlink() or previous.is_symlink():
            raise ValueError(f"Link simbólico recusado durante a restauração: {name}")
        if destination.exists() and not destination.is_file():
            raise ValueError(f"Destino não é arquivo: {destination}")
        if previous.exists() and not previous.is_file():
            raise ValueError(f"Backup não é arquivo: {previous}")

    for name in names:
        destination = app_dir / name
        previous = backup / name
        if previous.is_file():
            shutil.copy2(previous, destination)
        elif destination.exists():
            destination.unlink()

    manifest.unlink()
    shutil.rmtree(backup)
