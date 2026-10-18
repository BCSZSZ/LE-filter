"""Package the reviewed engine, independent examples and a pinned Pyodide."""
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
PYODIDE_VERSION = "314.0.7"
PYODIDE_FILES = ("pyodide.mjs", "pyodide.asm.mjs", "pyodide.asm.wasm", "python_stdlib.zip", "pyodide-lock.json")
WEB_FILES = ("index.html", "app.js", "workbench.js", "profile-import.js", "style.css", "browser.js", "worker.mjs")
PROBABILITY_FILES = ("index.html", "app.js", "model.mjs", "style.css")
PROBABILITY_WORKBOOK = "outputs/01a135a3-5a09-7e91-83c5-4bd333aeb5ea/普通崇高预言-T7概率.xlsx"


def build_probability_page(site):
    output = site / "probability"
    output.mkdir(exist_ok=True)
    digest = hashlib.sha256()
    for name in PROBABILITY_FILES:
        content = (ROOT / "tool/probability_web" / name).read_bytes()
        digest.update(name.encode() + b"\0" + content)
        (output / name).write_bytes(content)
    data = (ROOT / "analysis/prophecy-probabilities.json").read_bytes()
    digest.update(data)
    (output / "probabilities.json").write_bytes(data)
    shutil.copyfile(ROOT / PROBABILITY_WORKBOOK, output / "probabilities.xlsx")
    revision = digest.hexdigest()[:16]
    app = (output / "app.js").read_text(encoding="utf-8")
    app = app.replace('"./model.mjs"', f'"./model.mjs?v={revision}"')
    app = app.replace('"probabilities.json"', f'"probabilities.json?v={revision}"')
    (output / "app.js").write_text(app, encoding="utf-8", newline="\n")
    index = (output / "index.html").read_text(encoding="utf-8")
    for name in ("app.js", "style.css"):
        index = index.replace(f'"{name}"', f'"{name}?v={revision}"')
    index = index.replace('href="probabilities.xlsx"', f'href="probabilities.xlsx?v={revision}"')
    (output / "index.html").write_text(index, encoding="utf-8", newline="\n")


def build_archive(output):
    evidence = json.loads((ROOT / "analysis/raxx-variable-extraction.json").read_text(encoding="utf-8"))
    files = ["tool/engine.py", "tool/requirements.py", "tool/browser_runtime.py", "tool/letools.py", "tool/character_save.py",
             "scripts/extract_raxx_variables.py", "scripts/generate_filter.py", "scripts/generate_current_filter.py",
             "sources/tool-catalog.json", "sources/unique-drop-catalog.json", "sources/seasonal-unique-protection.json", "sources/common-unique-protection.json", "sources/item-sets.json", "sources/ultra-rare-uniques.json", "templates/base-manifest.json", "templates/LE-base-v1.xml",
             "analysis/raxx-variable-extraction.json"]
    files += [spec["file"] for spec in evidence["strict_inputs"].values()]
    files += [str(p.relative_to(ROOT)).replace("\\", "/") for p in sorted((ROOT / "requirements").glob("*.json"))]
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(set(files)):
            info = zipfile.ZipInfo(name)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, (ROOT / name).read_bytes())


def build_startup_snapshot(output):
    sys.path.insert(0, str(ROOT / "tool"))
    from browser_runtime import browser_startup_snapshot
    content = (json.dumps(browser_startup_snapshot(), ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    output.write_bytes(content)
    return content


def main():
    site = ROOT / ".site"
    site.mkdir(exist_ok=True)
    for name in WEB_FILES:
        shutil.copyfile(ROOT / "tool/web" / name, site / name)
    build_probability_page(site)
    build_archive(site / "runtime.zip")
    startup = build_startup_snapshot(site / "bootstrap.json")
    # Hash uncompressed files so Windows and Linux produce the same revision.
    digest = hashlib.sha256()
    with zipfile.ZipFile(site / "runtime.zip") as archive:
        for name in sorted(archive.namelist()):
            digest.update(name.encode() + b"\0" + archive.read(name))
    for name in WEB_FILES:
        digest.update(name.encode() + b"\0" + (site / name).read_bytes())
    digest.update(b"bootstrap.json\0" + startup)
    revision = digest.hexdigest()[:16]
    index = (site / "index.html").read_text(encoding="utf-8")
    index = index.replace('<script src="app.js">', '<script src="browser.js"></script>\n<script src="app.js">')
    index = index.replace('</head>', f'<link rel="preload" href="bootstrap.json?v={revision}" as="fetch" crossorigin>\n</head>')
    for name in ("app.js", "workbench.js", "profile-import.js", "browser.js", "style.css"):
        index = index.replace(f'"{name}"', f'"{name}?v={revision}"')
    (site / "index.html").write_text(index, encoding="utf-8", newline="\n")
    (site / ".nojekyll").touch()
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
