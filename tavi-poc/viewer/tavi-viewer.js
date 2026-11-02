"use strict";
// WORK Candidate: use repository discovery for future instance/*.json files;
// explicitly registered pairings avoid inferring a normative binding from filenames.
const REPOSITORY = "pontsoleil/XBRL_GL_Next";
const BRANCH = "main";
const KNOWN = {
  "tavi-ins.json": {taxonomy:"tavi-tax.json",csv:"tavi-ins.csv"},
  "tavi-uuid-ins.json": {taxonomy:"tavi-uuid-tax.json",csv:"tavi-uuid-ins.csv"}
};
const $ = id => document.getElementById(id);
const base = new URL("../", document.currentScript.src);
const asset = (dir, name) => new URL(`${dir}/${encodeURIComponent(name)}`, base);
const state = {active:"template", file:"", values:null, request:0};
async function readText(url){const r=await fetch(url,{cache:"no-cache"});if(!r.ok)throw new Error(`${url.pathname}: HTTP ${r.status}`);return r.text();}
function setStatus(message,error=false){$("status").textContent=` ${message}`;$("status").className=error?"status error":"status";}
function parseCSV(text){
 const rows=[];let row=[],field="",quoted=false;
 for(let p=0;p<text.length;p++){const c=text[p];
  if(quoted){if(c==='"' && text[p+1]==='"'){field+='"';p++;}else if(c==='"'){quoted=false;}else{field+=c;}}
  else if(c==='"'){quoted=true;}else if(c===','){row.push(field);field="";}
  else if(c==='\n'||c==='\r'){if(c==='\r'&&text[p+1]==='\n')p++;row.push(field);rows.push(row);row=[];field="";}
  else{field+=c;}}
 if(field!==""||row.length){row.push(field);rows.push(row);}if(quoted)throw new Error("CSV has an unclosed quoted field");
 return rows;
}
function transposeCSV(text){const target=$("csv");target.replaceChildren();const rows=parseCSV(text);if(!rows.length)return;
 const table=document.createElement("table");const thead=document.createElement("thead");const thr=document.createElement("tr");
 for(let c=0;c<rows.length;c++){let th=document.createElement("th");th.textContent=c===0?"Item":`Record ${c}`;thr.append(th);}thead.append(thr);table.append(thead);
 const body=document.createElement("tbody"),max=Math.max(...rows.map(r=>r.length));
 for(let k=0;k<max;k++){let tr=document.createElement("tr");for(let c=0;c<rows.length;c++){const cell=document.createElement(c===0?"th":"td");cell.textContent=rows[c][k]??"";tr.append(cell);}body.append(tr);}table.append(body);target.append(table);
 $("csv-name").textContent=`${state.values.csvFile} · ${Math.max(0,rows[0].length)} columns × ${rows.length-1} records (transposed)`;
}
function showTab(){document.querySelectorAll("[data-tab]").forEach(b=>b.setAttribute("aria-selected",String(b.dataset.tab===state.active)));
 if(!state.values)return;const v=state.values;
 const names={template:`taxonomy/${v.taxFile} · xbrlModel.tableTemplates`,taxonomy:`taxonomy/${v.taxFile}`,schema:"taxonomy/tavi-schema.json"};
 $("source-name").textContent=names[state.active];$("source").textContent=state.active==="template"?JSON.stringify(v.tax.xbrlModel?.tableTemplates??[],null,2):state.active==="taxonomy"?v.taxText:v.schemaText;
}
async function load(name){const pair=KNOWN[name];if(!pair){setStatus(`No approved taxonomy/CSV pairing for ${name}`,true);return;}
 state.file=name;const req=++state.request;setStatus("Loading...");$("source").textContent="";$("csv").replaceChildren();
 try{const [instText,taxText,schemaText,csvText]=await Promise.all([
 readText(asset("instance",name)),readText(asset("taxonomy",pair.taxonomy)),readText(asset("taxonomy","tavi-schema.json")),readText(asset("instance",pair.csv))]);
 if(req!==state.request)return;
 const inst=JSON.parse(instText),tax=JSON.parse(taxText),schema=JSON.parse(schemaText);
 if(!schema || typeof schema!=="object")throw Error("JSON Schema cannot be read");
 state.values={inst,tax,taxText,schemaText,csvText,taxFile:pair.taxonomy,csvFile:pair.csv};transposeCSV(csvText);showTab();setStatus("Loaded");
 }catch(e){if(req!==state.request)return;setStatus(String(e.message??e),true);$("source").textContent="Unable to load the selected source files.";}}
async function discover(){
 // GitHub API discovery is optional; metadata must never silently replace an approved pairing.
 // In offline/local preview, known names remain available.
 let names=Object.keys(KNOWN);
 try{const endpoint=`https://api.github.com/repos/${REPOSITORY}/contents/tavi-poc/instance?ref=${BRANCH}`;
 const r=await fetch(endpoint,{headers:{Accept:"application/vnd.github+json"}});
 if(r.ok){const listing=await r.json();if(Array.isArray(listing)){const found=listing.filter(x=>x.type==="file"&&x.name.endsWith(".json")).map(x=>x.name);names=[...new Set([...names,...found])].sort();}}
 }catch(_e){}const select=$("instance");select.replaceChildren();
 for(const n of names){const op=document.createElement("option");op.value=n;op.textContent=n+(KNOWN[n]?"":" (mapping not configured)");select.append(op);}
 select.value=names.includes("tavi-uuid-ins.json")?"tavi-uuid-ins.json":names[0];await load(select.value);
}
document.querySelectorAll("[data-tab]").forEach(b=>b.addEventListener("click",()=>{state.active=b.dataset.tab;showTab();}));
$("instance").addEventListener("change",e=>load(e.target.value));
discover();
