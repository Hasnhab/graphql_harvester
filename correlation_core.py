# correlation_core.py
import os
import json
from datetime import datetime

# Define paths needed by this module
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
BASE_DIR = os.path.join(desktop, "graphql_harvester")
os.makedirs(BASE_DIR, exist_ok=True)
REPO_INDEX = os.path.join(BASE_DIR, "index.json")

# Global state
repo_items = []
repo_seen_docids = set()
session_items = []
session_seen_docids = set()

# Global caches for cross-file correlation
CACHE_DOC_BY_BASE = {}
CACHE_VARS_BY_BASE = {}
CACHE_MODULE_BY_BASE = {}

def _upsert_repo(docid, variables, module, ts, host="", src=""):
    for it in repo_items:
        if it.get("doc_id") == docid:
            it["variables"] = _merge_vars(it.get("variables", {}), variables)
            it["module"] = module or it.get("module", "")
            it["ts"] = ts or it.get("ts", "")
            if host and not it.get("host"): it["host"] = host
            if src and not it.get("src"): it["src"] = src
            return False
    repo_items.append({"doc_id": docid, "variables": variables, "module": module, "ts": ts, "host": host or "", "src": src or ""})
    repo_seen_docids.add(docid)
    return True

def _upsert_session(docid, variables, module, ts, host="", src=""):
    for it in session_items:
        if it.get("doc_id") == docid:
            it["variables"] = _merge_vars(it.get("variables", {}), variables)
            it["module"] = module or it.get("module", "")
            it["ts"] = ts or it.get("ts", "")
            if host and not it.get("host"): it["host"] = host
            if src and not it.get("src"): it["src"] = src
            return False
    if docid not in session_seen_docids:
        session_seen_docids.add(docid)
        session_items.append({"doc_id": docid, "variables": variables, "module": module, "ts": ts, "host": host or "", "src": src or ""})
        return True
    return False

def _load_repo_index():
    if os.path.exists(REPO_INDEX):
        try:
            with open(REPO_INDEX, "r", encoding="utf-8") as f:
                data = json.load(f)
                items = data.get("items", [])
                for it in items:
                    if "host" not in it: it["host"] = ""
                    if "src" not in it: it["src"] = ""
                return items
        except Exception:
            pass
    return []

def _save_repo_index(items):
    safe_items = []
    for it in items:
        safe_items.append({
            "doc_id": it.get("doc_id"),
            "variables": it.get("variables", {}),
            "module": it.get("module", ""),
            "ts": it.get("ts", ""),
            "host": it.get("host", ""),
            "src": it.get("src", "")
        })
    with open(REPO_INDEX, "w", encoding="utf-8") as f:
        json.dump({"items": safe_items}, f, ensure_ascii=False, indent=2)

def _merge_vars(existing: dict, newvars: dict):
    if not isinstance(existing, dict) or not existing:
        return dict(newvars) if isinstance(newvars, dict) else {}
    if not isinstance(newvars, dict) or not newvars:
        return existing
    merged = dict(existing)
    for k, v in newvars.items():
        if k not in merged or merged[k] is None:
            merged[k] = v
    return merged