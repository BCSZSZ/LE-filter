"""Portable relay protocol, error atomicity and private scheme boundaries."""
from copy import deepcopy
from io import BytesIO
import json
from pathlib import Path
import unittest
from urllib.error import HTTPError

import engine
from letools import import_profiles
from profile_proxy import ProfileProxy, ProfileReadError, UPSTREAM, MAX_RESPONSE, normalize_links

FIXTURE = json.loads((engine.ROOT / "sources/builds/maxroll-character-api-2026-10-18.json").read_text(encoding="utf-8"))["responses"]
URLS = [row["url"] for row in FIXTURE]


class Response(BytesIO):
    status = 200


def upstream(fail=False, change=None, clock=None):
    calls = []

    def open_request(request, timeout):
        calls.append(request)
        assert request.full_url.startswith(UPSTREAM)
        assert request.get_method() == "GET"
        assert timeout == 20
        assert request.get_header("Accept") == "application/json"
        row = next(x for x in FIXTURE if request.full_url.endswith('/' + x["response"]["characterName"]))
        raw = deepcopy(row["response"])
        if fail and row is FIXTURE[-1]:
            raw = {"error": "not_found"}
        if change:
            change(raw)
        return Response(json.dumps(raw).encode())

    return ProfileProxy(opener=open_request, **({"clock": clock} if clock else {})), calls


class ProfileProxyTests(unittest.TestCase):
    def test_frozen_native_api_reads_all_76_items_and_deduplicates(self):
        proxy, calls = upstream()
        bundle = proxy.read({"links": URLS + [URLS[0]], "name": "个人方案"})
        imported = import_profiles(bundle)
        self.assertEqual([p["url"] for p in bundle["profiles"]], URLS)
        self.assertEqual(len(calls), 4)
        self.assertEqual([len(p["items"]) for p in imported["source"]["profiles"]], [19] * 4)
        self.assertEqual({k: len(v) for k, v in imported["profile"].items()},
                         {"uniques": 13, "equipment": 10, "idols": 11, "altars": 1, "bases": 0})

    def test_invalid_destinations_never_reach_upstream(self):
        proxy, calls = upstream()
        for links in ([], {}, ["http://127.0.0.1/"], [URLS[0] + "?x=1"], [URLS[0] + "/snapshot/x"],
                      [URLS[0].replace("MAONG", "%2f")], [URLS[0].replace("MAONG", "a" * 129)]):
            with self.subTest(links=links), self.assertRaises(ProfileReadError):
                proxy.read({"links": links})
        self.assertEqual(calls, [])
        self.assertEqual(normalize_links(URLS[0] + "\n" + URLS[0]), URLS[:1])

    def test_source_failure_and_identity_mismatch_abort_the_complete_batch(self):
        for options in ({"fail": True}, {"change": lambda raw: raw.update(characterName="wrong")}):
            proxy, _ = upstream(**options)
            with self.assertRaises(ProfileReadError):
                proxy.read({"links": URLS})

    def test_success_cache_does_not_share_mutable_results_and_expires(self):
        clock = [100]
        proxy, calls = upstream(clock=lambda: clock[0])
        first = proxy.read({"links": URLS[:1]})
        first["profiles"][0]["save"]["savedItems"].clear()
        second = proxy.read({"links": URLS[:1]})
        self.assertEqual(len(second["profiles"][0]["save"]["savedItems"]), 19)
        self.assertEqual(len(calls), 1)
        clock[0] += 301
        proxy.read({"links": URLS[:1]})
        self.assertEqual(len(calls), 2)

    def test_redirect_invalid_json_and_oversized_responses_are_rejected(self):
        def redirect(request, timeout):
            raise HTTPError(request.full_url, 302, "Redirect", {}, None)
        for opener in (redirect, lambda *_args, **_kwargs: Response(b"not json"),
                       lambda *_args, **_kwargs: Response(b"a" * (MAX_RESPONSE + 1))):
            with self.subTest(opener=opener), self.assertRaises(ProfileReadError):
                ProfileProxy(opener=opener).read({"links": URLS[:1]})
