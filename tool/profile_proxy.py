"""Bounded, target-only character API client for local and Python web servers."""
from concurrent.futures import Future, ThreadPoolExecutor
from copy import deepcopy
import json
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import HTTPRedirectHandler, Request, build_opener

from letools import profile_url

UPSTREAM = "https://planners.maxroll.gg/lastepoch/characters/"
MAX_RESPONSE = 512 * 1024


class ProfileReadError(ValueError):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *_):
        return None


def normalize_links(value):
    values = value.split() if isinstance(value, str) else value
    if not isinstance(values, list) or len(values) > 100:
        raise ProfileReadError("请填写1–12个具体角色链接。")
    urls = []
    for item in values:
        if not item:
            continue
        try:
            url, account, character = profile_url(item)
        except ValueError as error:
            raise ProfileReadError(str(error)) from None
        if any(len(part) > 128 or "\x7f" in part for part in (account, character)):
            raise ProfileReadError("账号或角色名格式不正确。")
        if url not in urls:
            urls.append(url)
    if not 1 <= len(urls) <= 12:
        raise ProfileReadError("一次读取1–12个角色；重复链接只读取一次。")
    return urls


def compact_character(raw, url):
    _, account, character = profile_url(url)
    if not isinstance(raw, dict) or raw.get("error"):
        raise ProfileReadError(f"无法读取 {character}：角色未公开、账号／角色名不正确，或来源站暂时不可用。", 502)
    if not isinstance(raw.get("characterName"), str) or raw["characterName"].lower() != character.lower():
        raise ProfileReadError(f"来源返回的角色与 {character} 链接不一致。", 502)
    if not isinstance(raw.get("savedItems"), list) or len(raw["savedItems"]) > 2000:
        raise ProfileReadError(f"{character}缺少装备数据，或来源格式已变化。", 502)
    items = []
    for item in raw["savedItems"]:
        if not isinstance(item, dict) or type(item.get("containerID")) is not int:
            raise ProfileReadError("来源物品位置格式已变化。", 502)
        if not (2 <= item["containerID"] <= 12 or item["containerID"] in (29, 123)):
            continue
        data = item.get("data")
        if (not isinstance(data, list) or not 10 <= len(data) <= 256
                or any(type(n) is not int or not 0 <= n <= 255 for n in data)):
            raise ProfileReadError("来源物品格式已变化。", 502)
        items.append({"containerID": item["containerID"], "data": data})
    if not 1 <= len(items) <= 37:
        raise ProfileReadError(f"{character}没有可读取的装备，或物品数量不正确。", 502)
    result = {"url": url, "provider": "Maxroll", "api_url": UPSTREAM + quote(account, safe="") + "/" + quote(character, safe=""),
              "save": {"characterName": raw["characterName"], "savedItems": items}}
    if type(raw.get("lastUpdated")) in (str, int, float):
        result["last_updated"] = raw["lastUpdated"]
    return result


class ProfileProxy:
    def __init__(self, opener=None, clock=time.monotonic):
        self.open = opener or build_opener(NoRedirect()).open
        self.clock = clock
        self.cache, self.pending = {}, {}
        self.lock = threading.Lock()

    def _fetch(self, url):
        _, account, character = profile_url(url)
        request = Request(UPSTREAM + quote(account, safe="") + "/" + quote(character, safe=""),
                          headers={"Accept": "application/json", "User-Agent": "LE-filter character importer"})
        try:
            with self.open(request, timeout=20) as response:
                if response.status != 200:
                    raise ProfileReadError(f"{character}来源站返回HTTP {response.status}，请稍后重试。", 502)
                raw = response.read(MAX_RESPONSE + 1)
        except HTTPError as error:
            code = error.code
            error.close()
            raise ProfileReadError(f"{character}来源站返回HTTP {code}，请稍后重试。", 502) from None
        except (URLError, OSError, TimeoutError):
            raise ProfileReadError(f"{character}读取失败或超时，请稍后重试。", 502) from None
        if len(raw) > MAX_RESPONSE:
            raise ProfileReadError(f"{character}返回数据超过大小限制。", 502)
        try:
            data = json.loads(raw)
        except (ValueError, UnicodeDecodeError):
            raise ProfileReadError(f"{character}返回数据无效，请稍后重试。", 502) from None
        return compact_character(data, url)

    def character(self, url):
        with self.lock:
            hit = self.cache.get(url)
            if hit and hit[0] > self.clock():
                return deepcopy(hit[1])
            owner = url not in self.pending
            if owner:
                if len(self.pending) >= 24:
                    raise ProfileReadError("角色读取服务繁忙，请稍后重试。", 429)
                self.pending[url] = Future()
            pending = self.pending[url]
        if not owner:
            try:
                return deepcopy(pending.result(timeout=25))
            except TimeoutError:
                raise ProfileReadError("角色读取超时，请稍后重试。", 502) from None
        try:
            result = self._fetch(url)
            with self.lock:
                if len(self.cache) >= 256:
                    del self.cache[next(iter(self.cache))]
                self.cache[url] = (self.clock() + 300, result)
            pending.set_result(result)
            return deepcopy(result)
        except Exception as error:
            pending.set_exception(error)
            raise
        finally:
            with self.lock:
                del self.pending[url]

    def read(self, payload):
        if not isinstance(payload, dict):
            raise ProfileReadError("读取参数不正确。")
        urls = normalize_links(payload.get("links"))
        name = payload.get("name", "")
        if not isinstance(name, str) or len(name) > 100:
            raise ProfileReadError("个人BD名称请限制在100字以内。")
        results, failures, todo = [None] * len(urls), [], iter(enumerate(urls))
        lock = threading.Lock()

        def worker():
            while True:
                with lock:
                    job = next(todo, None) if not failures else None
                if job is None:
                    return
                index, url = job
                try:
                    results[index] = self.character(url)
                except Exception as error:
                    with lock:
                        failures.append(error)

        with ThreadPoolExecutor(max_workers=min(3, len(urls))) as pool:
            list(pool.map(lambda _: worker(), range(min(3, len(urls)))))
        if failures:
            raise failures[0]
        return {"format": "letools-profile-bundle", "version": 1, "name": name.strip(), "profiles": results}


proxy = ProfileProxy()
