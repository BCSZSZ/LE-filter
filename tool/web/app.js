const $ = id => document.getElementById(id);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const copy = value => JSON.parse(JSON.stringify(value));
const STORAGE = 'le-filter-workbench-v1';
const endgameCategories = [
  ['uniques','所需暗金','选择暗金'],
  ['equipment','装备词条','添加部位'],
  ['altars','祭坛词条','添加祭坛'],
  ['idols','神像词条','添加神像'],
  ['bases','所需底材','添加底材']
];
const levelingCategories = [['affixes','所需词条','选择词条'],['bases','所需底材','添加底材']];
const categories = () => mode==='leveling'?levelingCategories:endgameCategories;
let catalog, examples, config, activeId, mode='endgame', category='uniques', view='editor', selection, imported, generated, toastTimer;
let selectionApplied=false;
const workbenchReady = () => selectionApplied && config.builds.some(b=>b.enabled);
const emptyProfile = () => ({uniques:[],equipment:[],altars:[],idols:[],bases:[]});
const emptyLeveling = () => ({affixes:[],bases:[]});
const build = () => config.builds.find(b => b.id === activeId);
const profile = () => build().profiles[mode];
const typeName = t => catalog.types[t]?.zh || t;
const label = (kind,id) => catalog[kind][String(id)]?.zh || `未知ID ${id}`;
const chips = (ids,kind,typ) => ids.map(id => `<span class="chip ${kind==='bases'?'base-chip':''}">${esc(label(kind,kind==='bases'?`${typ}:${id}`:id))}<small>${esc(id)}</small></span>`).join('');

function toast(message,error=false){
  clearTimeout(toastTimer);$('toast').textContent=message;$('toast').hidden=false;$('toast').className=error?'error-toast':'';
  toastTimer=setTimeout(()=>$('toast').hidden=true,error?10000:3500);
}
async function api(path,payload){
  if(globalThis.LEFilterAPI)return globalThis.LEFilterAPI(path,payload);
  const response=await fetch(path,payload?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}:{});
  const data=await response.json();if(!response.ok)throw Error(data.error || '请求失败');return data;
}
function save(){
  generated=null;
  try{localStorage.setItem(STORAGE,JSON.stringify(config));$('save-state').textContent='已保存在此浏览器';}
  catch{$('save-state').textContent='请用“保存配置”备份';}
}
function selectionChanged(){selectionApplied=false;view='editor';save();render();}
async function download(text,name){
  if(globalThis.LEFilterAPI){
    const url=URL.createObjectURL(new Blob([text],{type:name.endsWith('.xml')?'application/xml':'application/json'}));
    const a=document.createElement('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();
    setTimeout(()=>URL.revokeObjectURL(url),30000);return;
  }
  const result=await api('/api/download',{text,name});
  const a=document.createElement('a');a.href=result.url;a.download=name;document.body.append(a);a.click();a.remove();
}
function render(){
  const selected=config.builds.filter(b=>b.enabled),ready=workbenchReady();
  if(!selected.some(b=>b.id===activeId))activeId=selected.find(b=>b.id===config.main_id)?.id||selected[0]?.id;
  $('builds').innerHTML=config.builds.map(b=>`<div class="build-card ${ready&&b.id===activeId?'editing':''}"><input type="checkbox" data-enable="${esc(b.id)}" ${b.enabled?'checked':''} aria-label="收集${esc(b.name)}"><div><button class="build-name" data-edit="${esc(b.id)}">${esc(b.name)}</button><div class="build-meta"><label><input type="radio" name="main-build" data-main="${esc(b.id)}" ${b.id===config.main_id?'checked':''}>主套路</label><button class="remove-build" data-remove="${esc(b.id)}" aria-label="移除${esc(b.name)}">×</button></div></div></div>`).join('');
  $('apply-builds').textContent=`应用所选BD（${selected.length}）`;
  $('build-title').textContent=ready?build().name:'BD编辑工作台';
  $('workspace-builds').hidden=!ready;$('workspace-controls').hidden=!ready;$('workspace-empty').hidden=ready;
  $('workspace-builds').innerHTML=ready?selected.map(b=>`<button data-workspace-build="${esc(b.id)}" class="${b.id===activeId?'active':''}"><span class="dot ${b.id===config.main_id?'pink':'blue'}"></span>${esc(b.name)} · ${b.id===config.main_id?'主':'副'}套路</button>`).join(''):'';
  $('workspace-message').textContent=selected.length?'选择待应用':'尚未选择BD';
  $('rename-build').hidden=!ready;
  ['preview-button','export-xml','save-requirements','extra-t7'].forEach(id=>$(id).disabled=!ready);
  document.querySelectorAll('[data-mode]').forEach(b=>b.classList.toggle('active',b.dataset.mode===mode));
  document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===view));
  $('editor').hidden=!ready||view!=='editor';$('preview').hidden=!ready||view!=='preview';
  $('extra-t7').checked=config.extra_t7;
  if(!ready){['targets','categories','source-info','preview-rules'].forEach(id=>$(id).replaceChildren());$('preview-summary').textContent='';return;}
  $('profile-note').textContent=mode==='endgame'?'终局目标':'0–29级：至少1项目标；30–49级：目标总阶数≥5；50–79级：≥8，单可用目标T≥5；80级退出。';
  if(!categories().some(c=>c[0]===category))category=categories()[0][0];
  $('categories').innerHTML=categories().map(([key,title],i)=>`<button data-category="${key}" class="${category===key?'active':''}"><span class="step-num">0${i+1}</span>${title}</button>`).join('');
  const item=categories().find(c=>c[0]===category);
  $('category-title').textContent=item[1];$('add-target').textContent=item[2];$('add-target').hidden=!item[2];
  $('export-xml').textContent='导出filter';
  renderTargets();renderSource();
}
function renderTargets(){
  const data=profile()[category];
  if(!data.length){$('targets').innerHTML=`<div class="empty"><strong>为这个BD选择${categories().find(c=>c[0]===category)[1]}</strong>从列表搜索选择，或导入filter填入目标。</div>`;return;}
  if(category==='uniques'||category==='affixes'){
    $('targets').innerHTML=`<div class="target-row"><div class="chips">${chips(data,category)}</div></div>`;return;
  }
  $('targets').innerHTML=data.map((g,i)=>{
    if(category==='bases'&&mode==='endgame'){
      return `<div class="target-row"><div class="row-heading"><strong>${esc(typeName(g.type))}</strong><div class="row-actions"><button data-pick="preferred_bases" data-index="${i}">首选底材</button><button data-pick="bases" data-index="${i}">替代底材</button><button data-delete="${i}" aria-label="移除此分组">×</button></div></div><div class="chips"><small>首选</small>${g.preferred_bases?.length?chips(g.preferred_bases,'bases',g.type):'<small>未指定</small>'}</div><div class="chips" style="margin-top:12px"><small>替代</small>${g.bases.length?chips(g.bases,'bases',g.type):'<small>未选择</small>'}</div></div>`;
    }
    const commands=`${category!=='bases'?`<button data-pick="affixes" data-index="${i}">词缀</button>`:''}<button data-pick="bases" data-index="${i}">底材</button>${category==='idols'?`<button data-pick="pair_bases" data-index="${i}">两项层底材</button>`:''}<button data-delete="${i}" aria-label="移除此分组">×</button>`;
    const bases=g.bases.length?chips(g.bases,'bases',g.type):`<small>${category==='bases'?'未选择底材':'底材不限'}</small>`;
    const references=category==='bases'?'':[['enchanted','附魔'],['corrupted','腐化']].filter(([key])=>g[key]?.length).map(([key,title])=>`<div class="chips" style="margin-top:12px"><small>${title}参考</small>${chips(g[key],'affixes')}</div>`).join('');
    return `<div class="target-row"><div class="row-heading"><strong>${esc(typeName(g.type))}</strong><div class="row-actions">${commands}</div></div><div class="chips">${bases}</div>${category!=='bases'?`<div class="chips" style="margin-top:12px">${g.affixes.length?chips(g.affixes,'affixes'):'<small>未选择词缀</small>'}</div>`:''}${references}</div>`;
  }).join('');
}
function renderSource(){
  const source=build().requirement_sources?.[mode]||build().source;
  const legacy=mode==='leveling'&&build().legacy_leveling;
  $('source-details').hidden=!source&&!legacy;
  $('source-info').innerHTML=(source?`<p>${esc(source.name)}${source.scope?` · ${esc(source.scope)}`:''}</p>${(source.warnings||[]).map(w=>`<p class="warning">${esc(w)}</p>`).join('')}`:'')+(legacy?'<p>旧练级配置已转换为两份列表；原始数据随整套配置保存。</p>':'');
}
function openPicker(kind,field,values,types,apply,normalOnly=false,single=false,excluded=[]){
  const eligible=normalOnly?values.filter(id=>[0,5].includes(catalog.affixes[id]?.special)):values;
  selection={kind,field,chosen:new Set(eligible.map(String)),types,apply,normalOnly,single,excluded};
  $('picker-title').textContent=kind==='uniques'?'选择所需暗金':kind==='bases'?'选择底材':'选择目标词缀';
  $('picker-search').value='';$('only-selected').checked=false;$('show-legacy').checked=false;
  renderPicker();$('picker').showModal();setTimeout(()=>$('picker-search').focus(),50);
}
function renderPicker(){
  const query=$('picker-search').value.trim().toLowerCase();
  const s=selection;
  const all=Object.values(catalog[s.kind]).filter(a=>{
    if(s.excluded.includes(a.id))return false;
    const selected=s.chosen.has(String(a.id));
    if(s.kind==='affixes'&&s.normalOnly&&![0,5].includes(a.special))return false;
    if(s.kind==='affixes'&&['equipment','leveling'].includes(s.field)&&[4,6].includes(a.special))return false;
    if(s.kind==='bases'&&(!s.types.includes(a.type)))return false;
    if(s.kind==='affixes'&&s.types.length&&!s.types.some(t=>a.types.includes(t))&&!selected)return false;
    if((a.legacy||a.hidden)&&!$('show-legacy').checked&&!selected)return false;
    if($('only-selected').checked&&!selected)return false;
    return `${a.zh} ${a.en} ${a.id}`.toLowerCase().includes(query);
  });
  $('picker-summary').textContent=`找到${all.length}项 · 中文、英文和ID均可过滤`;
  $('selection-count').textContent=`已选${s.chosen.size}项`;
  $('picker-list').innerHTML=all.map(a=>`<label class="pick-row"><input type="checkbox" data-id="${a.id}" ${s.chosen.has(String(a.id))?'checked':''}><div><strong>${esc(a.zh)}</strong><small>${esc(a.en)}${s.kind==='affixes'?` · ${a.prefix?'前缀':'后缀'}${a.special===4?' · 附魔参考':a.special===6?' · 腐化参考':a.special===1?' · 实验词缀':''}`:s.kind==='uniques'?` · ${esc(typeName(a.type))}${a.set?' · 套装':''}`:` · 需求等级${a.level}`}${a.legacy||a.hidden?' · 旧／隐藏条目':''}</small></div><span class="id-tag">${a.id}</span></label>`).join('')||'<div class="empty">没有匹配项，试试英文或ID。</div>';
}
function pickGroup(field,index){
  const g=profile()[category][index];
  const kind=field==='affixes'?'affixes':'bases';
  const ranked=category==='bases'&&mode==='endgame';
  openPicker(kind,category,field==='pair_bases'?(g.pair_bases??g.bases):(g[field]||[]),[g.type],values=>{
    const sameBases=JSON.stringify(g.pair_bases)===JSON.stringify(g.bases);
    if(ranked&&field==='preferred_bases')g.bases=[...new Set([...g.bases,...(g.preferred_bases||[])])].filter(id=>!values.includes(id));
    g[field]=values;
    if(field==='bases'&&category==='idols'&&sameBases)g.pair_bases=copy(values);
    save();render();
  },category==='idols'&&kind==='affixes',ranked&&field==='preferred_bases',ranked&&field==='bases'?(g.preferred_bases||[]):[]);
  if(ranked)$('picker-title').textContent=field==='preferred_bases'?'选择首选底材（最多一个）':'选择替代底材';
}
function showGroupDialog(){
  const types=category==='altars'?['IDOL_ALTAR']:category==='idols'?Object.keys(catalog.types).filter(t=>t.startsWith('IDOL_')&&t!=='IDOL_ALTAR'):catalog.equipment_types;
  $('group-title').textContent=categories().find(c=>c[0]===category)[2];
  $('group-type').innerHTML=types.map(t=>`<option value="${t}">${esc(typeName(t))} ${esc(t.startsWith('IDOL_')&&t!=='IDOL_ALTAR'?t.slice(5):'')}</option>`).join('');
  $('group-dialog').showModal();
}
async function preview(){
  if(!workbenchReady())return toast('请先勾选BD并点击“应用所选BD”。');
  try{
    $('preview-button').disabled=true;
    const snapshot=JSON.stringify(config),out=await api('/api/generate',{config});
    if(!workbenchReady()||snapshot!==JSON.stringify(config))return;
    generated=out;view='preview';render();renderPreview();
  }catch(e){toast(e.message,true);}finally{$('preview-button').disabled=!workbenchReady();}
}
function renderPreview(){
  if(!generated)return;
  const selected=config.builds.filter(b=>b.enabled).map(b=>b.name).join('＋');
  $('preview-summary').textContent=`${selected} · 终局＋练级 · ${generated.count}条规则 / ${generated.enabled}条启用。${generated.warnings.join(' ')}`;
  const query=$('preview-search').value.toLowerCase();
  const rows=generated.rules.filter(r=>`${r.name} ${r.sound} ${r.gate} ${r.types.map(typeName).join(' ')} ${(r.uniques||[]).map(i=>`${label('uniques',i)} ${i}`).join(' ')}`.toLowerCase().includes(query));
  $('preview-rules').innerHTML=`<table class="preview-table"><thead><tr><th>顺序</th><th>档位</th><th>规则与目标</th><th>条件</th></tr></thead><tbody>${rows.map(r=>`<tr><td>${r.number}${r.enabled?'':'<small>关闭</small>'}</td><td><span class="badge tier-${r.tier}">${esc(r.sound)}</span><small>${esc(r.role)}</small></td><td>${esc(r.name)}<small>${esc(r.types.map(typeName).join('、'))}</small>${r.category.startsWith('终局05')?`<small>底材：${esc(r.bases.map(i=>`${label('bases',`${r.types[0]}:${i}`)}(${i})`).join('、'))}</small>`:''}${r.affixes.flat().length<30?`<small>${esc(r.affixes.flat().map(i=>`${label('affixes',i)}(${i})`).join('、'))}</small>`:''}${r.uniques?.length?`<details><summary>${r.uniques.length}种暗金／套装</summary><small>${esc(r.uniques.map(i=>`${label('uniques',i)}(${i})`).join('、'))}</small></details>`:''}</td><td>${esc(r.gate)}<small>${r.action==='HIDE'?'隐藏':'显示'}</small></td></tr>`).join('')}</tbody></table>`;
}
function showImportResult(){
  const p=imported.profile;
  $('import-result').innerHTML=`<h2 style="margin-bottom:14px">${esc(imported.name)}</h2><div class="import-summary">${endgameCategories.map(([k,title])=>`<span class="stat">${title} <strong>${p[k].length}</strong>${k==='uniques'?'项':'组'}</span>`).join('')}</div>${imported.warnings.map(w=>`<p class="warning">${esc(w)}</p>`).join('')}<details><summary>核对${imported.rules.length}条来源规则与情报分类</summary><div class="source-scroll"><table class="source-table"><thead><tr><th>来源</th><th>原规则</th><th>填入类别</th></tr></thead><tbody>${imported.rules.map(r=>`<tr><td>X${r.x}<br>${r.enabled?'启用':'关闭'}</td><td>${esc(r.name||'(无名称)')}<br><small>${esc(r.types.map(typeName).join('、'))} · ${r.affix_count}个词缀ID</small></td><td><select data-import-rule="${r.x}" aria-label="X${r.x}情报分类"><option value="">不提取</option>${endgameCategories.map(([k,title])=>`<option value="${k}" ${r.category===k?'selected':''}>${title}</option>`).join('')}</select></td></tr>`).join('')}</tbody></table></div></details>`;
  $('apply-import').disabled=false;
}
async function analyzeImport(assignments){
  try{
    imported=await api('/api/import',{xml:$('xml-text').value,assignments});showImportResult();
  }catch(e){$('apply-import').disabled=true;toast(e.message,true);}
}

$('builds').addEventListener('click',e=>{
  const edit=e.target.closest('[data-edit]');if(edit){if(!workbenchReady()||!config.builds.find(b=>b.id===edit.dataset.edit)?.enabled)return toast('请先勾选该BD并点击“应用所选BD”。');activeId=edit.dataset.edit;view='editor';render();return;}
  const remove=e.target.closest('[data-remove]');if(remove){config.builds=config.builds.filter(b=>b.id!==remove.dataset.remove);if(config.main_id===remove.dataset.remove)config.main_id=config.builds.find(b=>b.enabled)?.id;selectionChanged();}
});
$('builds').addEventListener('change',e=>{
  if(e.target.dataset.enable){const b=config.builds.find(b=>b.id===e.target.dataset.enable);b.enabled=e.target.checked;if(!config.builds.find(b=>b.id===config.main_id)?.enabled)config.main_id=config.builds.find(b=>b.enabled)?.id;}
  if(e.target.dataset.main){config.main_id=e.target.dataset.main;config.builds.find(b=>b.id===config.main_id).enabled=true;}
  selectionChanged();
});
$('apply-builds').onclick=()=>{selectionApplied=true;if(!config.builds.find(b=>b.id===config.main_id)?.enabled)config.main_id=config.builds.find(b=>b.enabled)?.id;activeId=config.main_id;view='editor';save();render();};
$('workspace-builds').onclick=e=>{const b=e.target.closest('[data-workspace-build]');if(b){activeId=b.dataset.workspaceBuild;view='editor';render();}};
$('add-build').onclick=()=>{const b={id:crypto.randomUUID(),name:`新BD ${config.builds.length+1}`,enabled:true,profiles:{endgame:emptyProfile(),leveling:emptyLeveling()}};config.builds.push(b);activeId=b.id;selectionChanged();};
$('rename-build').onclick=()=>{
  const input=document.createElement('input');input.type='text';input.value=build().name;input.setAttribute('aria-label','BD名称');$('build-title').replaceChildren(input);input.focus();
  const done=()=>{build().name=input.value.trim()||'未命名BD';save();render();};input.onblur=done;input.onkeydown=e=>{if(e.key==='Enter')input.blur();};
};
document.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>{mode=b.dataset.mode;category=categories()[0][0];view='editor';render();});
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{if(b.dataset.view==='preview')preview();else{view='editor';render();}});
$('categories').onclick=e=>{const b=e.target.closest('[data-category]');if(b){category=b.dataset.category;render();}};
$('add-target').onclick=()=>{
  if(category==='uniques'||category==='affixes')openPicker(category,mode==='leveling'?'leveling':category,profile()[category],category==='affixes'?catalog.equipment_types:[],values=>{profile()[category]=values;save();render();});
  else showGroupDialog();
};
$('create-group').onclick=()=>{const g=category==='bases'?{type:$('group-type').value,bases:[]}:{type:$('group-type').value,bases:[],affixes:[],corrupted:[],enchanted:[],sources:[]};if(category==='idols')g.pair_bases=[];profile()[category].push(g);$('group-dialog').close();save();render();pickGroup(category==='bases'?'bases':'affixes',profile()[category].length-1);};
$('targets').addEventListener('click',e=>{
  const pick=e.target.closest('[data-pick]');if(pick)pickGroup(pick.dataset.pick,Number(pick.dataset.index));
  const del=e.target.closest('[data-delete]');if(del){profile()[category].splice(Number(del.dataset.delete),1);save();render();}
});
['picker-search','only-selected','show-legacy'].forEach(id=>$(id).addEventListener('input',renderPicker));
$('picker-list').onchange=e=>{if(e.target.dataset.id){const id=e.target.dataset.id;if(e.target.checked){if(selection.single)selection.chosen.clear();selection.chosen.add(id);}else selection.chosen.delete(id);if(selection.single)renderPicker();else $('selection-count').textContent=`已选${selection.chosen.size}项`;}};
$('apply-selection').onclick=()=>{selection.apply([...selection.chosen].map(Number).sort((a,b)=>a-b));$('picker').close();};
document.querySelectorAll('[data-close]').forEach(b=>b.onclick=()=>$(b.dataset.close).close());
$('import-filter').onclick=()=>{$('import-mode').value=mode;$('import-dialog').showModal();};
$('xml-file').onchange=async e=>{if(e.target.files[0]){$('xml-text').value=await e.target.files[0].text();await analyzeImport();}};
$('analyze-import').onclick=()=>analyzeImport();
$('apply-import').onclick=async()=>{
  const assignments=Object.fromEntries([...document.querySelectorAll('[data-import-rule]')].map(el=>[el.dataset.importRule,el.value]));
  await analyzeImport(assignments);if($('apply-import').disabled)return;
  const id=crypto.randomUUID(),stage=$('import-mode').value;
  const b={id,name:imported.name,enabled:true,profiles:{endgame:emptyProfile(),leveling:emptyLeveling()},source:{name:$('xml-file').files[0]?.name||'粘贴XML',sha256:imported.source_sha256,warnings:imported.warnings,rules:imported.rules}};
  b.profiles[stage]=copy(stage==='leveling'?imported.leveling_profile:imported.profile);config.builds.push(b);activeId=id;mode=stage;category=categories()[0][0];selectionChanged();$('import-dialog').close();toast('已提取目标，点击“应用所选BD”后核对修改。');
};
$('extra-t7').onchange=e=>{config.extra_t7=e.target.checked;save();};
$('preview-button').onclick=preview;$('preview-search').oninput=renderPreview;
$('export-xml').onclick=async()=>{
  if(!workbenchReady())return toast('请先勾选BD并点击“应用所选BD”。');
  try{const out=await api('/api/generate',{config});await download(out.xml,'LE-filter.xml');toast(`已导出${out.count}条规则，包含终局和练级目标。${out.warnings.join(' ')}`);}catch(e){toast(e.message,true);}
};
$('save-config').onclick=async()=>{try{await download(JSON.stringify(config,null,2),'LE-filter-targets.json');}catch(e){toast(e.message,true);}};
$('save-requirements').onclick=async()=>{
  try{const document=await api('/api/requirements/export',{build:build(),stage:mode});await download(JSON.stringify(document,null,2),'LE-filter-requirements.json');toast(`已保存本BD的${mode==='endgame'?'终局':'练级'}需求。`);}catch(e){toast(e.message,true);}
};
$('import-requirements').onclick=()=>$('requirements-file').click();
$('requirements-file').onchange=async e=>{
  try{
    const file=e.target.files[0];if(!file)return;
    const data=await api('/api/requirements/import',{document:JSON.parse(await file.text())});
    let b=config.builds.find(b=>b.id===data.id);
    if(!b){b={id:data.id,name:data.name,enabled:false,profiles:{endgame:emptyProfile(),leveling:emptyLeveling()}};config.builds.push(b);}
    b.name=data.name;
    b.profiles[data.stage]=data.profile;b.requirement_sources||={};b.requirement_sources[data.stage]=data.source;
    activeId=b.id;mode=data.stage;category=categories()[0][0];selectionChanged();toast('已载入BD需求，勾选该BD并点击“应用所选BD”后编辑。');
  }catch(e){toast(e.message,true);}finally{e.target.value='';}
};
$('load-config').onclick=()=>$('config-file').click();
$('config-file').onchange=async e=>{
  try{const file=e.target.files[0];if(!file)return;const loaded=JSON.parse(await file.text());config=(await api('/api/validate',{config:loaded})).config;activeId=config.main_id;selectionChanged();toast('已载入配置，点击“应用所选BD”载入工作台。');}catch(e){toast(e.message,true);}finally{e.target.value='';}
};
$('load-examples').onclick=()=>{config=copy(examples);activeId=config.main_id;category='uniques';mode='endgame';selectionChanged();toast('已载入示例方案，点击“应用所选BD”载入工作台。');};
async function init(){
  try{
    if(globalThis.LEFilterAPI){document.querySelector('.layout').inert=true;document.querySelector('.top-actions').inert=true;$('save-state').textContent='首次加载，请稍候…';}
    const boot=await api('/api/bootstrap');catalog=boot.catalog;examples=boot.config;
    try{config=JSON.parse(localStorage.getItem(STORAGE));}catch{}
    if(!config||config.version!==1||!Array.isArray(config.builds))config=copy(examples);
    config=(await api('/api/validate',{config})).config;save();
    activeId=config.main_id;$('catalog-version').textContent=catalog.version;render();
    document.querySelector('.layout').inert=false;document.querySelector('.top-actions').inert=false;
  }catch(e){toast(`无法启动：${e.message}`,true);}
}
init();
