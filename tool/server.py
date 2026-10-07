"""Local-only web app. Uses Python's standard library; no installation required."""
import argparse
import json
import mimetypes
import webbrowser
import uuid
from functools import lru_cache
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import xml.etree.ElementTree as ET

from engine import bootstrap, extract, generate, validate_profile
from requirements import read_document, write_document

WEB = Path(__file__).parent / "web"
DOWNLOADS = {}


class Handler(BaseHTTPRequestHandler):
    def reply(self, value, status=200, mime="application/json", filename=None):
        raw = value if isinstance(value, bytes) else json.dumps(value, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", mime + "; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        if filename:
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path.startswith("/download/"):
            item = DOWNLOADS.get(self.path.removeprefix("/download/"))
            if item:
                name, raw, mime = item
                return self.reply(raw, mime=mime, filename=name)
            return self.reply({"error": "下载已过期，请重新导出。"}, 404)
        if self.path == "/api/bootstrap":
            return self.reply(boot())
        name = "index.html" if self.path == "/" else self.path.lstrip("/")
        if name not in {"index.html", "app.js", "style.css"}:
            return self.reply({"error": "Not found"}, 404)
        return self.reply((WEB / name).read_bytes(), mime=mimetypes.guess_type(name)[0] or "text/plain")

    def do_POST(self):
        # Refuse cross-origin writes from other sites; the tool binds only localhost.
        if self.headers.get("Origin") not in {None, "http://" + self.headers.get("Host", "")}:
            return self.reply({"error": "请求必须来自本地工具页面。"}, 403)
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size <= 0 or size > 20 * 1024 * 1024:
                raise ValueError("文件为空或超过20MB。")
            payload = json.loads(self.rfile.read(size))
            if self.path == "/api/download":
                name = payload["name"]
                if name not in {"LE-filter-endgame.xml", "LE-filter-leveling.xml", "LE-filter-targets.json", "LE-filter-requirements.json"}:
                    raise ValueError("下载文件名不正确。")
                token = uuid.uuid4().hex
                mime = "application/xml" if name.endswith(".xml") else "application/json"
                DOWNLOADS[token] = (name, payload["text"].encode(), mime)
                if len(DOWNLOADS) > 8:
                    del DOWNLOADS[next(iter(DOWNLOADS))]
                return self.reply({"url": "/download/" + token})
            if self.path == "/api/import":
                return self.reply(extract(payload["xml"], payload.get("assignments")))
            if self.path == "/api/requirements/import":
                return self.reply(read_document(payload["document"]))
            if self.path == "/api/requirements/export":
                return self.reply(write_document(payload["build"], payload["stage"]))
            if self.path == "/api/generate":
                return self.reply(generate(payload["config"], payload.get("mode", "endgame")))
            if self.path == "/api/validate":
                config = payload["config"]
                if config["version"] != 1 or not isinstance(config["builds"], list):
                    raise ValueError("配置格式不正确。")
                for build in config["builds"]:
                    for mode in ["endgame", "leveling"]:
                        validate_profile(build["profiles"][mode])
                return self.reply({"valid": True})
            return self.reply({"error": "Not found"}, 404)
        except (ValueError, KeyError, TypeError, ET.ParseError) as e:
            return self.reply({"error": str(e)}, 400)

    def log_message(self, *_):
        pass


@lru_cache(maxsize=1)
def boot():
    return bootstrap()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--open", action="store_true")
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"LE Filter tool: http://127.0.0.1:{args.port}", flush=True)
    if args.open:
        webbrowser.open(f"http://127.0.0.1:{args.port}")
    server.serve_forever()
