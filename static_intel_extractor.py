# static_intel_extractor.py
import re
from datetime import datetime

# Global caches
CACHE_DOC_BY_BASE = {}
CACHE_VARS_BY_BASE = {}
CACHE_MODULE_BY_BASE = {}

MODULE_BLOCK_RE = re.compile(
r'__d\(\s*"([^"]+)"\s*,.*?\(function\([^\)]*\)\s*\{\s*(.*?)\s*\}\s*\)\s*,.*?\)\s*;',
re.S
)
DOCID_EXPORT_RE = re.compile(r'\w+\.exports\s*=\s*"(\d+)"')
LOCAL_ARG_BLOCK_RE = re.compile(r'\{[^{}]*kind\s*:\s*"LocalArgument"[^{}]*\}', re.S)
NAME_IN_BLOCK_RE    = re.compile(r'name\s*:\s*"([^"]+)"')
DEFAULT_IN_BLOCK_RE = re.compile(r'defaultValue\s*:\s*([^,\}]+)')
VARIABLE_NAME_RE    = re.compile(r'variableName\s*:\s*"([^"]+)"')
ENTRYPOINT_PAIR_RE = re.compile(
r'parameters\s*:\s*\w\(\s*"([^"]+)"\s*\)\s*,[\s\S]*?variables\s*:\s*\{(.*?)\}',
re.S
)
VAR_KEY_RE = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)\s*:')
def _extract_modules(text):
    modules = {}
    for m in MODULE_BLOCK_RE.finditer(text):
        name, body = m.groups()
        modules[name] = body
    return modules
def _base_name_from_operation(module_name):
    if module_name.endswith("_facebookRelayOperation"):
        return module_name[:-len("_facebookRelayOperation")]
    return None
def _normalize_default_token(token: str):
    if token is None:
        return None
    s = token.strip()
    if s == "!0": return False
    if s == "!1": return True
    if s.lower() == "null": return None
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    if re.search(r'WebPixelRatio\.get\(\)', s):
        return 1
    if re.fullmatch(r'-?\d+', s):
        try: return int(s)
        except: return s
    if s == "true": return True
    if s == "false": return False
    return None
def _collect_variables_from_graphql(graphql_body):
    names = set(VARIABLE_NAME_RE.findall(graphql_body))
    defaults_map = {}
    for block in LOCAL_ARG_BLOCK_RE.findall(graphql_body):
        nm = None
        dv = None
        m_name = NAME_IN_BLOCK_RE.search(block)
        if m_name:
            nm = m_name.group(1)
            names.add(nm)
        m_def = DEFAULT_IN_BLOCK_RE.search(block)
        if m_def:
            dv = _normalize_default_token(m_def.group(1))
        if nm:
            defaults_map[nm] = dv
    variables = {}
    for n in sorted(names):
        variables[n] = defaults_map.get(n, None)
    return variables
def _infer_default_for_key_from_varblock(var_key: str, var_block: str):
    m = re.search(rf'{re.escape(var_key)}\s*:\s*(.+?)(?:,|\n|\}})', var_block, re.S)
    if not m:
        return None
    token = m.group(1).strip()
    m_tern = re.search(r'\?\s*[^:]+:\s*(.+)$', token)
    if m_tern:
        dv = _normalize_default_token(m_tern.group(1))
        if dv is not None:
            return dv
    dv = _normalize_default_token(token)
    return dv
def _collect_variables_from_entrypoint(entry_body: str, base_name: str):
    variables = {}
    for params_name, var_block in ENTRYPOINT_PAIR_RE.findall(entry_body):
        if params_name != f"{base_name}$Parameters":
            continue
        keys = VAR_KEY_RE.findall(var_block)
        for k in keys:
            if k not in variables:
                variables[k] = _infer_default_for_key_from_varblock(k, var_block)
        break
    return variables
def _collect_variables_from_parameters_blocks(full_text: str, base_name: str):
    variables = {}
    for params_name, var_block in ENTRYPOINT_PAIR_RE.findall(full_text):
        if params_name != f"{base_name}$Parameters":
            continue
        keys = VAR_KEY_RE.findall(var_block)
        for k in keys:
            if k not in variables:
                variables[k] = _infer_default_for_key_from_varblock(k, var_block)
        break
    return variables
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
def _harvest_from_text(txt: str):
    modules = _extract_modules(txt)
    if not modules:
        return {}
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    local_doc_by_base = {}
    for name, body in modules.items():
        base = _base_name_from_operation(name)
        if not base: continue
        m_doc = DOCID_EXPORT_RE.search(body)
        if not m_doc: continue
        docid = m_doc.group(1)
        local_doc_by_base[base] = docid
        CACHE_DOC_BY_BASE[base] = docid
        CACHE_MODULE_BY_BASE[base] = base
    for name, body in modules.items():
        if name.endswith(".graphql"):
            base = name[:-len(".graphql")]
            vars_graphql = _collect_variables_from_graphql(body)
            CACHE_VARS_BY_BASE[base] = _merge_vars(CACHE_VARS_BY_BASE.get(base, {}), vars_graphql)
            CACHE_MODULE_BY_BASE[base] = base
    for name, body in modules.items():
        if name.endswith(".entrypoint"):
            for params_name, var_block in ENTRYPOINT_PAIR_RE.findall(body):
                if params_name.endswith("$Parameters"):
                    base = params_name[:-len("$Parameters")]
                    variables = {}
                    keys = VAR_KEY_RE.findall(var_block)
                    for k in keys:
                        variables[k] = _infer_default_for_key_from_varblock(k, var_block)
                    CACHE_VARS_BY_BASE[base] = _merge_vars(CACHE_VARS_BY_BASE.get(base, {}), variables)
                    CACHE_MODULE_BY_BASE[base] = base
    for params_name, var_block in ENTRYPOINT_PAIR_RE.findall(txt):
        if params_name.endswith("$Parameters"):
            base = params_name[:-len("$Parameters")]
            variables = {}
            keys = VAR_KEY_RE.findall(var_block)
            for k in keys:
                variables[k] = _infer_default_for_key_from_varblock(k, var_block)
            CACHE_VARS_BY_BASE[base] = _merge_vars(CACHE_VARS_BY_BASE.get(base, {}), variables)
            CACHE_MODULE_BY_BASE[base] = base
    pairs = {}
    candidate_bases = set(local_doc_by_base.keys()) | set(CACHE_DOC_BY_BASE.keys())
    for base in sorted(candidate_bases):
        docid = local_doc_by_base.get(base) or CACHE_DOC_BY_BASE.get(base)
        if not docid: continue
        variables = {}
        graphql_name = f"{base}.graphql"
        if graphql_name in modules:
            variables = _collect_variables_from_graphql(modules[graphql_name])
        else:
            newname = base[:-5] if base.endswith("Query") else base
            entry_name = f"{newname}.entrypoint"
            entry_body = modules.get(entry_name)
            variables = _collect_variables_from_entrypoint(entry_body, base) if entry_body else {}
        if not variables:
            variables = _collect_variables_from_parameters_blocks(txt, base)
        if (not variables) and (base in CACHE_VARS_BY_BASE):
            variables = CACHE_VARS_BY_BASE.get(base, {})
        if variables:
            CACHE_VARS_BY_BASE[base] = _merge_vars(CACHE_VARS_BY_BASE.get(base, {}), variables)
        pairs[docid] = {
            "doc_id": docid,
            "variables": variables if isinstance(variables, dict) else {},
            "module": CACHE_MODULE_BY_BASE.get(base, base),
            "ts": ts
        }
    return pairs