"""Copy the tracked relay sources into its separately managed Sites checkout."""
import argparse
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def prepare(checkout):
    checkout = checkout.resolve()
    if checkout == ROOT or ROOT in checkout.parents:
        raise ValueError("Sites后端使用独立checkout，不能覆盖当前仓库。")
    source = ROOT / "services/letools-relay"
    if not (checkout / "vite.config.ts").is_file():
        raise ValueError("先使用Sites的project-setup.mjs准备Vinext项目。")
    destination = checkout / ".openai/hosting.json"
    manifest = json.loads((source / "hosting.json").read_text(encoding="utf-8"))
    if destination.exists():
        existing = json.loads(destination.read_text(encoding="utf-8"))
        if existing.get("project_id") != manifest["project_id"]:
            raise ValueError("Sites项目身份不一致，未修改checkout。")
        manifest.update(existing)
    destination.parent.mkdir(exist_ok=True)
    temporary = destination.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(destination)
    (checkout / "lib").mkdir(exist_ok=True)
    shutil.copyfile(source / "relay.mjs", checkout / "lib/relay.mjs")
    for file in (source / "site").rglob("*"):
        if file.is_file():
            target = checkout / file.relative_to(source / "site")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(file, target)
    print(f"Prepared relay sources: {checkout}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("checkout", type=Path)
    prepare(parser.parse_args().checkout)
