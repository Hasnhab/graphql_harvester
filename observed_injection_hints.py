# observed_injection_hints.py
import os
import json
import html
import re
from datetime import datetime
import assets 

desktop = os.path.join(os.path.expanduser("~"), "Desktop")
BASE_DIR = os.path.join(desktop, "graphql_harvester")
os.makedirs(BASE_DIR, exist_ok=True)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)
LOGO_DATA_URL = f"data:image/png;base64,{assets.LOGO_XVISOR03_PNG}"
OBSERVED_PARAMS = {}
def _norm_key(k: str) -> str:
    if not k:
        return ""
    s = str(k).strip()
    s1 = re.sub(r"[^A-Za-z0-9_]", "", s)
    return s1.lower()
def _repr_value(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    try:
        if isinstance(v, str):
            return json.dumps(v)
        return json.dumps(v)
    except Exception:
        return str(v)
def _observed_add_from_dict(d: dict):
    for k, v in (d or {}).items():
        nk = _norm_key(k)
        if not nk:
            continue
        val_repr = _repr_value(v)
        slot = OBSERVED_PARAMS.get(nk) or {"values": {}, "count": 0}
        slot["values"][val_repr] = slot["values"].get(val_repr, 0) + 1
        slot["count"] += 1
        OBSERVED_PARAMS[nk] = slot
def _observed_top_value(nk: str):
    slot = OBSERVED_PARAMS.get(nk)
    if not slot:
        return None
    vals = slot["values"]
    if not vals:
        return None
    return sorted(vals.items(), key=lambda x: (-x[1], x[0]))[0][0]
def _observed_snapshot():
    out = {}
    for nk, slot in OBSERVED_PARAMS.items():
        topv = _observed_top_value(nk)
        tops = sorted(slot["values"].items(), key=lambda x: (-x[1], x[0]))[:5]
        out[nk] = {
            "count": slot.get("count", 0),
            "value": topv if topv is not None else None,
            "values": [{"v": k, "c": c} for k, c in tops]
        }
    return out
def _html_header(title, banner_color, subtitle="By Hasan Habeeb", page_kind="repo"):
    table_id = "repo_graphql_table" if page_kind == "repo" else "session_graphql_table"
    observed_json = json.dumps(_observed_snapshot(), ensure_ascii=False)
    tpl = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>__TITLE__</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
:root{
--bg:#0a0b10; --bg2:#0d0f16; --fg:#e5e7eb; --muted:#9ca3af;
--panel:#12141b; --panel2:#0f1218; --border:#1f2430;
--brandRed:#ff2a2a; --brandGlow:#ff3b3b;
--ok:#10b981; --warn:#f59e0b; --danger:#ef4444;
--fontBrand: 'Inter','Segoe UI',Arial,sans-serif;
}
*{box-sizing:border-box; margin:0; padding:0}
html,body{height:100%; font-size:16px}
body{margin:0; padding:20px; font-family:var(--fontBrand); color:var(--fg); background:var(--bg); overflow-x:hidden}
.bg-logo{position:fixed; inset:0; z-index:0; pointer-events:none; background-image:url('__LOGO_PATH__'); background-repeat:no-repeat; background-position:center 20%; background-size:900px auto; opacity:0.06; filter:blur(28px) saturate(140%); mix-blend-mode:screen; transform:translateZ(0);}
.app-root{position:relative; z-index:1; min-height:100vh; max-width:1800px; margin:0 auto}
.banner{position:relative; display:flex; flex-direction:column; gap:16px; padding:20px; margin-bottom:20px; color:#fff; background:linear-gradient(135deg, rgba(25,25,35,0.95), rgba(10,12,20,0.98)); border-radius:16px; box-shadow:0 10px 40px rgba(0,0,0,0.7), inset 0 -1px 0 rgba(255,255,255,0.03)}
.banner-content{display:flex; flex-wrap:wrap; justify-content:space-between; align-items:flex-start; gap:20px}
.brand-left{display:flex; flex-direction:column; gap:12px; min-width:300px}
.brand-logo{display:flex; align-items:center; gap:16px}
.brand-logo-img{width:72px; height:72px; object-fit:contain; filter: drop-shadow(0 0 24px rgba(255,42,42,0.6)); border-radius:12px; background:linear-gradient(145deg, rgba(255,255,255,0.05), rgba(0,0,0,0.15)); padding:8px; border:1px solid rgba(255,42,42,0.2)}
.brand-text{display:flex; flex-direction:column; line-height:1.1}
.brand-name{font-weight:900; font-size:28px; color:#fff; text-shadow:0 0 12px var(--brandGlow)}
.brand-page{font-weight:700; font-size:18px; color:#cbd5e1; opacity:0.9}
.brand-sub{font-size:14px; font-weight:700; background:linear-gradient(90deg, rgba(255,42,42,0.12), rgba(255,42,42,0.05)); border:1px solid rgba(255,42,42,0.2); padding:8px 16px; border-radius:12px; display:inline-block}
.stats-row{display:flex; gap:16px; flex-wrap:wrap}
.kpi-card{background:rgba(18,22,30,0.7); border:1px solid var(--border); border-radius:12px; padding:16px; min-width:180px; transition:all 0.3s ease}
.kpi-card:hover{border-color:var(--brandRed); transform:translateY(-2px)}
.kpi-label{font-size:13px; color:var(--muted); margin-bottom:6px; font-weight:600}
.kpi-value{font-size:24px; font-weight:800; color:#fff; text-shadow:0 0 8px rgba(255,42,42,0.3)}
.kpi-trend{display:flex; align-items:center; gap:6px; margin-top:4px; font-size:13px}
.positive{color:var(--ok)}
.negative{color:var(--danger)}
.controls-section{background:rgba(15,18,26,0.7); border-radius:16px; padding:24px; margin-bottom:24px; border:1px solid var(--border)}
.toolbar{display:grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap:16px; margin-bottom:16px}
.toolbar-group{display:flex; flex-direction:column; gap:8px}
.toolbar-label{font-size:13px; color:var(--muted); margin-bottom:4px}
.toolbar input,.toolbar textarea{width:100%; padding:10px 14px; border:1px solid var(--border); background:var(--panel); color:var(--fg); border-radius:10px; font-size:14px; transition:all 0.2s}
.toolbar input:focus,.toolbar textarea:focus{outline:none; border-color:var(--brandRed); box-shadow:0 0 0 2px rgba(255,42,42,0.2)}
.toolbar-buttons{display:grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap:12px; margin-top:12px}
.dash-grid{display:grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap:20px; margin-bottom:24px}
.panel-section{display:flex; flex-direction:column; gap:20px}
.panel-card{background:var(--panel); border:1px solid var(--border); border-radius:16px; padding:20px; transition:all 0.3s ease; position:relative; overflow:hidden}
.panel-card::before{content:''; position:absolute; top:0; left:0; right:0; height:3px; background:linear-gradient(90deg, transparent, var(--brandRed), transparent); opacity:0; transition:opacity 0.3s}
.panel-card:hover::before{opacity:1}
.panel-card:hover{border-color:rgba(255,42,42,0.4); transform:translateY(-3px); box-shadow:0 8px 30px rgba(0,0,0,0.4)}
.section-header{display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; padding-bottom:12px; border-bottom:1px solid rgba(31,36,48,0.7)}
.section-title{font-weight:800; font-size:18px; color:#e5e7eb; display:flex; align-items:center; gap:10px}
.section-title i{font-size:18px; color:var(--brandRed)}
.card-content{display:flex; flex-direction:column; gap:16px}
.input-row{display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:16px; align-items:end}
.btn{padding:10px 18px; border:none; background:linear-gradient(145deg, #1a1d26, #0d0f15); color:var(--fg); border-radius:10px; cursor:pointer; font-weight:600; transition:all 0.2s; display:inline-flex; align-items:center; gap:8px; border:1px solid var(--border); font-size:14px}
.btn:hover{transform:translateY(-2px); box-shadow:0 6px 16px rgba(255,42,42,0.2); border-color:var(--brandRed)}
.btn:active{transform:translateY(0)}
.btn-primary{background:linear-gradient(145deg, #ff2a2a, #e01a1a); border:none; color:white}
.btn-primary:hover{box-shadow:0 6px 24px rgba(255,42,42,0.4)}
.btn-group{display:flex; flex-wrap:wrap; gap:10px; margin-top:10px}
.hint-badge{display:inline-flex; align-items:center; gap:8px; padding:6px 14px; font-size:13px; border-radius:12px; background:linear-gradient(90deg, rgba(255,42,42,0.1), transparent); border:1px solid rgba(255,42,42,0.3); color:#e5e7eb; font-weight:600}
.hint-badge .dot{width:8px; height:8px; border-radius:50%; background:var(--warn)}
.observed-panel{margin-top:16px; background:rgba(16,19,26,0.7); border:1px solid #1f2430; border-radius:12px; padding:16px}
.observed-scroll-container{max-height:300px; overflow-y:auto; margin-top:12px; padding-right:6px}
.observed-scroll-container::-webkit-scrollbar{width:8px}
.observed-scroll-container::-webkit-scrollbar-track{background:rgba(31,36,48,0.3); border-radius:4px}
.observed-scroll-container::-webkit-scrollbar-thumb{background:rgba(255,42,42,0.4); border-radius:4px}
.observed-scroll-container::-webkit-scrollbar-thumb:hover{background:rgba(255,42,42,0.6)}
.observed-header{display:flex; justify-content:space-between; align-items:center; margin-bottom:12px}
.observed-row{display:grid; grid-template-columns: 1.2fr .8fr 1fr auto auto; gap:12px; align-items:center; padding:8px 10px; margin-bottom:8px; background:rgba(12,15,22,0.5); border-radius:8px; font-size:13px}
.observed-row:hover{background:rgba(31,36,48,0.6)}
.observed-key{font-weight:600; color:#e5e7eb}
.observed-count{color:#9ca3af; font-size:12px}
.observed-select{width:100%; padding:6px 10px; border:1px solid var(--border); background:#0f1218; color:#e5e7eb; border-radius:6px; font-size:13px}
.observed-actions{display:flex; flex-direction:column; gap:6px}
.observed-section-toggle{display:flex; align-items:center; gap:8px; cursor:pointer; padding:8px 0; color:var(--fg); font-weight:600}
.observed-section-toggle i{transition:transform 0.3s ease}
.observed-section-toggle.active i{transform:rotate(180deg)}
.observed-summary{background:rgba(25,28,38,0.7); border-radius:10px; padding:12px; margin-top:12px}
.summary-item{display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid rgba(31,36,48,0.5)}
.summary-item:last-child{border-bottom:none}
.summary-label{color:var(--muted); font-size:13px}
.summary-value{font-weight:600; color:#e5e7eb}
.data-panel{background:var(--panel2); border-radius:16px; overflow:hidden; box-shadow:0 8px 40px rgba(0,0,0,0.5); margin-top:24px; border:1px solid var(--border)}
table{width:100%; border-collapse:collapse; background:var(--panel2); font-size:14px}
th,td{border:1px solid var(--border); padding:12px 14px; vertical-align:top}
th{background:rgba(12,14,22,0.95); position:sticky; top:0; z-index:10; text-align:left; color:var(--muted); font-weight:700}
tr:nth-child(even) td{background:rgba(13,17,24,0.5)}
tr:hover td{background:rgba(31,36,48,0.6)}
pre{margin:0; white-space:pre-wrap; word-break:break-word; font-family:Consolas, monospace; font-size:13px; color:#cbd5e1; max-height:180px; overflow:auto; line-height:1.5}
#detail_overlay{display:none; position:fixed; inset:0; background:rgba(0,0,0,0.75); z-index:10000; align-items:center; justify-content:center; backdrop-filter:blur(5px)}
#detail_overlay.active{display:flex}
.detail_card{width:90%; max-width:1200px; height:85vh; display:flex; flex-direction:column; background:linear-gradient(145deg, #0f1218, #0a0c12); border:1px solid rgba(255,42,42,0.3); border-radius:16px; box-shadow:0 20px 50px rgba(0,0,0,0.8), 0 0 0 1px var(--brandRed)}
.detail_header{display:flex; justify-content:space-between; align-items:center; padding:16px 24px; border-bottom:1px solid var(--border); gap:12px; flex-wrap:wrap}
.pill{display:inline-flex; align-items:center; gap:8px; padding:6px 14px; border-radius:12px; background:rgba(31,36,48,0.7); border:1px solid #1f2430; color:#cbd5e1; font-size:14px; font-weight:600}
.btn-close{background:rgba(239,68,68,0.1); border-color:rgba(239,68,68,0.3); color:var(--danger); margin-left:auto}
.detail_body{flex:1; display:grid; grid-template-columns:2fr 1fr; gap:24px; padding:24px; overflow:hidden}
.block{background:rgba(12,15,22,0.7); border:1px solid #1f2430; border-radius:12px; padding:18px; display:flex; flex-direction:column; overflow:hidden}
.block-title{font-size:16px; font-weight:700; color:#e5e7eb; margin-bottom:14px; padding-bottom:8px; border-bottom:1px solid rgba(31,36,48,0.7)}
.json-tree{font-family:Consolas, monospace; font-size:13px; color:#cbd5e1; flex:1 1 auto; overflow:auto; background:rgba(9,11,18,0.8); border:1px solid rgba(31,36,48,0.7); border-radius:10px; padding:14px; line-height:1.5}
.json-k{color:#93c5fd; font-weight:500}
.json-v-str{color:#86efac}
.json-v-num{color:#fde68a}
.json-v-bool{color:#fca5a5}
.json-collapser{cursor:pointer; user-select:none; color:#a5b4fc; margin-right:8px; font-weight:bold}
.hint-table{width:100%; border-collapse:collapse; background:rgba(9,11,18,0.9); border:1px solid #1f2430; border-radius:10px; overflow:hidden}
.hint-table th,.hint-table td{border:1px solid rgba(31,36,48,0.7); padding:10px 12px; font-size:13px}
.hint-ok{color:#10b981; font-weight:600}
.hint-miss{color:#ef4444; font-weight:600}
.host-pill,.src-pill{background:rgba(31,36,48,0.7); border:1px solid #1f2430; border-radius:12px; padding:6px 12px; color:#cbd5e1; font-size:13px; display:inline-flex; gap:8px; align-items:center; font-weight:500}
.auto-pill{background:rgba(255,42,42,0.15); border-color:rgba(255,42,42,0.4); color:#ff8888}
.search-box{position:relative; width:100%}
.search-icon{position:absolute; left:12px; top:50%; transform:translateY(-50%); color:var(--muted); font-size:14px}
.search-input{width:100%; padding:10px 12px 10px 36px; border:1px solid var(--border); background:var(--panel); color:var(--fg); border-radius:10px; font-size:14px}
@media (max-width:1200px){
    .dash-grid{grid-template-columns:1fr}
    .banner-content{flex-direction:column}
    .brand-left{min-width:auto}
    .stats-row{flex-direction:column; gap:12px}
}
@media (max-width:768px){
    .toolbar{grid-template-columns:1fr}
    .input-row{grid-template-columns:1fr}
    .detail_body{grid-template-columns:1fr}
    .observed-row{grid-template-columns:1fr}
    .btn-group{flex-direction:column}
    .observed-scroll-container{max-height:250px}
}
</style>
<script src="https://kit.fontawesome.com/a076d05399.js" crossorigin="anonymous"></script>
<script>
(function(){
const tableId = "__TABLE_ID__";
const pageKind = "__PAGE_KIND__";
window.__OBSERVED__ = __OBSERVED_JSON__;
function getRows(){ const t=document.getElementById(tableId); if(!t) return []; return Array.from(t.querySelectorAll('tbody tr')); }
function parseJSONSafe(s){ try { return JSON.parse(s); } catch(e){ return null; } }
function rowObj(tr){
const tds = tr.querySelectorAll('td');
const pre = tds[2] ? tds[2].querySelector('pre') : null;
const vars = pre ? pre.innerText : "{}";
return {
idx: tds[0]?.innerText.trim() || "",
docid: tds[1]?.innerText.trim() || "",
v: vars,
vObj: parseJSONSafe(vars) || {},
module: tr.getAttribute('data-module') || "",
varsjson: tr.getAttribute('data-varsjson') || "",
host: tr.getAttribute('data-host') || "",
src: tr.getAttribute('data-src') || "",
tr
};
}
function normKey(k){
if(!k) return '';
const s = String(k).trim();
const s1 = s.replace(/[^A-Za-z0-9_]/g,'');
return s1.toLowerCase();
}
function applyFilters(){
const idf = (document.getElementById('filter_docid')||{value:''}).value.toLowerCase();
const mf  = (document.getElementById('filter_module')||{value:''}).value.toLowerCase();
const hf  = (document.getElementById('filter_host')||{value:''}).value.toLowerCase();
const tf  = (document.getElementById('filter_text')||{value:''}).value.toLowerCase();
getRows().forEach(tr=>{
const o=rowObj(tr);
const hay=(o.docid+' '+o.module+' '+o.host+' '+o.v).toLowerCase();
const show = (!idf || o.docid.toLowerCase().includes(idf))
&& (!mf  || o.module.toLowerCase().includes(mf))
&& (!hf  || o.host.toLowerCase().includes(hf))
&& (!tf  || hay.includes(tf));
tr.style.display = show ? '' : 'none';
});
autoAddObservedCandidates();
updateKPIs();
renderRepeatedHints();
renderPatternMatches();
updateBulkHintBadge();
renderObservedPanel();
}
function updateKPIs(){
const all=getRows(), vis=all.filter(tr=>tr.style.display!=='none');
const t=document.getElementById('kpi_total'); const v=document.getElementById('kpi_visible');
const r=document.getElementById('kpi_rules');
if(t) t.textContent=all.length; if(v) v.textContent=vis.length;
if(r) r.textContent=Object.keys(injectionRules||{}).length;
}
function openDetailFromTr(tr){
const o=rowObj(tr), ov=document.getElementById('detail_overlay'); if(!ov) return;
document.getElementById('det_docid').textContent=o.docid||'';
document.getElementById('det_module').textContent=o.module||'';
document.getElementById('det_host').textContent=o.host||'(unknown)';
document.getElementById('det_src').textContent=o.src||'(unknown)';
renderJSONTreeFromObj(o.vObj||{}, document.getElementById('det_vars'));
ov.classList.add('active');
}
function closeDetail(){ const ov=document.getElementById('detail_overlay'); if(ov) ov.classList.remove('active'); }
function attachClicks(){
getRows().forEach(tr=>{
tr.addEventListener('click', (e)=>{ if(['BUTTON','INPUT','SELECT','A','TEXTAREA','LABEL'].includes(e.target.tagName)) return; openDetailFromTr(tr); });
});
}
function renderJSONTreeFromObj(obj, container){
if(!obj || typeof obj!=='object'){ container.textContent='(empty)'; return; }
container.innerHTML=''; container.appendChild(jsonNode(obj,'root'));
}
function jsonNode(value,key){
const wrap=document.createElement('div'); wrap.className='json-entry';
if(typeof value==='object' && value!==null){
const isArray=Array.isArray(value);
const details=document.createElement('details'); details.open=true;
const summary=document.createElement('summary');
const coll=document.createElement('span'); coll.className='json-collapser'; coll.textContent=isArray?'[]':'{}';
const k=document.createElement('span'); k.className='json-k'; k.textContent=key==='root'?(isArray?`Array[${value.length}]`:'Object'):key+':';
summary.appendChild(coll); summary.appendChild(k); details.appendChild(summary);
Object.keys(value).forEach(chKey=>{
const chWrap=document.createElement('div'); chWrap.style.marginLeft='16px'; chWrap.appendChild(jsonNode(value[chKey], chKey)); details.appendChild(chWrap);
});
wrap.appendChild(details);
} else {
const k=document.createElement('span'); k.className='json-k'; k.textContent=key==='root'?'':key+': ';
let v=document.createElement('span');
if(typeof value==='string'){ v.className='json-v-str'; v.textContent=JSON.stringify(value); }
else if(typeof value==='number'){ v.className='json-v-num'; v.textContent=String(value); }
else if(typeof value==='boolean'){ v.className='json-v-bool'; v.textContent=String(value); }
else if(value===null){ v.className='json-v-bool'; v.textContent='null'; }
wrap.appendChild(k); wrap.appendChild(v);
}
return wrap;
}
const LS_KEY = 'pf_injection_rules';
const LS_PRESETS_KEY = 'pf_injection_presets';
const LS_AUTO_KEY = 'pf_auto_added_rules';
let injectionRules = loadRules();
let presets = loadPresets();
let autoAdded = loadAutoAdded();
let tempOverlayRules = {};
let useTempOverlayOnExport = false;
function loadRules(){
const raw = localStorage.getItem(LS_KEY);
if(!raw) return {};
try { const obj = JSON.parse(raw); return (obj && typeof obj==='object') ? obj : {}; } catch(e){ return {}; }
}
function saveRules(){
try { localStorage.setItem(LS_KEY, JSON.stringify(injectionRules)); } catch(e){}
renderRulesList(); renderRepeatedHints(); renderPatternMatches(); updateBulkHintBadge(); renderObservedPanel();
}
function loadPresets(){
const raw = localStorage.getItem(LS_PRESETS_KEY);
if(!raw) return {};
try { const obj = JSON.parse(raw); return (obj && typeof obj==='object') ? obj : {}; } catch(e){ return {}; }
}
function savePresets(){ try { localStorage.setItem(LS_PRESETS_KEY, JSON.stringify(presets)); } catch(e){} renderPresetsList(); }
function loadAutoAdded(){
const raw = localStorage.getItem(LS_AUTO_KEY);
if(!raw) return {};
try { const obj = JSON.parse(raw); return (obj && typeof obj==='object') ? obj : {}; } catch(e){ return {}; }
}
function saveAutoAdded(){
try { localStorage.setItem(LS_AUTO_KEY, JSON.stringify(autoAdded)); } catch(e){}
}
function resolveValueToken(valStr){
const s = String(valStr).trim();
if (s === '') return '';
if (s.toLowerCase() === 'null') return null;
if (s.toLowerCase() === 'true') return true;
if (s.toLowerCase() === 'false') return false;
if (/^-?\d+$/.test(s)) { try { return parseInt(s,10); } catch(e){ return s; } }
const m = s.match(/^["'](.*)["']$/);
return m ? m[1] : s;
}
function setRule(key, value){
const k = normKey(key);
if(!k) return;
injectionRules[k] = resolveValueToken(value);
saveRules();
}
function removeRule(key){
const k = normKey(key);
delete injectionRules[k];
delete autoAdded[k];
saveAutoAdded();
saveRules();
}
function clearRules(){
injectionRules = {};
autoAdded = {};
saveAutoAdded();
saveRules();
}
function addAutoRule(nk, value){
if(!nk) return;
injectionRules[nk] = resolveValueToken(value);
autoAdded[nk] = true;
}
function exportRulesJSON(){
safeDownload(JSON.stringify(injectionRules, null, 2), tableId+'_injection_rules.json');
}
function importRulesJSON(ev){
const file = ev.target.files[0]; if(!file) return;
const reader = new FileReader();
reader.onload = function(){
try { const obj = JSON.parse(reader.result); if(obj && typeof obj==='object'){ injectionRules = obj; } } catch(e){}
saveRules();
ev.target.value = '';
};
reader.readAsText(file, 'utf-8');
}
function renderRulesList(){
const box = document.getElementById('inj_rules_list');
const search = (document.getElementById('inj_rule_search')||{value:''}).value.trim().toLowerCase();
if(!box) return;
const keys = Object.keys(injectionRules).sort().filter(k=>!search || k.toLowerCase().includes(search));
const rows = keys.map(k=>{
const v = injectionRules[k];
const autoTag = autoAdded[k] ? '<span class="pill auto-pill" title="Added automatically">auto</span>' : '';
return `<div style="display:grid;grid-template-columns: 1fr auto auto auto;gap:8px;margin-bottom:6px;align-items:center;">
<span class="muted">${k}</span>
<span>${JSON.stringify(v)}</span>
${autoTag}
<button class="btn" onclick="_dash_removeRule('${k}')">Remove</button>
</div>`;
});
box.innerHTML = rows.length ? rows.join('') : '<div class="muted">(no rules)</div>';
}
function applyRulesToObj(varsObj){
const out = {};
Object.keys(varsObj||{}).forEach(k=>{ out[k] = varsObj[k]; });
Object.keys(out).forEach(origKey=>{
const nk = normKey(origKey);
if(nk in injectionRules){
out[origKey] = injectionRules[nk];
}
});
Object.keys(out).forEach(origKey=>{
const nk = normKey(origKey);
if(nk in tempOverlayRules){
out[origKey] = tempOverlayRules[nk];
}
});
return out;
}
function renderPresetsList(){ const box = document.getElementById('inj_presets_list'); if(!box) return; const names = Object.keys(presets).sort();
box.innerHTML = names.length ? names.map(name=>(`<div style="display:flex;gap:6px;align-items:center;margin-bottom:6px;">
<span class="muted">${name}</span>
<button class="btn" onclick="_dash_loadPreset('${name}')">Load</button>
<button class="btn" onclick="_dash_deletePreset('${name}')">Delete</button>
</div>`)).join('') : '<div class="muted">(no presets)</div>';
}
function saveCurrentAsPreset(){ const name = (document.getElementById('inj_preset_name')||{value:''}).value.trim(); if(!name) return; presets[name] = injectionRules; savePresets(); }
function loadPreset(name){ const p = presets[name]; if(!p || typeof p!=='object') return; injectionRules = JSON.parse(JSON.stringify(p)); saveRules(); }
function deletePreset(name){ delete presets[name]; savePresets(); }
function collectVisibleKeys(){
const rows=getVisibleRowsOrdered();
const keysSet = new Set();
const byKey = {};
rows.forEach(o=>{
const obj = o.vObj || parseJSONSafe(o.varsjson || o.v) || {};
Object.keys(obj||{}).forEach(k=>{
keysSet.add(k);
byKey[k] = (byKey[k]||0)+1;
});
});
return { keys:Array.from(keysSet), freq:byKey };
}
function renderPatternMatches(){
const inp = document.getElementById('pattern_search');
const box = document.getElementById('pattern_results');
if(!inp || !box) return;
const q = (inp.value||'').toLowerCase().trim();
const {keys,freq} = collectVisibleKeys();
const filtered = q ? keys.filter(k=>k.toLowerCase().includes(q)) : [];
filtered.sort((a,b)=> (freq[b]||0)-(freq[a]||0) || a.localeCompare(b));
const rows = filtered.slice(0,200).map(k=>`<div style="display:flex;justify-content:space-between;gap:8px;margin-bottom:4px;"><span>${k}</span><span class="muted">x${freq[k]||1}</span></div>`);
box.innerHTML = rows.length ? rows.join('') : '<div class="muted">(no matches)</div>';
}
function applyPatternPreview(){
const q = (document.getElementById('pattern_search')||{value:''}).value.toLowerCase().trim();
const valStr = (document.getElementById('pattern_value')||{value:''}).value;
const val = resolveValueToken(valStr);
tempOverlayRules = {};
if(q){
const {keys} = collectVisibleKeys();
keys.forEach(k=>{
if(k.toLowerCase().includes(q)){
tempOverlayRules[normKey(k)] = val;
}
});
}
previewApply();
}
function togglePatternExport(){ const cb = document.getElementById('pattern_export_enable'); useTempOverlayOnExport = !!(cb && cb.checked); }
function getVisibleRowsOrdered(){ return getRows().filter(tr=>tr.style.display!=='none').map(tr=>rowObj(tr)); }
function isInjectionEnabled(){ const cb = document.getElementById('inj_enable'); return !!(cb && cb.checked); }
function compactJSONStringFromRow(o){
const src = o.varsjson && o.varsjson.trim() ? o.varsjson : (o.v ? o.v : "{}");
const obj = parseJSONSafe(src);
let finalObj = (obj && typeof obj==='object') ? obj : null;
const overlayActiveForExport = useTempOverlayOnExport;
if(finalObj && (isInjectionEnabled() || overlayActiveForExport)){
const stash = tempOverlayRules;
if(!overlayActiveForExport){ tempOverlayRules = {}; }
finalObj = applyRulesToObj(finalObj);
tempOverlayRules = stash;
}
if(finalObj){ try { return JSON.stringify(finalObj); } catch(e){} }
return String(src).replace(/\r?\n+/g, ' ').trim();
}
function safeDownload(content, filename){
const ts = new Date();
const pad = (n)=> String(n).padStart(2,'0');
const stamp = ts.getFullYear()+''+pad(ts.getMonth()+1)+''+pad(ts.getDate())+'_'+pad(ts.getHours())+''+pad(ts.getMinutes());
const base = filename.replace(/[\s\(\)]+/g,'_');
const name = base.replace(/__TABLE_ID__/g, tableId) + '_' + stamp;
const a=document.createElement('a');
a.href='text/plain;charset=utf-8,'+encodeURIComponent(content);
a.download=name;
a.click();
}
function exportVariablesPitchfork(){ const lines=getVisibleRowsOrdered().map(o=>compactJSONStringFromRow(o)); safeDownload(lines.join('\n'), '__TABLE_ID___variables_pitchfork.txt'); }
function exportDocIdsAligned(){ const lines=getVisibleRowsOrdered().map(o=>o.docid || ''); safeDownload(lines.join('\n'), '__TABLE_ID___doc_ids_aligned.txt'); }
function exportPitchforkPair(){
const rows=getVisibleRowsOrdered(), seen=new Set(), vOut=[], idOut=[];
for(const o of rows){
const vOne=compactJSONStringFromRow(o); const idOne=o.docid || '';
const key=vOne+'||'+idOne; if(seen.has(key)) continue; seen.add(key);
vOut.push(vOne); idOut.push(idOne);
}
safeDownload(vOut.join('\n'), '__TABLE_ID___variables_pitchfork.txt');
setTimeout(()=>safeDownload(idOut.join('\n'), '__TABLE_ID___doc_ids_aligned.txt'), 150);
}
function previewApply(){
getRows().forEach(tr=>{
if(tr.style.display==='none') return;
const o=rowObj(tr);
const pre = tr.querySelector('td:nth-child(3) pre');
if(!pre) return;
const obj = parseJSONSafe(o.varsjson || o.v) || {};
const applied = applyRulesToObj(obj);
try { pre.innerText = JSON.stringify(applied, null, 2); } catch(e){}
});
}
function previewApplyInjection(){ previewApply(); }
function resetPreview(){
tempOverlayRules = {};
useTempOverlayOnExport = false;
const cb1 = document.getElementById('pattern_export_enable'); if(cb1) cb1.checked = false;
getRows().forEach(tr=>{
const o=rowObj(tr);
const pre = tr.querySelector('td:nth-child(3) pre');
if(!pre) return;
const src = o.varsjson && o.varsjson.trim() ? o.varsjson : (o.v ? o.v : "{}");
pre.innerText = src;
});
}
function renderRepeatedHints(){
const box = document.getElementById('inj_repeated_hints'); if(!box) return;
const rows = getVisibleRowsOrdered();
const freq = {};
rows.forEach(o=>{
const obj = o.vObj || parseJSONSafe(o.varsjson || o.v) || {};
Object.keys(obj||{}).forEach(k=>{
const nk = normKey(k);
if(!nk) return;
freq[nk] = freq[nk] || { origSet: new Set(), count: 0 };
freq[nk].count += 1;
freq[nk].origSet.add(k);
});
});
const entries = Object.keys(freq).map(nk=>({nk, count:freq[nk].count, covered: (nk in injectionRules), examples: Array.from(freq[nk].origSet).slice(0,5)}));
entries.sort((a,b)=> b.count - a.count || a.nk.localeCompare(b.nk));
const top = entries.filter(e=>e.count>1).slice(0,50);
const rowsHtml = top.length ? top.map(e=>{
const cls = e.covered ? 'hint-ok' : 'hint-miss';
const status = e.covered ? 'covered' : 'missing';
const ex = e.examples.join(', ');
const autoTag = autoAdded[e.nk] ? ' · <span class="hint-ok" title="Auto-added">auto</span>' : '';
return `<tr><td>${ex}</td><td>${e.count}</td><td class="${cls}">${status}${autoTag}</td><td><button class="btn" onclick="_dash_setRule('${e.nk}', (document.getElementById('inj_quick_value')||{value:''}).value || '1234')">Add rule</button></td></tr>`;
}).join('') : '<tr><td colspan="4" class="muted">(no repeats among visible rows)</td></tr>';
box.innerHTML = `<table class="hint-table"><thead><tr><th>Variable examples</th><th>Count</th><th>Status</th><th>Action</th></tr></thead><tbody>${rowsHtml}</tbody></table>`;
}
function collectObservedCandidates(){
const observed = window.__OBSERVED__ || {};
const {keys} = collectVisibleKeys();
const presentNKs = new Set(keys.map(k=>normKey(k)));
const candidates = [];
const byNkOrig = {};
keys.forEach(k=>{
const nk = normKey(k);
if(!nk) return;
(byNkOrig[nk] = byNkOrig[nk] || []).push(k);
});
Object.keys(observed).forEach(nk=>{
const info = observed[nk];
if(!info || typeof info.value === 'undefined' || info.value === null) return;
if(presentNKs.has(nk)){
const origs = byNkOrig[nk] || [nk];
const displayKey = origs[0];
const values = Array.isArray(info.values) ? info.values : [{v:info.value,c:info.count||1}];
candidates.push({key: displayKey, nk, top: info.value, count: info.count||0, values});
}
});
candidates.sort((a,b)=> (b.count - a.count) || a.key.localeCompare(b.key));
return candidates;
}
function autoAddObservedCandidates(){
const candidates = collectObservedCandidates();
const missing = candidates.filter(c=>!(c.nk in injectionRules));
if(missing.length === 0) return;
missing.forEach(c=>{
addAutoRule(c.nk, c.top);
});
saveAutoAdded();
saveRules();
}
function updateBulkHintBadge(){
const badge = document.getElementById('bulk_hint_badge');
if(!badge) return;
const candidates = collectObservedCandidates();
const uncovered = candidates.filter(c=>!(c.nk in injectionRules));
if(uncovered.length > 0){
badge.style.display = 'inline-flex';
const countEl = badge.querySelector('.count');
if(countEl) countEl.textContent = String(uncovered.length);
} else {
badge.style.display = 'none';
}
}
function onBulkHintClick(){
const candidates = collectObservedCandidates().filter(c=>!(c.nk in injectionRules));
if(candidates.length === 0) return;
candidates.forEach(c=>addAutoRule(c.nk, c.top));
saveAutoAdded();
saveRules();
}
function renderObservedPanel(){
const box = document.getElementById('observed_panel'); if(!box) return;
const list = collectObservedCandidates();
if(list.length === 0){
box.innerHTML = '<div class="muted">(no live intersections with visible output variables)</div>';
document.getElementById('observed_count').textContent = '0';
updateObservedSummary();
return;
}
const htmlRows = list.map(item=>{
const covered = (item.nk in injectionRules);
const autoTag = autoAdded[item.nk] ? ' <span class="pill auto-pill" title="Added automatically">auto</span>' : '';
const coverBadge = covered ? `<span class="hint-ok" title="In rules">covered</span>${autoTag}` : `<span class="hint-miss" title="Not in rules">missing</span>`;
const select = `<select class="observed-select" data-nk="${item.nk}" id="obs_sel_${item.nk}">
${item.values.map(it=>`<option value="${it.v}">${it.v} (x${it.c})</option>`).join('')}
</select>`;
return `<div class="observed-row">
<div class="observed-key">${item.key}</div>
<div class="observed-count">seen: x${item.count} · ${coverBadge}</div>
<div>${select}</div>
<div class="observed-actions">
<button class="btn" onclick="_dash_obsAdd('${item.nk}', '${item.key}')">Add</button>
<button class="btn" onclick="_dash_obsPreview('${item.nk}')">Preview</button>
</div>
<div class="observed-actions">
<button class="btn" onclick="_dash_obsUpdate('${item.nk}', '${item.key}')">Add/Update</button>
<button class="btn" onclick="_dash_obsReset('${item.nk}')">Reset</button>
</div>
</div>`;
}).join('');
box.innerHTML = htmlRows;
document.getElementById('observed_count').textContent = list.length;
updateObservedSummary();
}
function getSelectedValue(nk){
const sel = document.getElementById('obs_sel_'+nk);
if(!sel) return null;
return sel.value;
}
function obsAdd(nk, displayKey){
const v = getSelectedValue(nk);
if(v === null) return;
setRule(displayKey, v);
autoAdded[normKey(displayKey)] = true;
saveAutoAdded();
saveRules();
}
function obsUpdate(nk, displayKey){
const v = getSelectedValue(nk);
if(v === null) return;
setRule(displayKey, v);
}
function obsPreview(nk){
const v = getSelectedValue(nk);
if(v === null) return;
tempOverlayRules[nk] = resolveValueToken(v);
previewApply();
}
function obsReset(nk){
delete tempOverlayRules[nk];
previewApply();
}
function obsPreviewAll(){
const list = collectObservedCandidates();
tempOverlayRules = {};
list.forEach(item=>{
const v = (getSelectedValue(item.nk) ?? item.top);
tempOverlayRules[item.nk] = resolveValueToken(v);
});
previewApply();
}
function autoAddAll(){
const candidates = collectObservedCandidates().filter(c=>!(c.nk in injectionRules));
candidates.forEach(c=>{
addAutoRule(c.nk, c.top);
});
saveAutoAdded();
saveRules();
renderObservedPanel();
updateBulkHintBadge();
}
function updateObservedSummary(){
const candidates = collectObservedCandidates();
const covered = candidates.filter(c=>c.nk in injectionRules).length;
const total = candidates.length;
const pending = total - covered;
document.getElementById('total_observed').textContent = total || 0;
document.getElementById('covered_count').textContent = covered || 0;
document.getElementById('pending_count').textContent = pending || 0;
}
function toggleObservedSection(){
const container = document.getElementById('observed_scroll_container');
const toggle = document.querySelector('.observed-section-toggle');
container.style.display = container.style.display === 'none' ? 'block' : 'none';
toggle.classList.toggle('active');
}
window._dash_applyFilters=applyFilters;
window._dash_exportVariablesPitchfork=exportVariablesPitchfork;
window._dash_exportDocIdsAligned=exportDocIdsAligned;
window._dash_exportPitchforkPair=exportPitchforkPair;
window._dash_closeDetail=closeDetail;
window._dash_setRule=setRule;
window._dash_removeRule=removeRule;
window._dash_clearRules=clearRules;
window._dash_previewApplyInjection=previewApplyInjection;
window._dash_resetPreview=resetPreview;
window._dash_savePreset=saveCurrentAsPreset;
window._dash_loadPreset=loadPreset;
window._dash_deletePreset=deletePreset;
window._dash_exportRulesJSON=exportRulesJSON;
window._dash_importRulesJSON=importRulesJSON;
window._dash_renderPatternMatches=renderPatternMatches;
window._dash_applyPatternPreview=applyPatternPreview;
window._dash_togglePatternExport=togglePatternExport;
window._dash_onBulkHintClick=onBulkHintClick;
window._dash_obsAdd=obsAdd;
window._dash_obsUpdate=obsUpdate;
window._dash_obsPreview=obsPreview;
window._dash_obsReset=obsReset;
window._dash_obsPreviewAll=obsPreviewAll;
window._dash_autoAddAll=autoAddAll;
document.addEventListener('DOMContentLoaded', function(){
autoAddObservedCandidates();
updateKPIs(); attachClicks();
renderRulesList(); renderPresetsList(); renderRepeatedHints();
renderPatternMatches();
updateBulkHintBadge();
renderObservedPanel();
});
})();
</script>
</head>
<body>
<div class="bg-logo" aria-hidden="true"></div>
<div class="app-root">
<div class="banner">
<div class="banner-content">
<div class="brand-left">
<div class="brand-logo">
<img src="__LOGO_PATH__" alt="XVISOR03 Logo" class="brand-logo-img">
<div class="brand-text">
<div class="brand-name">XVISOR03</div>
<div class="brand-page">__TITLE__</div>
</div>
</div>
<div class="brand-sub">__SUBTITLE__</div>
</div>
<div class="stats-row">
<div class="kpi-card">
<div class="kpi-label">Total Queries</div>
<div class="kpi-value" id="kpi_total">0</div>
<div class="kpi-trend positive"><i class="fas fa-arrow-up"></i> Detected</div>
</div>
<div class="kpi-card">
<div class="kpi-label">Active Session</div>
<div class="kpi-value" id="kpi_visible">0</div>
<div class="kpi-trend"><i class="fas fa-eye"></i> Visible items</div>
</div>
<div class="kpi-card">
<div class="kpi-label">Injection Rules</div>
<div class="kpi-value" id="kpi_rules">0</div>
<div class="kpi-trend positive"><i class="fas fa-bolt"></i> Auto-applied</div>
</div>
</div>
</div>
</div>

<div class="controls-section">
<div class="section-header">
<div class="section-title"><i class="fas fa-filter"></i> Query Filters</div>
</div>
<div class="toolbar">
<div class="toolbar-group">
<div class="toolbar-label"><i class="fas fa-barcode"></i> Doc ID</div>
<input id="filter_docid" placeholder="Filter by doc_id..." oninput="_dash_applyFilters()">
</div>
<div class="toolbar-group">
<div class="toolbar-label"><i class="fas fa-cube"></i> Module Name</div>
<input id="filter_module" placeholder="Filter by module name..." oninput="_dash_applyFilters()">
</div>
<div class="toolbar-group">
<div class="toolbar-label"><i class="fas fa-globe"></i> Host</div>
<input id="filter_host" placeholder="Filter by host (e.g., adsmanager.facebook.com)..." oninput="_dash_applyFilters()">
</div>
<div class="toolbar-group">
<div class="toolbar-label"><i class="fas fa-search"></i> Full Text</div>
<input id="filter_text" placeholder="Search in variables and metadata..." oninput="_dash_applyFilters()">
</div>
</div>
<div class="toolbar-buttons">
<button class="btn btn-primary" onclick="_dash_exportVariablesPitchfork()"><i class="fas fa-file-export"></i> Export Variables (Pitchfork)</button>
<button class="btn" onclick="_dash_exportDocIdsAligned()"><i class="fas fa-file-alt"></i> Export Doc IDs</button>
<button class="btn" onclick="_dash_exportPitchforkPair()"><i class="fas fa-project-diagram"></i> Export Pitchfork Pair</button>
</div>
</div>

<div class="dash-grid">
<div class="panel-section">
<div class="panel-card">
<div class="section-header">
<div class="section-title"><i class="fas fa-brain"></i> Injection Rules & Presets</div>
</div>
<div class="card-content">
<div class="input-row">
<div>
<div class="toolbar-label"><i class="fas fa-key"></i> Variable Key</div>
<input id="inj_key" placeholder="Variable key (e.g., actor_id, pageID)">
</div>
<div>
<div class="toolbar-label"><i class="fas fa-value"></i> Value</div>
<input id="inj_value" placeholder='Value (e.g., 1234 or "abc")'>
</div>
</div>
<div class="btn-group">
<button class="btn btn-primary" onclick="_dash_setRule(document.getElementById('inj_key').value, document.getElementById('inj_value').value)"><i class="fas fa-plus"></i> Add/Update Rule</button>
<button class="btn" onclick="_dash_clearRules()"><i class="fas fa-trash"></i> Clear All Rules</button>
<div style="display:flex; align-items:center; gap:8px; margin:0 10px">
<input type="checkbox" id="inj_enable" style="width:18px; height:18px">
<label for="inj_enable" style="font-size:14px">Use injection on export</label>
</div>
</div>
<div class="input-row">
<div>
<div class="toolbar-label"><i class="fas fa-search"></i> Search Rules</div>
<div class="search-box">
<i class="fas fa-search search-icon"></i>
<input id="inj_rule_search" placeholder="Search rules..." oninput="(function(){ _dash_applyFilters(); })()">
</div>
</div>
<div style="display:flex; gap:10px; margin-top:24px">
<button class="btn" onclick="_dash_exportRulesJSON()"><i class="fas fa-download"></i> Export Rules JSON</button>
<label class="btn" style="cursor:pointer;">
<i class="fas fa-upload"></i> Import Rules JSON
<input type="file" accept=".json,application/json" style="display:none" onchange="_dash_importRulesJSON(event)">
</label>
</div>
</div>
<div id="inj_rules_list" class="block" style="margin-top:16px; max-height:220px; overflow:auto;"></div>
</div>
</div>

<div class="panel-card">
<div class="section-header">
<div class="section-title"><i class="fas fa-save"></i> Rule Presets</div>
</div>
<div class="card-content">
<div class="input-row">
<div>
<div class="toolbar-label"><i class="fas fa-tag"></i> Preset Name</div>
<input id="inj_preset_name" placeholder="Preset name (e.g., Production IDs, Test Accounts)">
</div>
<div style="display:flex; align-items:end">
<button class="btn btn-primary" onclick="_dash_savePreset()" style="height:42px; margin-bottom:6px"><i class="fas fa-save"></i> Save Current Rules</button>
</div>
</div>
<div id="inj_presets_list" class="block" style="margin-top:16px; max-height:180px; overflow:auto;"></div>
</div>
</div>

<div class="panel-card">
<div class="section-header">
<div class="section-title"><i class="fas fa-chart-bar"></i> Variable Insights</div>
</div>
<div class="card-content">
<div class="toolbar-label" style="margin-bottom:8px"><i class="fas fa-lightbulb"></i> Quick Value for New Rules</div>
<input id="inj_quick_value" placeholder='e.g., 1234 or "test_value"' style="margin-bottom:16px">
<div id="inj_repeated_hints" class="block" style="max-height:240px; overflow:auto;"></div>
</div>
</div>
</div>

<div class="panel-section">
<div class="panel-card">
<div class="section-header">
<div class="section-title"><i class="fas fa-magic"></i> Pattern Injection</div>
</div>
<div class="card-content">
<div class="input-row">
<div>
<div class="toolbar-label"><i class="fas fa-search"></i> Pattern Search</div>
<input id="pattern_search" placeholder='Type substring (e.g., "id" or "page")' oninput="_dash_renderPatternMatches()">
</div>
<div>
<div class="toolbar-label"><i class="fas fa-magic"></i> Replacement Value</div>
<input id="pattern_value" placeholder='Set value for all matches (e.g., 1234 or "x")'>
</div>
</div>
<button class="btn btn-primary" onclick="_dash_applyPatternPreview()" style="margin:16px 0"><i class="fas fa-eye"></i> Apply to Visible (Preview)</button>
<div style="display:flex; align-items:center; gap:12px; padding:12px; background:rgba(31,36,48,0.3); border-radius:10px; margin-top:8px">
<input type="checkbox" id="pattern_export_enable" onclick="_dash_togglePatternExport()" style="width:18px; height:18px">
<label for="pattern_export_enable" style="font-size:14px">Use pattern overlay on export (no raw change)</label>
</div>
<div class="section-header" style="margin-top:20px; padding-top:12px">
<div class="section-title"><i class="fas fa-list"></i> Pattern Matches</div>
</div>
<div id="pattern_results" class="block" style="margin-top:12px; max-height:180px; overflow:auto;"></div>
</div>
</div>

<div class="panel-card">
<div class="section-header">
<div class="section-title"><i class="fas fa-bolt"></i> Live Variable Hints</div>
<span class="hint-badge" id="bulk_hint_badge" style="display:none;">
<span class="dot"></span><span>Auto-hints available: <span class="count">0</span></span>
</span>
</div>
<div class="card-content">
<div style="display:flex; gap:10px; margin-bottom:12px">
<button class="btn" onclick="_dash_obsPreviewAll()"><i class="fas fa-eye"></i> Preview All</button>
<button class="btn" onclick="_dash_resetPreview()"><i class="fas fa-undo"></i> Reset Preview</button>
<button class="btn" onclick="_dash_autoAddAll()"><i class="fas fa-magic"></i> Auto-Add All</button>
</div>
<div class="observed-section-toggle active" onclick="toggleObservedSection()">
<i class="fas fa-chevron-down"></i>
<span>Observed in live /api/graphql (<span id="observed_count">0</span> intersections)</span>
</div>
<div class="observed-scroll-container" id="observed_scroll_container">
<div class="observed-panel" id="observed_panel"></div>
</div>
<div class="observed-summary">
<div class="summary-item">
<span class="summary-label">Total observed variables:</span>
<span class="summary-value" id="total_observed">0</span>
</div>
<div class="summary-item">
<span class="summary-label">Covered by rules:</span>
<span class="summary-value" id="covered_count">0</span>
</div>
<div class="summary-item">
<span class="summary-label">Pending coverage:</span>
<span class="summary-value" id="pending_count">0</span>
</div>
</div>
</div>
</div>
</div>
</div>

<div class="data-panel">
<div class="section-header">
<div class="section-title"><i class="fas fa-database"></i> GraphQL Query Repository</div>
</div>
<table id="__TABLE_ID__">
<thead>
<tr>
<th style="width:5%">#</th>
<th style="width:15%">Doc ID</th>
<th style="width:40%">Variables (JSON)</th>
<th style="width:20%">Module</th>
<th style="width:20%">Host</th>
</tr>
</thead>
<tbody>
"""
    return (tpl.replace("__TITLE__", html.escape(title))
        .replace("__SUBTITLE__", html.escape(subtitle))
        .replace("__TABLE_ID__", table_id)
        .replace("__PAGE_KIND__", page_kind)
        .replace("__OBSERVED_JSON__", observed_json)
        .replace("__LOGO_PATH__", html.escape(LOGO_DATA_URL)))

def _html_footer():
    return """
</tbody>
</table>
</div>
<div id="detail_overlay" onclick="_dash_closeDetail()">
<div class="detail_card" onclick="event.stopPropagation()">
<div class="detail_header">
<div class="pill"><span class="dot" style="background:#10b981;"></span><span class="label">Doc ID: <span id="det_docid"></span></span></div>
<div class="pill"><span class="dot" style="background:#38bdf8;"></span><span class="label">Module: <span id="det_module"></span></span></div>
<div class="host-pill"><span class="dot" style="background:#f59e0b;"></span><span class="label">Host: <span id="det_host"></span></span></div>
<div class="src-pill"><span class="dot" style="background:#f59e0b;"></span><span class="label">Source: <span id="det_src"></span></span></div>
<button class="btn btn-close" onclick="_dash_closeDetail()">Close</button>
</div>
<div class="detail_body">
<div class="block">
<div class="block-title">Variables</div>
<div id="det_vars" class="json-tree"></div>
</div>
<div class="block">
<div class="block-title">Notes</div>
<div class="muted">- Collapsible JSON tree.<br>- Injection applies on export/preview only; raw data remains intact.<br>- Pattern overlays and observed bulk-hints can be previewed/reset easily.<br>- Host and source show target domain and the statics file URL containing the query.</div>
</div>
</div>
</div>
</div>
</div>
</div>
</body>
</html>
"""

def _row_html(idx, doc_id, variables, module, host="", src=""):
    vars_str = json.dumps(variables, ensure_ascii=False, indent=2) if isinstance(variables, dict) else str(variables)
    return (
        f"<tr data-module=\"{html.escape(module)}\" data-varsjson=\"{html.escape(vars_str)}\" data-host=\"{html.escape(host or '')}\" data-src=\"{html.escape(src or '')}\">"
        f"<td>{idx}</td>"
        f"<td>{html.escape(str(doc_id))}</td>"
        f"<td><pre>{html.escape(vars_str)}</pre></td>"
        f"<td class='muted'>{html.escape(module)}</td>"
        f"<td class='muted'>{html.escape(host or '')}</td>"
        "</tr>\n"
    )

def _render_html(items, path, page_kind):
    title = "graphql_harvester - Repository" if page_kind == "repo" else "graphql_harvester - Session"
    table_kind = "repo" if page_kind == "repo" else "session"
    with open(path, "w", encoding="utf-8") as f:
        f.write(_html_header(title, "#e02424", subtitle="By Hasan Habeeb", page_kind=table_kind))
        for i, it in enumerate(items, start=1):
            f.write(_row_html(i, it["doc_id"], it["variables"], it.get("module", ""), it.get("host", ""), it.get("src", "")))
        f.write(_html_footer())
