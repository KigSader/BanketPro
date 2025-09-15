#!/usr/bin/env python3
# dump_repo.py — собирает важные файлы в один markdown для ревью
import os, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT  = ROOT / "repo_dump.md"

# Что включаем
INCLUDE_EXT  = {".py", ".html", ".txt", ".md", ".ini", ".cfg", ".toml", ".yaml", ".yml"}
INCLUDE_DIRS = {"banketpro", "calendarapp", "crm", "menuapp", "tasksapp",
                "warehouse", "employees", "expenses", "reviews", "settingsapp",
                "templates"}  # добавь свои app'ы при необходимости

# Что исключаем
EXCLUDE_DIRS = {".git", ".hg", ".svn", "__pycache__", ".pytest_cache", ".mypy_cache",
                "venv", ".venv", "env", "node_modules", "static", "media",
                "migrations", "dist", "build", ".idea", ".vscode", ".DS_Store"}

def should_skip_dir(path: Path) -> bool:
    name = path.name
    if name in EXCLUDE_DIRS: return True
    if name.startswith('.'): return True
    return False

def should_take_file(path: Path) -> bool:
    if path.suffix.lower() not in INCLUDE_EXT: return False
    return True

def walk_selected(root: Path):
    # Ищем только внутри INCLUDE_DIRS (и корневые конфиги)
    for p in sorted(root.iterdir()):
        if p.is_file() and should_take_file(p):
            yield p
        elif p.is_dir() and (p.name in INCLUDE_DIRS) and not should_skip_dir(p):
            for sub, _, files in os.walk(p):
                sp = Path(sub)
                # отбрасываем запрещённые каталоги
                parts = set(sp.parts)
                if any(d in parts for d in EXCLUDE_DIRS): continue
                for f in files:
                    fp = sp / f
                    if should_take_file(fp):
                        yield fp

def main():
    lines = []
    lines.append("# Repository dump\n")
    for file in walk_selected(ROOT):
        rel = file.relative_to(ROOT)
        try:
            content = file.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            continue
        # слегка маскируем секреты в .env и settings
        if rel.name.lower().startswith(".env") or rel.name.lower() in {"settings.py",}:
            content = re.sub(r"(SECRET_KEY\s*=\s*['\"].+?['\"])", r"SECRET_KEY = '***'", content)
            content = re.sub(r"(DATABASES\s*=\s*\{[\s\S]+?\})", r"DATABASES = { /* redacted for dump */ }", content)

        lines.append(f"\n\n---\n## {rel}\n```{file.suffix[1:] or ''}\n{content}\n```\n")

    OUT.write_text("".join(lines), encoding="utf-8")
    print(f"Written: {OUT}")

if __name__ == "__main__":
    main()
