"""Run the existing importer and generator inside the browser's Python runtime."""
import json
import xml.etree.ElementTree as ET
from functools import lru_cache

from engine import ROOT, bootstrap, extract, generate, normalize_config
from requirements import read_document, write_document


@lru_cache(maxsize=1)
def browser_bootstrap():
    result = bootstrap()
    for slug in ("flay-lich-allie-guide", "bleed-skeleton-roamer-guide-835"):
        build = {"id": slug, "enabled": False, "profiles": {}, "requirement_sources": {}}
        for stage in ("endgame", "leveling"):
            document = json.loads((ROOT / f"requirements/{slug}.{stage}.json").read_text(encoding="utf-8"))
            data = read_document(document)
            build["name"] = data["name"]
            build["profiles"][stage] = data["profile"]
            build["requirement_sources"][stage] = data["source"]
        result["config"]["builds"].append(build)
    return result


def dispatch_json(request):
    try:
        data = json.loads(request)
        path, payload = data["path"], data.get("payload") or {}
        if path == "/api/bootstrap":
            result = browser_bootstrap()
        elif path == "/api/import":
            result = extract(payload["xml"], payload.get("assignments"))
        elif path == "/api/requirements/import":
            result = read_document(payload["document"])
        elif path == "/api/requirements/export":
            result = write_document(payload["build"], payload["stage"])
        elif path == "/api/generate":
            result = generate(payload["config"])
        elif path == "/api/validate":
            result = {"valid": True, "config": normalize_config(payload["config"])}
        else:
            raise ValueError("页面不支持此操作。")
    except (ValueError, KeyError, TypeError, ET.ParseError) as error:
        result = {"error": str(error)}
    return json.dumps(result, ensure_ascii=False)
