const $ = id => document.getElementById(id);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const copy = value => JSON.parse(JSON.stringify(value));
const STORAGE = 'le-filter-workbench-v1';
const categories = [
  ['uniques','所需暗金','用名字选择目标；0LP保留，高潜能仍按四档提示。','选择暗金'],
  ['equipment','装备词条','每个部位独立填写。至少两个目标时，一条整池条件识别双目标T7。','添加部位'],
  ['altars','祭坛词条','按祭坛底材绑定目标；至少一项，阶数不限。','添加祭坛'],
  ['idols','神像词条','只计普通目标：一项开始、两项灵感。附魔／腐化另外记录。','添加神像'],
  ['bases','所需底材','独立收集制作底材，不给装备T7素材强加同底材要求。','添加底材'],
  ['leveling_slots','练级分段','保留Raxx的等级、阶数与数量门槛；目标独立填写，空白表示沿用原示例。','']
];
const levelNames = {63:'武器／副手T6过渡',64:'防具／首饰T6过渡',75:'早期腐化装备',128:'过渡神像：两项目标',129:'过渡神像：一项目标',135:'开荒神像',136:'开荒武器底材',137:'开荒副手底材',138:'开荒头盔底材',139:'开荒胸甲底材',140:'开荒腰带底材',141:'开荒鞋子底材',142:'开荒项链底材',143:'开荒戒指底材',144:'开荒手套底材',145:'开荒遗物底材',146:'T3生命／物抗拆解',147:'T3移速／冷却拆解',148:'T3抗性拆解',149:'T2生命／物抗',150:'T2移速／冷却',151:'T2抗性',152:'早期弓箭词条',153:'早期近战武器词条',154:'早期施法武器词条',156:'早期遗物底材',157:'早期法器底材',158:'早期箭袋底材',159:'早期盾牌底材',160:'早期戒指底材',161:'早期项链底材'};
let catalog, examples, config, activeId, mode='endgame', category='uniques', view='editor', selection, imported, generated, levelId=136, toastTimer;
const emptyProfile = () => ({uniques:[],equipment:[],altars:[],idols:[],bases:[],leveling_slots:{}});
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
  const response=await fetch(path,payload?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}:{});
  const data=await response.json();if(!response.ok)throw Error(data.error || '请求失败');return data;
}
function save(){
  generated=null;
  try{localStorage.setItem(STORAGE,JSON.stringify(config));$('save-state').textContent='已保存在此浏览器';}
  catch{$('save-state').textContent='请用“保存配置”备份';}
}
async function download(text,name){
  const result=await api('/api/download',{text,name});
  const a=document.createElement('a');a.href=result.url;a.download=name;document.body.append(a);a.click();a.remove();
}
function render(){
  if(!config.builds.length){config.builds.push({id:crypto.randomUUID(),name:'新BD',enabled:true,profiles:{endgame:emptyProfile(),leveling:emptyProfile()}});config.main_id=config.builds[0].id;}
  if(!build())activeId=config.builds[0].id;
  $('builds').innerHTML=config.builds.map(b=>`<div class="build-card ${b.id===activeId?'editing':''}"><input type="checkbox" data-enable="${esc(b.id)}" ${b.enabled?'checked':''} aria-label="收集${esc(b.name)}"><div><button class="build-name" data-edit="${esc(b.id)}">${esc(b.name)}</button><div class="build-meta"><label><input type="radio" name="main-build" data-main="${esc(b.id)}" ${b.id===config.main_id?'checked':''}>主套路</label><button class="remove-build" data-remove="${esc(b.id)}" aria-label="移除${esc(b.name)}">×</button></div></div></div>`).join('');
  $('build-title').textContent=build().name;
  document.querySelectorAll('[data-mode]').forEach(b=>b.classList.toggle('active',b.dataset.mode===mode));
  document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===view));
  $('editor').hidden=view!=='editor';$('preview').hidden=view!=='preview';
  $('profile-note').textContent=mode==='endgame'?'终局目标独立于练级目标。当前已勾选 '+config.builds.filter(b=>b.enabled).length+' 个BD，导出时合并收集。':'练级目标独立填写；Raxx原有等级分段保持。第6项可逐段替换原示例，尚未填写的部分沿用Raxx。';
  $('categories').innerHTML=categories.map(([key,title],i)=>`<button data-category="${key}" class="${category===key?'active':''}"><span class="step-num">0${i+1}</span>${title}</button>`).join('');
  const item=categories.find(c=>c[0]===category);
  $('category-title').textContent=item[1];$('category-description').textContent=item[2];$('add-target').textContent=item[3];$('add-target').hidden=!item[3];
  $('extra-t7').checked=config.extra_t7;$('export-xml').textContent=`导出${mode==='endgame'?'终局':'练级'}filter`;
  renderTargets();renderSource();
}
function renderTargets(){
  if(category==='leveling_slots'){renderLeveling();return;}
  const data=profile()[category];
  if(!data.length){$('targets').innerHTML=`<div class="empty"><strong>为这个BD选择${categories.find(c=>c[0]===category)[1]}</strong>从列表搜索选择，或导入filter填入目标。</div>`;return;}
  if(category==='uniques'){
    $('targets').innerHTML=`<div class="target-row"><div class="chips">${chips(data,'uniques')}</div><p class="reference">已选${data.length}项。可用中文、英文或ID搜索并增删。</p></div>`;return;
  }
  $('targets').innerHTML=data.map((g,i)=>{
    const commands=`${category!=='bases'?`<button data-pick="affixes" data-index="${i}">词缀</button>`:''}<button data-pick="bases" data-index="${i}">底材</button>${category==='idols'?`<button data-pick="pair_bases" data-index="${i}">两项层底材</button>`:''}<button data-delete="${i}" aria-label="移除此分组">×</button>`;
    const bases=g.bases.length?chips(g.bases,'bases',g.type):'<small>底材不限</small>';
    let note=category==='equipment'?`${g.affixes.length}个目标；单目标T7${g.affixes.length>=2?'＋整池至少两目标T7':''}。`:category==='idols'?'一项开始；两项灵感；普通目标阶数不限。':'';
    const pairBases=g.pair_bases??g.bases;
    if(category==='idols')note+=' 两项底材：'+(pairBases.length?pairBases.map(id=>label('bases',`${g.type}:${id}`)).join('、'):'不限');
    const extra=[...(g.enchanted||[]),...(g.corrupted||[])];
    return `<div class="target-row"><div class="row-heading"><strong>${esc(typeName(g.type))}</strong><div class="row-actions">${commands}</div></div><div class="chips">${bases}</div>${category!=='bases'?`<div class="chips" style="margin-top:12px">${g.affixes.length?chips(g.affixes,'affixes'):'<small>尚未填写词缀；此组不会生成目标规则</small>'}</div>`:''}<p class="reference">${esc(note)}</p>${extra.length?`<p class="reference">附魔／腐化参考，不计入普通目标：${esc(extra.map(id=>`${label('affixes',id)} (${id})`).join('、'))}</p>`:''}</div>`;
  }).join('');
}
function renderSource(){
  const source=build().requirement_sources?.[mode]||build().source;
  $('source-details').hidden=!source;
  if(source)$('source-info').innerHTML=`<p>${esc(source.name)}${source.scope?` · ${esc(source.scope)}`:''}</p>${(source.warnings||[]).map(w=>`<p class="warning">${esc(w)}</p>`).join('')}<p>来源提供收集目标；潜能、阶数、声音和规则顺序由我们的基底处理。</p>`;
}
function levelOverride(){
  const p=build().profiles.leveling;
  if(!p.leveling_slots[levelId]){
    const slot=catalog.leveling_slots.find(r=>r.id===Number(levelId));
    p.leveling_slots[levelId]={enabled:slot.enabled,types:copy(slot.types),bases:copy(slot.subtypes),affixes:[...new Set(slot.affix_pools.flat())]};
  }
  return p.leveling_slots[levelId];
}
function renderLeveling(){
  const slot=catalog.leveling_slots.find(r=>r.id===Number(levelId));
  const weaponTypes=catalog.equipment_types.filter(t=>t.startsWith('ONE_HANDED_')||t.startsWith('TWO_HANDED_')||['BOW','WAND'].includes(t));
  const entryTypes=Number(levelId)===136?weaponTypes:['CATALYST','SHIELD','QUIVER'];
  const override=build().profiles.leveling.leveling_slots[levelId];
  const data=override||{enabled:slot.enabled,types:slot.types,bases:slot.subtypes,affixes:[...new Set(slot.affix_pools.flat())]};
  $('targets').innerHTML=`<div class="target-row level-row"><div class="row-heading"><select id="level-slot" aria-label="选择练级分段">${catalog.leveling_slots.map(r=>`<option value="${r.id}" ${r.id===Number(levelId)?'selected':''}>R${r.id} · ${esc(levelNames[r.id]||r.name)}</option>`).join('')}</select><span class="level-default">${override?'已独立填写':'沿用Raxx原示例'}</span></div><p class="reference">固定门槛：${esc(slot.gate)}</p><p class="reference">原类型：${esc(slot.types.map(typeName).join('、')||'不限')}</p><div class="row-actions" style="margin:18px 0"><label><input id="level-enabled" type="checkbox" ${data.enabled?'checked':''}>启用这一段</label>${slot.affix_pools.length?'<button id="level-affixes">独立填写词缀</button>':''}${slot.types.length||[136,137].includes(Number(levelId))?'<button id="level-bases">独立填写底材</button>':''}<button id="reset-level">恢复原示例</button></div>${[136,137].includes(Number(levelId))?`<label class="field-label" style="margin:12px 0">武器／副手类型<select id="level-type"><option value="">请选择具体类型</option>${entryTypes.map(t=>`<option value="${t}" ${data.types[0]===t?'selected':''}>${esc(typeName(t))}</option>`).join('')}</select></label>`:''}<div class="chips">${chips(data.affixes.slice(0,16),'affixes')}</div>${data.affixes.length>16?`<p class="reference">共${data.affixes.length}项目标，完整列表可在选择器中搜索。</p>`:''}<div class="chips" style="margin-top:12px">${data.types.length===1?chips(data.bases,'bases',data.types[0]):'<small>原规则多类型底材配置保持；需修改时先在JSON中指定单类型，或选武器／副手独立入口。</small>'}</div><p class="reference">练级接口不从终局目标自动复制。词缀数量与阶数、退出等级来自Raxx原规则。</p></div>`;
}
function openPicker(kind,field,values,types,apply,normalOnly=false){
  const eligible=normalOnly?values.filter(id=>[0,5].includes(catalog.affixes[id]?.special)):values;
  selection={kind,field,chosen:new Set(eligible.map(String)),types,apply,normalOnly};
  $('picker-title').textContent=kind==='uniques'?'选择所需暗金':kind==='bases'?'选择底材':'选择目标词缀';
  $('picker-search').value='';$('only-selected').checked=false;$('show-legacy').checked=false;
  renderPicker();$('picker').showModal();setTimeout(()=>$('picker-search').focus(),50);
}
function renderPicker(){
  const query=$('picker-search').value.trim().toLowerCase();
  const s=selection;
  const all=Object.values(catalog[s.kind]).filter(a=>{
    const selected=s.chosen.has(String(a.id));
    if(s.kind==='affixes'&&s.normalOnly&&![0,5].includes(a.special))return false;
    if(s.kind==='affixes'&&s.field==='equipment'&&[4,6].includes(a.special))return false;
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
  openPicker(kind,category,field==='pair_bases'?(g.pair_bases??g.bases):(g[field]||[]),[g.type],values=>{
    const sameBases=JSON.stringify(g.pair_bases)===JSON.stringify(g.bases);
    g[field]=values;
    if(field==='bases'&&category==='idols'&&sameBases)g.pair_bases=copy(values);
    save();render();
  },category==='idols'&&kind==='affixes');
}
function showGroupDialog(){
  const types=category==='altars'?['IDOL_ALTAR']:category==='idols'?Object.keys(catalog.types).filter(t=>t.startsWith('IDOL_')&&t!=='IDOL_ALTAR'):catalog.equipment_types;
  $('group-title').textContent=categories.find(c=>c[0]===category)[3];
  $('group-type').innerHTML=types.map(t=>`<option value="${t}">${esc(typeName(t))} ${esc(t.startsWith('IDOL_')&&t!=='IDOL_ALTAR'?t.slice(5):'')}</option>`).join('');
  $('group-dialog').showModal();
}
async function preview(){
  try{
    $('preview-button').disabled=true;
    generated=await api('/api/generate',{config,mode});view='preview';render();renderPreview();
  }catch(e){toast(e.message,true);}finally{$('preview-button').disabled=false;}
}
function renderPreview(){
  if(!generated)return;
  const selected=config.builds.filter(b=>b.enabled).map(b=>b.name).join('＋');
  $('preview-summary').textContent=`${selected} · ${mode==='endgame'?'终局':'练级'} · ${generated.count}条规则 / ${generated.enabled}条启用。T7只计恰好7阶；静音无地图图标和光柱。`;
  const query=$('preview-search').value.toLowerCase();
  const rows=generated.rules.filter(r=>`${r.name} ${r.sound} ${r.gate} ${r.types.map(typeName).join(' ')}`.toLowerCase().includes(query));
  $('preview-rules').innerHTML=`<table class="preview-table"><thead><tr><th>顺序</th><th>档位</th><th>规则与目标</th><th>条件</th></tr></thead><tbody>${rows.map(r=>`<tr><td>${r.number}${r.enabled?'':'<small>关闭</small>'}</td><td><span class="badge tier-${r.tier}">${esc(r.sound)}</span><small>${esc(r.role)}</small></td><td>${esc(r.name)}<small>${esc(r.types.map(typeName).join('、'))}</small>${r.affixes.flat().length<30?`<small>${esc(r.affixes.flat().map(i=>`${label('affixes',i)}(${i})`).join('、'))}</small>`:''}</td><td>${esc(r.gate)}<small>${r.action==='HIDE'?'隐藏':'显示'}</small></td></tr>`).join('')}</tbody></table>`;
}
function showImportResult(){
  const p=imported.profile;
  $('import-result').innerHTML=`<h2 style="margin-bottom:14px">${esc(imported.name)}</h2><div class="import-summary">${categories.slice(0,5).map(([k,title])=>`<span class="stat">${title} <strong>${p[k].length}</strong>${k==='uniques'?'项':'组'}</span>`).join('')}</div>${imported.warnings.map(w=>`<p class="warning">${esc(w)}</p>`).join('')}<details><summary>核对${imported.rules.length}条来源规则与情报分类</summary><div class="source-scroll"><table class="source-table"><thead><tr><th>来源</th><th>原规则</th><th>填入类别</th></tr></thead><tbody>${imported.rules.map(r=>`<tr><td>X${r.x}<br>${r.enabled?'启用':'关闭'}</td><td>${esc(r.name||'(无名称)')}<br><small>${esc(r.types.map(typeName).join('、'))} · ${r.affix_count}个词缀ID</small></td><td><select data-import-rule="${r.x}" aria-label="X${r.x}情报分类"><option value="">不提取</option>${categories.slice(0,5).map(([k,title])=>`<option value="${k}" ${r.category===k?'selected':''}>${title}</option>`).join('')}</select></td></tr>`).join('')}</tbody></table></div></details>`;
  $('apply-import').disabled=false;
}
async function analyzeImport(assignments){
  try{
    imported=await api('/api/import',{xml:$('xml-text').value,assignments});showImportResult();
  }catch(e){$('apply-import').disabled=true;toast(e.message,true);}
}

$('builds').addEventListener('click',e=>{
  const edit=e.target.closest('[data-edit]');if(edit){activeId=edit.dataset.edit;view='editor';render();return;}
  const remove=e.target.closest('[data-remove]');if(remove){config.builds=config.builds.filter(b=>b.id!==remove.dataset.remove);if(config.main_id===remove.dataset.remove)config.main_id=config.builds.find(b=>b.enabled)?.id;save();render();}
});
$('builds').addEventListener('change',e=>{
  if(e.target.dataset.enable){const b=config.builds.find(b=>b.id===e.target.dataset.enable);b.enabled=e.target.checked;if(!config.builds.find(b=>b.id===config.main_id)?.enabled)config.main_id=config.builds.find(b=>b.enabled)?.id;}
  if(e.target.dataset.main){config.main_id=e.target.dataset.main;config.builds.find(b=>b.id===config.main_id).enabled=true;}
  save();render();
});
$('add-build').onclick=()=>{const b={id:crypto.randomUUID(),name:`新BD ${config.builds.length+1}`,enabled:true,profiles:{endgame:emptyProfile(),leveling:emptyProfile()}};config.builds.push(b);activeId=b.id;view='editor';save();render();};
$('rename-build').onclick=()=>{
  const input=document.createElement('input');input.type='text';input.value=build().name;input.setAttribute('aria-label','BD名称');$('build-title').replaceChildren(input);input.focus();
  const done=()=>{build().name=input.value.trim()||'未命名BD';save();render();};input.onblur=done;input.onkeydown=e=>{if(e.key==='Enter')input.blur();};
};
document.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>{mode=b.dataset.mode;if(mode==='endgame'&&category==='leveling_slots')category='uniques';view='editor';render();});
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{if(b.dataset.view==='preview')preview();else{view='editor';render();}});
$('categories').onclick=e=>{const b=e.target.closest('[data-category]');if(b){category=b.dataset.category;if(category==='leveling_slots')mode='leveling';render();}};
$('add-target').onclick=()=>{if(category==='uniques')openPicker('uniques','uniques',profile().uniques,[],values=>{profile().uniques=values;save();render();});else showGroupDialog();};
$('create-group').onclick=()=>{const g={type:$('group-type').value,bases:[],affixes:[],corrupted:[],enchanted:[],sources:[]};if(category==='idols')g.pair_bases=[];profile()[category].push(g);$('group-dialog').close();save();render();pickGroup(category==='bases'?'bases':'affixes',profile()[category].length-1);};
$('targets').addEventListener('click',e=>{
  const pick=e.target.closest('[data-pick]');if(pick)pickGroup(pick.dataset.pick,Number(pick.dataset.index));
  const del=e.target.closest('[data-delete]');if(del){profile()[category].splice(Number(del.dataset.delete),1);save();render();}
  if(e.target.id==='reset-level'){delete build().profiles.leveling.leveling_slots[levelId];save();render();}
  if(e.target.id==='level-affixes'){
    const data=levelOverride();openPicker('affixes','leveling',data.affixes,data.types,values=>{data.affixes=values;save();render();},[128,129,135].includes(Number(levelId)));
  }
    if(e.target.id==='level-bases'){
    const data=levelOverride();if(data.types.length!==1){toast('这个原入口含多种类型。先使用独立武器／副手入口选择具体类型；原配置保持。',true);return;}
    openPicker('bases','leveling',data.bases,data.types,values=>{data.bases=values;save();render();});
  }
});
$('targets').addEventListener('change',e=>{
  if(e.target.id==='level-slot'){levelId=Number(e.target.value);renderLeveling();}
  if(e.target.id==='level-enabled'){levelOverride().enabled=e.target.checked;save();}
  if(e.target.id==='level-type'){const data=levelOverride();data.types=e.target.value?[e.target.value]:[];data.bases=[];save();render();}
});
['picker-search','only-selected','show-legacy'].forEach(id=>$(id).addEventListener('input',renderPicker));
$('picker-list').onchange=e=>{if(e.target.dataset.id){const id=e.target.dataset.id;if(e.target.checked)selection.chosen.add(id);else selection.chosen.delete(id);$('selection-count').textContent=`已选${selection.chosen.size}项`;}};
$('apply-selection').onclick=()=>{selection.apply([...selection.chosen].map(Number).sort((a,b)=>a-b));$('picker').close();};
document.querySelectorAll('[data-close]').forEach(b=>b.onclick=()=>$(b.dataset.close).close());
$('import-filter').onclick=()=>{$('import-mode').value=mode;$('import-dialog').showModal();};
$('xml-file').onchange=async e=>{if(e.target.files[0]){$('xml-text').value=await e.target.files[0].text();await analyzeImport();}};
$('analyze-import').onclick=()=>analyzeImport();
$('apply-import').onclick=async()=>{
  const assignments=Object.fromEntries([...document.querySelectorAll('[data-import-rule]')].map(el=>[el.dataset.importRule,el.value]));
  await analyzeImport(assignments);if($('apply-import').disabled)return;
  const id=crypto.randomUUID(),stage=$('import-mode').value;
  const b={id,name:imported.name,enabled:true,profiles:{endgame:emptyProfile(),leveling:emptyProfile()},source:{name:$('xml-file').files[0]?.name||'粘贴XML',sha256:imported.source_sha256,warnings:imported.warnings,rules:imported.rules}};
  b.profiles[stage]=copy(imported.profile);config.builds.push(b);activeId=id;mode=stage;category='uniques';view='editor';save();render();$('import-dialog').close();toast('已提取目标，可以逐项核对修改。');
};
$('extra-t7').onchange=e=>{config.extra_t7=e.target.checked;save();};
$('preview-button').onclick=preview;$('preview-search').oninput=renderPreview;
$('export-xml').onclick=async()=>{
  try{const out=await api('/api/generate',{config,mode});await download(out.xml,`LE-filter-${mode}.xml`);toast(`已导出${out.count}条规则。`);}catch(e){toast(e.message,true);}
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
    if(!b){b={id:data.id,name:data.name,enabled:false,profiles:{endgame:emptyProfile(),leveling:emptyProfile()}};config.builds.push(b);}
    b.name=data.name;
    data.profile.leveling_slots=copy(b.profiles[data.stage].leveling_slots);
    b.profiles[data.stage]=data.profile;b.requirement_sources||={};b.requirement_sources[data.stage]=data.source;
    activeId=b.id;mode=data.stage;category='uniques';view='editor';save();render();toast('已载入BD需求，修改后可保存为同一格式的JSON。');
  }catch(e){toast(e.message,true);}finally{e.target.value='';}
};
$('load-config').onclick=()=>$('config-file').click();
$('config-file').onchange=async e=>{
  try{const file=e.target.files[0];if(!file)return;const loaded=JSON.parse(await file.text());await api('/api/validate',{config:loaded});config=loaded;activeId=config.main_id;view='editor';save();render();toast('已载入配置。');}catch(e){toast(e.message,true);}finally{e.target.value='';}
};
$('load-examples').onclick=()=>{config=copy(examples);activeId=config.main_id;category='uniques';mode='endgame';view='editor';save();render();toast('已载入两个BD示例。');};
async function init(){
  try{
    const boot=await api('/api/bootstrap');catalog=boot.catalog;examples=boot.config;
    try{config=JSON.parse(localStorage.getItem(STORAGE));}catch{}
    if(!config||config.version!==1||!Array.isArray(config.builds))config=copy(examples);
    activeId=config.main_id;$('catalog-version').textContent=catalog.version;render();
  }catch(e){toast(`无法启动：${e.message}`,true);}
}
init();
