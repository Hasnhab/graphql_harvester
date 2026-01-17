# graphql_surface.py
import json
from urllib.parse import parse_qs

def _parse_graphql_variables_from_body(req_text: str):
    if not req_text:
        return []
    try:
        obj = json.loads(req_text)
        if isinstance(obj, dict):
            vars_field = obj.get("variables")
            if isinstance(vars_field, dict):
                return [vars_field]
            if isinstance(vars_field, str):
                try:
                    parsed = json.loads(vars_field)
                    if isinstance(parsed, dict):
                        return [parsed]
                except Exception:
                    pass
            return []
        if isinstance(obj, list):
            out = []
            for item in obj:
                if isinstance(item, dict):
                    v = item.get("variables")
                    if isinstance(v, dict):
                        out.append(v)
                    elif isinstance(v, str):
                        try:
                            pv = json.loads(v)
                            if isinstance(pv, dict):
                                out.append(pv)
                        except Exception:
                            pass
            return out
    except Exception:
        pass
    try:
        qs = parse_qs(req_text, keep_blank_values=True)
        vars_list = qs.get("variables") or qs.get("Variables") or []
        out = []
        for v in vars_list:
            try:
                parsed = json.loads(v)
                if isinstance(parsed, dict):
                    out.append(parsed)
            except Exception:
                continue
        if out:
            return out
    except Exception:
        pass
    return []