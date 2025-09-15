"""
dump_project_clean.py — cобирает ТВОЙ исходный код в repo_dump.md,
игнорируя системные папки и мусор.

Запуск:
    python dump_project_clean.py
Опции:
    python dump_project_clean.py --root . --out repo_dump.md --max-bytes 1048576
"""

import os
import sys
import argparse

# --- что исключаем полностью (имена папок) ---
EXCLUDE_DIRS = {
    ".git", ".hg", ".svn", ".idea", ".vscode",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".cache",
    "node_modules", "bower_components",
    ".venv", "venv", "env", "ENV", ".tox", ".eggs",
    "dist", "build", "htmlcov", "coverage_html",
    "site-packages", "lib", "lib64", "bin", "include",
    # часто это сборные артефакты, а не исходники
    "staticfiles", "media", "uploads",
    # логи/временное
    "logs", "log", "tmp", "temp"
}

# --- какие расширения считаем ИСХОДНИКАМИ ---
INCLUDE_EXTENSIONS = {
    # backend / infra
    ".py", ".pyi", ".ini", ".cfg", ".toml", ".yaml", ".yml",
    ".json", ".txt", ".md", ".sql",
    ".env.example", ".dockerignore",
    # frontend
    ".html", ".htm", ".css", ".scss", ".less",
    ".js", ".jsx", ".ts", ".tsx",
}

# --- какие файлы исключаем по имени (секреты и мусор) ---
EXCLUDE_FILENAMES = {
    ".env", ".env.local", ".env.development", ".env.production",
    ".python-version",
}

# --- лимит размера одного файла (по умолчанию 1 МБ, чтобы случайно не втянуть сгенерированные простыни) ---
DEFAULT_MAX_BYTES = 1 * 1024 * 1024  # 1 MiB


def guess_lang_by_ext(ext: str) -> str:
    ext = ext.lower()
    return {
        ".py": "python",
        ".pyi": "python",
        ".html": "html",
        ".htm": "html",
        ".css": "css",
        ".scss": "scss",
        ".less": "less",
        ".js": "javascript",
        ".jsx": "jsx",
        ".ts": "typescript",
        ".tsx": "tsx",
        ".json": "json",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".ini": "ini",
        ".cfg": "ini",
        ".toml": "toml",
        ".txt": "text",
        ".md": "markdown",
        ".sql": "sql",
        ".dockerignore": "text",
        ".env.example": "ini",
    }.get(ext, "")


def should_skip_dir(dirname: str) -> bool:
    # сравнение по имени каталога (как отдаёт os.walk в `dirs`)
    return dirname in EXCLUDE_DIRS or dirname.startswith(".")


def should_include_file(path: str) -> bool:
    base = os.path.basename(path)
    if base in EXCLUDE_FILENAMES:
        return False
    _, ext = os.path.splitext(base)
    # особый случай: ".env.example" — у него ext(".example"), проверим отдельно
    if base.endswith(".env.example"):
        return True
    return ext.lower() in INCLUDE_EXTENSIONS


def main():
    parser = argparse.ArgumentParser(description="Dump your source code to a single Markdown file.")
    parser.add_argument("--root", default=".", help="Project root to scan")
    parser.add_argument("--out", default="repo_dump.md", help="Output markdown file")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES, help="Per-file size cap")
    args = parser.parse_args()

    project_root = os.path.abspath(args.root)
    out_path = os.path.abspath(args.out)
    max_bytes = args.max_bytes

    included, skipped = 0, 0

    with open(out_path, "w", encoding="utf-8") as out:
        out.write(f"# Repository dump\n\nRoot: `{project_root}`\n\n")

        for root, dirs, files in os.walk(project_root):
            # отфильтровываем каталоги на месте, чтобы os.walk туда не заходил
            dirs[:] = [d for d in dirs if not should_skip_dir(d)]

            for fname in files:
                fpath = os.path.join(root, fname)

                # пропускаем файловые ссылки за пределы корня (на всякий случай)
                try:
                    rel = os.path.relpath(fpath, project_root)
                except Exception:
                    skipped += 1
                    continue

                if not should_include_file(fpath):
                    skipped += 1
                    continue

                try:
                    size = os.path.getsize(fpath)
                    if size > max_bytes:
                        skipped += 1
                        continue
                except OSError:
                    skipped += 1
                    continue

                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception as e:
                    content = f"<<Не удалось прочитать файл: {e}>>"

                _, ext = os.path.splitext(fname)
                lang = "text"
                # особый случай для .env.example
                if fname.endswith(".env.example"):
                    lang = "ini"
                else:
                    lang = guess_lang_by_ext(ext) or "text"

                out.write(f"\n\n# FILE: {rel}\n\n")
                out.write(f"```{lang}\n{content}\n```\n")
                included += 1

    print(f"Готово: {out_path}")
    print(f"Файлов включено: {included} | пропущено: {skipped}")
    print("Подсказка: если что-то нужное пропустилось — добавь расширение в INCLUDE_EXTENSIONS,")
    print("или убери папку из EXCLUDE_DIRS и повтори запуск.")


if __name__ == "__main__":
    sys.exit(main())
