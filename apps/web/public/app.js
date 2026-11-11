'use strict';
const $ = (s) => document.querySelector(s);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const session = crypto.randomUUID();
let data = null, source = null, selected = 0, name = 'Untitled integration';
const decisions = new Map(), records = new Map();
function notice(message='') { $('#notice').textContent = message; }
async function api(path, body) {
  const response = await fetch(path, body ? {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)} : {});
  const result = await response.json();
  if (!response.ok) throw new Error(typeof result.detail === 'string' ? result.detail : 'Check the file format and required fields.');
  return result;
}
function count() { return data?.candidates.length ?? 0; }
function title(kicker, heading, description, action='') { return `<div class="heading"><div><div class="eyebrow">${kicker}</div><h1>${heading}</h1><p class="sub">${description}</p></div>${action}</div>`; }
function empty() { return `<div class="empty"><h2>A source is your starting point.</h2><p>Import an OpenAPI document to discover its fields and propose mappings.</p><a class="btn primary" href="#discover">Import a source ↗</a></div>`; }
function render() {
  const page = location.hash.slice(1) || 'overview';
  document.querySelectorAll('nav a').forEach(a=>a.classList.toggle('active',a.dataset.page===page));
  $('#breadcrumb').textContent = `${name} / ${page === 'review' ? 'Field review' : page[0].toUpperCase()+page.slice(1)}`;
  $('#projectName').firstChild.textContent = `${name} `;
  $('#navCount').textContent = count()-decisions.size;
  if (page==='discover') discovery(); else if(page==='review') review(); else if(page==='mappings') mappings(); else overview();
}
function overview() {
  $('#content').innerHTML = title('INTEGRATION / 001', data ? 'Your source, taking shape.' : 'Make unfamiliar APIs<br>feel familiar.', 'A place to understand a source, resolve the uncertain fields, and build a mapping you can stand behind.') +
  `<div class="hero"><div><div class="eyebrow">${data?'NEXT UP / FIELD REVIEW':'START WITH YOUR SOURCE'}</div><h2>${data?esc(name):'Bring the API. We’ll lay it out.'}</h2><p>${data?`${count()} fields discovered. Inspect the evidence and decide where each one belongs.`:'Upload an OpenAPI document and sample responses, or explore a clearly labelled example integration.'}</p><a class="btn" href="#${data?'review':'discover'}">${data?'Review fields':'Set up your source'} ↗</a></div><div class="crossing" aria-hidden="true"><i></i><i></i><i></i><i></i></div></div>` +
  `<div class="stats"><div class="stat"><strong>${count()}</strong><small>Discovered fields</small></div><div class="stat"><strong>${count()-decisions.size}</strong><small>Awaiting your review</small></div><div class="stat"><strong>${decisions.size}</strong><small>Recorded decisions</small></div></div><div class="steps"><div class="step"><small>01 / UNDERSTAND</small><h3>Start with the source</h3><p>Endpoints, types, descriptions, and sample patterns in one place.</p></div><div class="step"><small>02 / DECIDE</small><h3>Give every field a home</h3><p>Compare suggested targets and inspect the evidence behind them.</p></div><div class="step"><small>03 / TAKE IT WITH YOU</small><h3>Keep a decision record</h3><p>Export your reviewed choices with their rationale for the next integration step.</p></div></div>`;
}
function discovery() {
  $('#content').innerHTML = title('SOURCE / DISCOVERY','Get to know the source.','Import a JSON OpenAPI document. Optional sample responses help identify dates, identifiers, and value patterns.') +
  `<div class="grid"><form id="importForm" class="panel"><h2>Your API, unpacked.</h2><label for="integrationName">Integration name</label><input id="integrationName" value="${esc(name==='Untitled integration'?'':name)}" placeholder="e.g. Northstar claims"><label for="specFile">OpenAPI document · JSON</label><input id="specFile" type="file" accept=".json,application/json" required><label for="sampleFile">Sample responses · JSON array · optional</label><input id="sampleFile" type="file" accept=".json,application/json"><p class="sub">Use sanitized samples. Files are processed by your local backend. Up to 200 response objects.</p><button class="btn primary" type="submit">Discover fields ↗</button></form><div class="panel"><div class="eyebrow">TAKE A LOOK AROUND</div><h2 style="margin-top:20px">Try a claims integration.</h2><p class="sub">A synthetic API with claim identifiers, policy details, dates, and financial fields. Uses the same discovery and mapping pipeline as your own files.</p><button id="example" class="btn">Load example source ↗</button><hr style="border:0;border-top:1px solid var(--line);margin:30px 0"><h3>What happens after import?</h3><p class="sub">Choose an endpoint, inspect its response fields, then review their proposed matches to the built-in Claim model.</p></div></div><div id="discoveryResults"></div>`;
  $('#importForm').onsubmit = async e => {
    e.preventDefault(); const button=e.submitter; button.disabled=true; notice('Reading and analyzing your source…');
    try {
      const spec = $('#specFile').files[0], sample=$('#sampleFile').files[0];
      if(spec.size+(sample?.size||0)>800000) throw new Error('Choose files smaller than 800 KB combined for this local preview.');
      source={spec:JSON.parse(await spec.text()),samples:sample?JSON.parse(await sample.text()):[]};
      if(!Array.isArray(source.samples)) throw new Error('Samples must be a JSON array of response objects.');
      name=$('#integrationName').value.trim()||spec.name; await analyze();
    } catch(error){notice(error.message);} finally{button.disabled=false;}
  };
  $('#example').onclick = async e => {e.target.disabled=true;notice('Discovering the example API…');try{source=await api('/workbench/example');name='Example · Claims API';await analyze();}catch(error){notice(error.message);e.target.disabled=false;}};
  if(data) showDiscovery();
}
async function analyze() {
  data=await api('/workbench/analyze',source); selected=0; decisions.clear();records.clear();notice('Source analyzed. Choose an endpoint below, then open field review.');render();
}
function showDiscovery() {
  const endpoints=data.catalog.endpoints.filter(e=>e.response_fields.length);
  $('#discoveryResults').innerHTML=`<div class="panel" style="margin-top:24px"><div class="heading"><h2>${count()} fields ready to inspect</h2><a href="#review" class="btn primary">Open field review ↗</a></div><label for="endpoint">Response endpoint</label><select id="endpoint">${endpoints.map((e,i)=>`<option value="${i}" ${e.path===data.endpoint.path&&e.method===data.endpoint.method?'selected':''}>${esc(e.method+' '+e.path)}</option>`).join('')}</select><p class="sub">${esc(data.endpoint.summary||'Response schema')} · ${source.samples.length} sample responses supplied</p><details><summary>Schema notes and unsupported constructs</summary><pre style="white-space:pre-wrap">${esc(JSON.stringify(data.catalog.unsupported ?? data.catalog.unsupported_constructs ?? [],null,2))}</pre></details></div>`;
  $('#endpoint').onchange=async e=>{const endpoint=endpoints[Number(e.target.value)];source={...source,path:endpoint.path,method:endpoint.method,samples:[]};notice('Analyzing endpoint…');try{await analyze();notice('Endpoint changed. Samples were cleared because response shapes may differ.');}catch(error){notice(error.message);}};
}
function review() {
  $('#content').innerHTML=title('MAPPING / FIELD REVIEW','A little scrutiny.<br>A better integration.','Inspect the source evidence, choose a target, and record your reasoning. Scores describe heuristic matches, not probabilities.') + (!data?empty():`<div class="toolbar"><input id="search" placeholder="Find a source field…" aria-label="Search fields"><select id="filter" aria-label="Filter decisions"><option value="all">All fields</option><option value="pending">Awaiting review</option><option value="done">Decided</option></select></div><div class="review-layout"><div id="fields" class="fields"></div><div id="detail" class="panel"></div></div>`);
  if(!data)return;
  $('#search').oninput=fieldList;$('#filter').onchange=fieldList;fieldList();detail();
}
function fieldList() {
  const query=$('#search').value.toLowerCase(), filter=$('#filter').value;
  const rows=data.candidates.map((c,i)=>({c,i})).filter(({c,i})=>c.external_path.toLowerCase().includes(query)&&(filter==='all'||(filter==='done')===decisions.has(i)));
  $('#fields').innerHTML=rows.length?rows.map(({c,i})=>`<button class="field ${i===selected?'selected':''}" data-index="${i}" aria-pressed="${i===selected}"><code>${esc(c.external_path)}</code><small>↳ ${esc(c.canonical_path||'No target proposed')}</small><span class="badge ${decisions.has(i)?'done':''}">${decisions.has(i)?esc(decisions.get(i).state):esc(c.status.replaceAll('_',' ').toLowerCase())}</span></button>`).join(''):'<p style="padding:20px">No fields match these filters.</p>';
  document.querySelectorAll('[data-index]').forEach(b=>b.onclick=()=>{selected=Number(b.dataset.index);fieldList();detail();});
}
function detail() {
  const c=data.candidates[selected], d=decisions.get(selected), field=data.endpoint.response_fields[selected];
  const signals=c.evidence?Object.entries(c.evidence):[];
  $('#detail').innerHTML=`<div class="eyebrow">SOURCE FIELD / ${selected+1} OF ${count()}</div><h2 style="margin-top:16px;overflow-wrap:anywhere">${esc(c.external_path)}</h2><p class="sub">${esc(field.description||'No description supplied in the source schema.')}</p><span class="badge">${esc(field.data_type)} · ${field.required?'required':'optional'}</span><h3>Why this match?</h3>${signals.length?signals.map(([key,v])=>`<div class="signal"><span>${esc(key.replaceAll('_',' '))} · ${v.score===null?'not available':Math.round(v.score*100)+'/100'}</span><p>${esc(v.reason)}</p></div>`).join(''):'<p class="sub">There isn’t enough evidence to propose a target. Inspect the schema and choose one explicitly.</p>'}<details><summary>Alternative targets (${c.alternatives.length})</summary>${c.alternatives.map(a=>`<p><code>${esc(a.canonical_path)}</code> · ${Math.round(a.score*100)}/100</p>`).join('')}</details>${d?`<div class="badge done">${esc(d.state)}</div><p>${esc(d.canonical_path||'No target selected')}</p><p class="sub">${esc(d.rationale)}</p>`:`<form id="decisionForm"><label for="target">Canonical target</label><select id="target"><option value="">Choose a target</option>${data.targets.map(t=>`<option ${t===c.canonical_path?'selected':''}>${esc(t)}</option>`).join('')}</select><label for="reviewer">Your name</label><input id="reviewer" required maxlength="100" autocomplete="name"><label for="reason">Reason for this decision</label><textarea id="reason" required maxlength="2000" placeholder="What makes this the right match?"></textarea><div class="actions"><button class="btn primary" name="action" value="approve">Save mapping</button><button class="btn" name="action" value="reject">Reject</button><button class="btn" name="action" value="unresolved">Leave unresolved</button></div></form>`}`;
  if(!d)$('#decisionForm').onsubmit=decide;
}
async function decide(e) {
  e.preventDefault();const index=selected,c=data.candidates[index], target=$('#target').value, action=e.submitter.value;
  if(action==='approve'&&!target){notice('Choose a canonical target before saving.');return;}
  const rationale=$('#reason').value.trim(), reviewer=$('#reviewer').value.trim();
  if(!rationale||!reviewer){notice('Enter your name and a reason.');return;}
  const buttons=[...$('#decisionForm').querySelectorAll('button')];buttons.forEach(b=>b.disabled=true);
  try {
    let record=records.get(index);
    if(!record){record=await api('/reviews',{tenant_id:session,review_id:crypto.randomUUID(),candidate:c});records.set(index,record);}
    const result=await api(`/reviews/${encodeURIComponent(record.review_id)}/decision`,{tenant_id:session,expected_version:record.version,reviewer_id:reviewer,rationale,canonical_path:action==='approve'?target:null,action:action==='approve'?(target===c.canonical_path?'CONFIRM':'CORRECT'):action==='reject'?'REJECT':'LEAVE_UNRESOLVED'});
    decisions.set(index,{...result,rationale,reviewer});notice('Decision recorded.');$('#navCount').textContent=count()-decisions.size;fieldList();detail();
  } catch(error){notice(error.message);buttons.forEach(b=>b.disabled=false);}
}
function mappings() {
  $('#content').innerHTML=title('RECORD / DECISIONS','The choices behind the mapping.','A review record you can inspect and export. Generated executable adapters are a later step.',decisions.size?'<button id="export" class="btn primary">Export decisions ↓</button>':'')+(decisions.size?`<div class="panel" style="overflow:auto"><table><thead><tr><th>SOURCE</th><th>TARGET</th><th>DECISION</th><th>REASON</th></tr></thead><tbody>${[...decisions].map(([i,d])=>`<tr><td><code>${esc(data.candidates[i].external_path)}</code></td><td>${esc(d.canonical_path||'—')}</td><td>${esc(d.state)}</td><td>${esc(d.rationale)}</td></tr>`).join('')}</tbody></table></div>`:empty());
  if(decisions.size)$('#export').onclick=()=>{const blob=new Blob([JSON.stringify({project:name,endpoint:data.endpoint.path,decisions:[...decisions].map(([i,d])=>({source:data.candidates[i].external_path,...d}))},null,2)],{type:'application/json'});const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='crosswalk-decisions.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
}
window.addEventListener('hashchange',()=>{notice();render();});render();
