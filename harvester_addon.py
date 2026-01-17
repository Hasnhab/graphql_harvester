# harvester_addon.py
import os
import json
from datetime import datetime
from mitmproxy import http
from urllib.parse import parse_qs, urlparse
import correlation_core
from graphql_surface import _parse_graphql_variables_from_body
from static_intel_extractor import _harvest_from_text
from observed_injection_hints import (
    OBSERVED_PARAMS, _norm_key, _repr_value, _observed_add_from_dict,
    _observed_top_value, _observed_snapshot, _render_html
)
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
BASE_DIR = os.path.join(desktop, "graphql_harvester")
os.makedirs(BASE_DIR, exist_ok=True)
REPO_HTML = os.path.join(BASE_DIR, "repository.html")
SESSION_HTML = os.path.join(BASE_DIR, "session.html")
REPO_INDEX = os.path.join(BASE_DIR, "index.json")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)
LOGO_REL_PATH = "assets/logo_xvisor03.png"
def load(_l):
    correlation_core.repo_items = correlation_core._load_repo_index()
    correlation_core.repo_seen_docids = set(it["doc_id"] for it in correlation_core.repo_items if "doc_id" in it)
    _render_html([], SESSION_HTML, page_kind="session")
    _render_html(correlation_core.repo_items, REPO_HTML, page_kind="repo")
def response(flow: http.HTTPFlow):
    try:
        ct = flow.response.headers.get("Content-Type", "").lower()
        url = flow.request.pretty_url
        url_lc = url.lower()
        is_js = (".js" in url_lc) or ("javascript" in ct)
        if not is_js:
            return
        body = flow.response.get_text() or ""
        if not body or ("__d(" not in body):
            return
        pairs = _harvest_from_text(body)
        if not pairs:
            return
        host = (flow.request.host or "").strip().lower()
        src = url.strip()
        updated_session = False
        updated_repo = False
        for docid, rec in pairs.items():
            new_repo = correlation_core._upsert_repo(docid, rec["variables"], rec["module"], rec["ts"], host, src)
            updated_repo = updated_repo or new_repo
            new_sess = correlation_core._upsert_session(docid, rec["variables"], rec["module"], rec["ts"], host, src)
            updated_session = updated_session or new_sess
        if updated_repo:
            correlation_core._save_repo_index(correlation_core.repo_items)
            _render_html(correlation_core.repo_items, REPO_HTML, page_kind="repo")
        if updated_session:
            _render_html(correlation_core.session_items, SESSION_HTML, page_kind="session")
    except Exception:
        return
def request(flow: http.HTTPFlow):
    try:
        url = (flow.request.pretty_url or "")
        url_lc = url.lower()
        if "/api/graphql" not in url_lc:
            return
        try:
            parsed_url = urlparse(url)
            q = parse_qs(parsed_url.query, keep_blank_values=True)
            vars_q = q.get("variables") or q.get("Variables") or []
            for vstr in vars_q:
                try:
                    pobj = json.loads(vstr)
                    if isinstance(pobj, dict):
                        _observed_add_from_dict(pobj)
                except Exception:
                    pass
        except Exception:
            pass
        req_text = flow.request.get_text() or ""
        vars_sets = _parse_graphql_variables_from_body(req_text)
        for vars_obj in vars_sets:
            _observed_add_from_dict(vars_obj)
        _render_html(correlation_core.session_items, SESSION_HTML, page_kind="session")
        _render_html(correlation_core.repo_items, REPO_HTML, page_kind="repo")
    except Exception:
        return
def done():
    pass

