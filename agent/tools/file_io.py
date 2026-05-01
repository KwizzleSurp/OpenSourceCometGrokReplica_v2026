"""File I/O helpers for reading/writing project workspace files."""
from pathlib import Path

def read_file(path: str) -> str:
    p = Path(path)
    if not p.exists(): return f"[file_io] not found: {path}"
    return p.read_text(encoding="utf-8")

def write_file(path: str, content: str) -> str:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"[file_io] wrote {len(content)} chars to {path}"

def list_dir(path: str = ".") -> list:
    return [str(f) for f in Path(path).rglob("*") if f.is_file()]
