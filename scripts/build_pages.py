"""Package the reviewed engine, four independent examples and a pinned Pyodide."""
import json
import shutil
import zipfile
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
PYODIDE_VERSION = "314.0.7"
PYODIDE_FILES = ("pyodide.mjs", "pyodide.asm.mjs", "pyodide.asm.wasm", "python_stdlib.zip", "pyodide-lock.json")


def build_archive(output):
    evidence = json.loads((ROOT / "analysis/raxx-variable-extraction.json").read_text(encoding="utf-8"))
    files = ["tool/engine.py", "tool/requirements.py", "tool/browser_runtime.py",
             "scripts/extract_raxx_variables.py", "scripts/generate_filter.py", "scripts/generate_current_filter.py",
             "sources/tool-catalog.json", "sources/seasonal-unique-protection.json", "templates/base-manifest.json", "templates/LE-base-v1.xml",
             "analysis/raxx-variable-extraction.json"]
    files += [spec["file"] for spec in evidence["strict_inputs"].values()]
    files += [str(p.relative_to(ROOT)).replace("\\", "/") for p in sorted((ROOT / "requirements").glob("*.json"))]
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(set(files)):
            info = zipfile.ZipInfo(name)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, (ROOT / name).read_bytes())


def main():
    site = ROOT / ".site"
    site.mkdir(exist_ok=True)
    for name in ("index.html", "app.js", "style.css", "browser.js", "worker.mjs"):
        shutil.copyfile(ROOT / "tool/web" / name, site / name)
    index = (site / "index.html").read_text(encoding="utf-8")
    index = index.replace('<script src="app.js">', '<script src="browser.js"></script>\n<script src="app.js">')
    (site / "index.html").write_text(index, encoding="utf-8", newline="\n")
    (site / ".nojekyll").touch()
    build_archive(site / "runtime.zip")
    cache = ROOT / ".cache/pyodide" / PYODIDE_VERSION
    cache.mkdir(parents=True, exist_ok=True)
    (site / "pyodide").mkdir(exist_ok=True)
    for name in PYODIDE_FILES:
        path = cache / name
        if not path.exists():
            with urlopen(f"https://cdn.jsdelivr.net/pyodide/v{PYODIDE_VERSION}/full/{name}", timeout=60) as response:
                path.write_bytes(response.read())
        shutil.copyfile(path, site / "pyodide" / name)
    print(f"Built {site}: {sum(p.stat().st_size for p in site.rglob('*') if p.is_file()):,} bytes")


if __name__ == "__main__":
    main()
