'use strict';
const $ = selector => document.querySelector(selector);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const pretty = value => JSON.stringify(value, null, 2);
function parseJSON(text) {
  return JSON.parse(text, (_key,value)=>{
    if(typeof value==='number'&&(!Number.isFinite(value)||Math.abs(value)>Number.MAX_SAFE_INTEGER))throw new Error('Numbers are out of range. Encode large IDs as strings.');
    return value;
  });
}
const operations = {copy:'Copy unchanged',text:'Convert to text',number:'Convert to number',integer:'Whole number (no rounding)',cents_to_dollars:'Cents → dollars',date_iso:'Date: YYYY-MM-DD',date_us:'Date: MM/DD/YYYY → ISO',date_day_first:'Date: DD/MM/YYYY → ISO',omit:'Omit this target field'};
let state = null, result = null, revision = 0, busy = false, pendingMapping = null;
const exampleRecords = [
  {claim_ref:'CL-1042',policy:{number:'POL-8801'},incident_date:'10/04/2026',paid_cents:125050,status:'open'},
  {claim_ref:'CL-1043',policy:{number:'POL-8802'},incident_date:'10/06/2026',paid_cents:9875,status:'closed'},
  {claim_ref:'CL-1044',policy:{number:'POL-8803'},incident_date:'10/09/2026',paid_cents:0,status:'pending'}
];
const exampleTarget = {claim_id:'CL-1042',policy_number:'POL-8801',loss_date:'2026-10-04',paid_amount:1250.5,status:'open'};
function notice(message='') { $('#notice').textContent = message; }
async function api(path, body) {
  const response = await fetch('/workbench/conversion/'+path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const data = await response.json();
  if (!response.ok) throw new Error(typeof data.detail==='string' ? data.detail : data.detail?.map(e=>e.msg).join('; ') || 'The request failed. Check your inputs.');
  return data;
}
function parseInputs() {
  if (new TextEncoder().encode($('#sourceInput').value+$('#targetInput').value).length>800000) throw new Error('Use at most 800 KB of sample data.');
  let records, target;
  try { records=parseJSON($('#sourceInput').value); } catch(error) { throw new Error('Source JSON: '+error.message); }
  try { target=parseJSON($('#targetInput').value); } catch(error) { throw new Error('Target JSON: '+error.message); }
  if (!Array.isArray(records)||!records.length||records.length>200||records.some(r=>!r||Array.isArray(r)||typeof r!=='object')) throw new Error('Source must contain 1–200 JSON objects in an array.');
  if (!target||Array.isArray(target)||typeof target!=='object'||!Object.keys(target).length) throw new Error('Target must be one non-empty JSON object.');
  return {records,target};
}
function showStep(mapping) {
  $('#setup').hidden=mapping;$('#workbench').hidden=!mapping;
  $('#inputStep').classList.toggle('active',!mapping);$('#mappingStep').classList.toggle('active',mapping);
  $('#inputStep').setAttribute('aria-current',mapping?'false':'step');$('#mappingStep').setAttribute('aria-current',mapping?'step':'false');
}
function invalidate() {
  revision++;result=null;$('#downloadOutput').disabled=true;$('#downloadCode').disabled=true;
  $('#resultTitle').textContent='See what comes out';$('#resultSummary').textContent='Run your mapping to compare the source with the converted result.';$('#codeHelp').hidden=true;
}
async function build(example=false) {
  if(busy)return;busy=true;$('#build').disabled=true;$('#example').disabled=true;notice('Reading the sample fields…');
  try {
    const inputs=parseInputs(), version=revision, suggestions=await api('suggest',inputs);
    if(version!==revision){notice('Inputs changed. Set up the mapping again.');return;}
    const next={...inputs,...suggestions};
    if(example) {
      const choices=[['/claim_ref','copy'],['/policy/number','copy'],['/incident_date','date_us'],['/paid_cents','cents_to_dollars'],['/status','copy']];
      next.rules.forEach((rule,i)=>{[rule.source,rule.operation]=choices[i];rule.reason='Example mapping · check before running';});
    }
    if(pendingMapping) {
      const saved=pendingMapping;
      if(!Array.isArray(saved.rules)||saved.rules.length!==next.rules.length)throw new Error('Saved mapping does not match this target.');
      const targets=new Set(next.rules.map(r=>r.target));
      if(new Set(saved.rules.map(r=>r.target)).size!==targets.size)throw new Error('Saved mapping has duplicate targets.');
      next.rules=saved.rules.map(r=>{
        if(!targets.has(r.target)||!Object.hasOwn(operations,r.operation)||typeof r.required!=='boolean'||(r.operation!=='omit'&&!next.sources.includes(r.source)))throw new Error('Saved mapping contains fields missing from these samples.');
        return {target:r.target,source:r.source,operation:r.operation,required:r.required,reviewed:false,reason:'Loaded mapping · review against these records'};
      });
      pendingMapping=null;
    }
    state=next;invalidate();renderRules();$('#mappingStep').disabled=false;showStep(true);renderRecords();
    notice(example?'Example loaded. Review the five mappings, then run the conversion.':'Check each mapping, then run the conversion.');
  } catch(error){state=null;$('#mappingStep').disabled=true;showStep(false);notice(error.message);}
  finally{busy=false;$('#build').disabled=false;$('#example').disabled=false;if(state)updateReviewCount();}
}
function renderRules() {
  $('#mappingCount').textContent=state.rules.length;
  $('#rules').innerHTML=state.rules.map((r,i)=>`<tr class="${r.reviewed?'reviewed':''}"><td><code>${esc(r.target)}</code><small>${esc(r.reason||'')}</small></td><td><select data-index="${i}" data-field="source" aria-label="Source for ${esc(r.target)}" ${r.operation==='omit'?'disabled':''}><option value="">Choose a source field</option>${state.sources.map(s=>`<option value="${esc(s)}" ${s===r.source?'selected':''}>${esc(s)}</option>`).join('')}</select></td><td><select data-index="${i}" data-field="operation" aria-label="Conversion for ${esc(r.target)}">${Object.entries(operations).map(([value,label])=>`<option value="${value}" ${r.operation===value?'selected':''}>${label}</option>`).join('')}</select></td><td><input type="checkbox" data-index="${i}" data-field="required" aria-label="Required ${esc(r.target)}" ${r.required?'checked':''} ${r.operation==='omit'?'disabled':''}></td><td><input type="checkbox" data-index="${i}" data-field="reviewed" aria-label="Reviewed ${esc(r.target)}" ${r.reviewed?'checked':''}></td></tr>`).join('');
  updateReviewCount();
}
function updateReviewCount() {
  const reviewed=state.rules.filter(r=>r.reviewed).length;
  $('#reviewCount').textContent=`${reviewed} of ${state.rules.length} reviewed · required fields fail when missing or null`;
  $('#run').disabled=busy||reviewed!==state.rules.length;
}
$('#rules').addEventListener('change',event=>{
  const element=event.target, rule=state.rules[Number(element.dataset.index)], field=element.dataset.field;
  if(!rule||!field)return;
  rule[field]=element.type==='checkbox'?element.checked:element.value;
  if(field!=='reviewed')rule.reviewed=false;
  invalidate();renderRules();renderRecord();notice();
  $(`[data-index="${element.dataset.index}"][data-field="${field}"]`).focus();
});
function renderRecords() {
  $('#recordSelect').innerHTML=state.records.map((_,i)=>`<option value="${i}">${i+1} of ${state.records.length}${result?.rows[i].errors.length?' · errors':''}</option>`).join('');renderRecord();
}
function renderRecord() {
  const index=Number($('#recordSelect').value)||0, row=result?.rows[index];
  $('#sourcePreview').textContent=pretty(state.records[index]);$('#outputPreview').textContent=row?pretty(row.output):'Your converted data will appear here.';
  $('#previewLabel').textContent=row?(row.errors.length?'Partial result · not exportable':'Validated'):'Not run yet';
  $('#recordStatus').textContent=row?(row.errors.length?`${row.errors.length} field errors`:'Passed'):'Awaiting conversion';
  $('#errors').innerHTML=row?.errors.map(e=>`<p><strong>${esc(e.target)}</strong> — ${esc(e.message)}</p>`).join('')||'';
}
function payload() { return {records:state.records,target:state.target,rules:state.rules.map(({reason,...rule})=>rule)}; }
$('#run').onclick=async()=>{
  if(busy)return;busy=true;const current=revision;updateReviewCount();notice('Converting sample records…');
  try {
    const response=await api('preview',payload());if(current!==revision)return;
    result=response;$('#resultTitle').textContent=`${result.valid} of ${state.records.length} records passed`;
    $('#resultSummary').textContent=result.invalid?'Fix the errors below before downloading. Failed records are excluded from output.':'Every sample passed the chosen type, required-field, and conversion checks.';
    $('#downloadOutput').disabled=!!result.invalid;$('#downloadCode').disabled=!!result.invalid;
    renderRecords();if(result.invalid){$('#recordSelect').value=String(result.rows.findIndex(r=>r.errors.length));renderRecord();}
    notice(result.invalid?'Some records need attention. Select a record to inspect its errors.':'Conversion complete. Inspect the results or download your files.');
  }catch(error){notice(error.message);}finally{busy=false;if(state)updateReviewCount();}
};
function download(filename,content,type='application/json') {
  const url=URL.createObjectURL(new Blob([content],{type})),link=document.createElement('a');link.href=url;link.download=filename;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
$('#downloadOutput').onclick=()=>{if(result&&!result.invalid)download('converted.json',pretty(result.output));};
$('#downloadCode').onclick=async()=>{
  if(!result||result.invalid)return;const current=revision;$('#downloadCode').disabled=true;
  try{const response=await api('export',payload());if(current!==revision)return;download('adapter.py',response.code,'text/x-python');$('#codeHelp').hidden=false;notice('Adapter downloaded. Run it with the command below.');}
  catch(error){notice(error.message);}finally{$('#downloadCode').disabled=!result||!!result.invalid;}
};
$('#save').onclick=()=>{download('crosswalk-mapping.json',pretty({version:1,target:state.target,rules:payload().rules}));notice('Mapping saved with your target example. Source records are not included.');};
$('#open').onclick=()=>$('#projectFile').click();
$('#projectFile').onchange=async event=>{
  try{
    const file=event.target.files[0];if(!file)return;if(file.size>800000)throw new Error('Mapping file must be under 800 KB.');
    const saved=parseJSON(await file.text());if(saved?.version!==1||!saved.target||!Array.isArray(saved.rules))throw new Error('Choose a Crosswalk mapping file.');
    $('#targetInput').value=pretty(saved.target);inputsChanged();pendingMapping=saved;showStep(false);
    notice('Mapping loaded. Add source records and select Set up field mapping to restore its rules.');
  }catch(error){notice(error.message);}finally{event.target.value='';}
};
for(const kind of ['source','target']) {
  const suffix=kind==='source'?'Source':'Target';
  $('#load'+suffix).onclick=()=>$('#'+kind+'File').click();
  $('#'+kind+'File').onchange=async event=>{
    try{const file=event.target.files[0];if(!file)return;if(file.size>800000)throw new Error('Choose a file smaller than 800 KB.');$('#'+kind+'Input').value=await file.text();inputsChanged();if(kind==='target')pendingMapping=null;notice(`${file.name} loaded.`);}catch(error){notice(error.message);}finally{event.target.value='';}
  };
  $('#'+kind+'Input').oninput=()=>{inputsChanged();if(kind==='target')pendingMapping=null;};
  $('#format'+suffix).onclick=()=>{try{$('#'+kind+'Input').value=pretty(parseJSON($('#'+kind+'Input').value));notice();}catch(error){notice(`${kind} JSON: ${error.message}`);}};
}
function inputsChanged(){invalidate();state=null;$('#mappingStep').disabled=true;}
$('#build').onclick=()=>build();$('#example').onclick=()=>{if(busy)return;pendingMapping=null;$('#sourceInput').value=pretty(exampleRecords);$('#targetInput').value=pretty(exampleTarget);inputsChanged();build(true);};
$('#inputStep').onclick=()=>{showStep(false);notice();};$('#mappingStep').onclick=()=>{if(state)showStep(true);};$('#recordSelect').onchange=renderRecord;
