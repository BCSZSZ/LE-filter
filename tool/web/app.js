const $ = id => document.getElementById(id);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const copy = value => JSON.parse(JSON.stringify(value));
const STORAGE = 'le-filter-workbench-v2';
const LEGACY_STORAGE = 'le-filter-workbench-v1';
const endgameCategories = [
  ['uniques','所需暗金','选择暗金'],
  ['equipment','装备词条','添加部位'],
  ['altars','祭坛词条','添加祭坛'],
  ['idols','神像词条','添加神像'],
  ['bases','所需底材','添加底材']
];
const levelingCategories = [['affixes','所需词条','选择词条'],['bases','所需底材','添加底材']];
const categories = () => mode==='leveling'?levelingCategories:endgameCategories;
let catalog, examples, templates, state, config, activeId, mode='endgame', category='uniques', view='editor', selection, imported, generated, toastTimer, previewRequest=0, draggingAffix;
let profileImport,profileReadController,profileReadRequest=0;
const workspace=globalThis.LEWorkbench;
const currentSave = () => workspace.activeSave(state);
const workbenchReady = () => !!currentSave() && config.builds.some(b=>b.enabled);
const emptyProfile = () => ({uniques:[],equipment:[],altars:[],idols:[],bases:[]});
const emptyLeveling = () => ({affixes:[],bases:[]});
const build = () => config.builds.find(b => b.id === activeId);
const profile = () => build().profiles[mode];
const typeName = t => catalog.types[t]?.zh || t || '未分类';
const label = (kind,id) => catalog[kind][String(id)]?.zh || `未知ID ${id}`;
const baseNames = (type,ids) => ids.map(id=>label('bases',`${type}:${id}`)).join('、');
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
function save(invalidate=true){
  if(invalidate){generated=null;previewRequest++;}
  if(currentSave())currentSave().active_build_id=activeId;
  try{localStorage.setItem(STORAGE,JSON.stringify(state));$('save-state').textContent=currentSave()?'方案已自动保存':'模板选择已记住';}
  catch{$('save-state').textContent='请用“保存配置”备份';}
}
function selectionChanged(){save(false);render();}
function openSave(saved){
  config=saved.config;activeId=saved.active_build_id||config.main_id;mode='endgame';category='uniques';view='editor';save();render();
}
function ensureSave(name){
  if(!currentSave()){
    const saved=workspace.addSave(state,state.draft_config,crypto.randomUUID(),name);
    config=saved.config;
  }
}
function addCustomBuild(){
  const b={id:crypto.randomUUID(),name:`自定义BD ${config.builds.length+1}`,enabled:true,profiles:{endgame:emptyProfile(),leveling:emptyLeveling()}};
  config.builds.push(b);
  if(!config.builds.some(b=>b.enabled&&b.id===config.main_id))config.main_id=b.id;
  activeId=b.id;mode='endgame';category='uniques';view='editor';save();render();
}
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
  const saved=currentSave();config=saved?.config||state.draft_config;
  const selected=config.builds.filter(b=>b.enabled),ready=workbenchReady();
  if(!selected.some(b=>b.id===activeId))activeId=selected.find(b=>b.id===config.main_id)?.id||selected[0]?.id;
  $('templates').innerHTML=templates.map(t=>{
    const checked=state.selection.ids.includes(t.id);
    return `<div class="template-card ${checked?'selected':''}"><label class="template-choice"><input type="checkbox" data-template-enable="${esc(t.id)}" ${checked?'checked':''} aria-label="选择模板：${esc(t.name)}"><strong>${esc(t.name)}</strong></label><small>已有模版 · 只读</small><label class="template-main"><input type="radio" name="template-main" data-template-main="${esc(t.id)}" ${checked&&t.id===state.selection.main_id?'checked':''} ${checked?'':'disabled'} aria-label="将${esc(t.name)}设为主BD">主BD</label></div>`;
  }).join('');
  $('builds').innerHTML=state.saves.map(s=>{
    const members=s.config.builds.filter(b=>b.enabled),main=members.find(b=>b.id===s.config.main_id);
    return `<div class="save-card ${s.id===state.active_save_id?'editing':''}"><button class="build-name" data-save="${esc(s.id)}" aria-pressed="${s.id===state.active_save_id}">${esc(s.name)}</button><small>${members.length}个BD${main?` · 主BD：${esc(main.name)}`:' · 尚未启用BD'}</small><div class="build-meta"><span>${s.id===state.active_save_id?'正在编辑':'点击继续编辑'}</span><button class="remove-build" data-remove-save="${esc(s.id)}" aria-label="删除方案：${esc(s.name)}">×</button></div></div>`;
  }).join('')||'<p class="saved-empty">勾选模版后，点击“用所选模版新建方案”，整个组合保存为一条方案。</p>';
  $('apply-builds').textContent=`用所选模版新建方案（${state.selection.ids.length}）`;
  $('apply-builds').disabled=!state.selection.ids.length;
  const commonView=view==='common';
  $('build-title').textContent=commonView?'共通规则':saved?saved.name:'BD编辑工作台';
  $('workspace-builds').hidden=!saved||!config.builds.length;$('workspace-controls').hidden=!ready;$('workspace-empty').hidden=ready||commonView;
  $('workspace-builds').innerHTML=saved?config.builds.map(b=>`<div class="workspace-bd ${b.enabled&&b.id===activeId?'active':''}"><input type="checkbox" data-enable="${esc(b.id)}" ${b.enabled?'checked':''} aria-label="在方案中启用${esc(b.name)}"><button data-workspace-build="${esc(b.id)}" ${b.enabled?'':'disabled'}><span class="dot ${b.id===config.main_id?'pink':'blue'}"></span>${esc(b.name)}</button><label><input type="radio" name="scheme-main" data-main="${esc(b.id)}" ${b.enabled&&b.id===config.main_id?'checked':''} ${b.enabled?'':'disabled'} aria-label="将方案内${esc(b.name)}设为主BD">主BD</label><button class="remove-build" data-remove-build="${esc(b.id)}" aria-label="从方案移除${esc(b.name)}">×</button></div>`).join(''):'';
  $('workspace-message').textContent=saved?'尚未启用BD':'尚未生成方案';
  $('workspace-help').textContent=saved?'启用方案内的BD，或添加自定义BD。':'在左侧多选已有模版，指定主BD，再点击“用所选模版新建方案”。';
  $('scheme-toolbar').hidden=!saved||commonView;
  $('current-build').textContent=ready?`正在编辑：${build().name}`:'';
  $('rename-save').hidden=!saved||commonView;
  $('rename-build').hidden=!ready||commonView;
  $('reset-build').hidden=!ready||commonView||!templates.some(t=>t.id===(build()?.template_id||activeId));
  $('common-button').classList.toggle('active',commonView);
  ['preview-button','export-xml','save-requirements','extra-t7'].forEach(id=>$(id).disabled=!ready);
  document.querySelectorAll('[data-mode]').forEach(b=>b.classList.toggle('active',b.dataset.mode===mode));
  document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===view));
  $('editor').hidden=!ready||view!=='editor';$('preview').hidden=!ready||view!=='preview';
  $('common-rules').hidden=!commonView;
  $('ultra-rare-targets').innerHTML=chips(catalog.ultra_rare_uniques,'uniques');
  $('common-experimentals-enabled').checked=config.common.exalted_experimentals_enabled;
  $('common-uniques-enabled').checked=config.common.common_uniques_enabled;
  $('common-sets-enabled').checked=config.common.common_sets_enabled;
  $('common-unique-targets').innerHTML=chips(catalog.common_unique_ids,'uniques');
  $('common-set-targets').innerHTML=chips(catalog.common_set_ids,'uniques');
  $('common-uniques-summary').textContent=`查看暗金保护名单（${catalog.common_unique_ids.length}种，含6件T0）`;
  $('common-sets-summary').textContent=`查看全部套装（${catalog.common_set_ids.length}件）`;
  $('common-idols-enabled').checked=config.common.unique_idols_enabled;
  $('common-idol-targets').innerHTML=config.common.unique_idols.length?chips(config.common.unique_idols,'uniques'):'<small>未选择暗金神像</small>';
  $('extra-t7').checked=config.extra_t7;
  if(!ready){['targets','categories','source-info','preview-rules'].forEach(id=>$(id).replaceChildren());$('preview-summary').textContent='';return;}
  $('profile-note').textContent=mode==='endgame'?'命中顺序：彗星红色→灵感橙色→主BD粉色→副BD蓝色→其余档位。至少三T7、双T7中至少一条对应BD目标T7、双T7且三词条（空一栏）为彗星；其余任意双T7为灵感。三词条按未封印的四个普通栏位计数。多T7覆盖全部23类装备，不含神像、祭坛、资源。非目标单T7＋低阶BD目标和额外单T7储备在85级退出。':'0–29级：至少1项目标；30–49级：目标总阶数≥5；50–79级：≥8，单可用目标T≥5；80级退出。命中顺序仍为彗星→灵感→主BD→副BD→通用档。';
  if(!categories().some(c=>c[0]===category))category=categories()[0][0];
  $('categories').innerHTML=categories().map(([key,title],i)=>`<button data-category="${key}" class="${category===key?'active':''}"><span class="step-num">0${i+1}</span>${title}</button>`).join('');
  const item=categories().find(c=>c[0]===category);
  $('category-title').textContent=item[1];$('add-target').textContent=item[2];$('add-target').hidden=!item[2];
  $('category-note').textContent=category==='equipment'?'暗金装备需要的词条，按优先级竖列排列，1为最高。拖动词条放到目标位置，或用↑↓调整。':category==='uniques'?'按装备部位分类。选中任意套装部件，会自动补全整套并加入filter。':'';
  $('category-note').hidden=!['equipment','uniques'].includes(category);
  $('export-xml').textContent='导出filter';
  renderTargets();renderSource();
  if(view==='preview'){
    if(generated)renderPreview();
    else{$('preview-summary').textContent='方案已修改，请重新点击“预览规则”。';$('preview-rules').replaceChildren();}
  }
}
function renderTargets(){
  const data=profile()[category];
  if(!data.length){$('targets').innerHTML=`<div class="empty"><strong>为这个BD选择${categories().find(c=>c[0]===category)[1]}</strong>从列表搜索选择，或导入filter填入目标。</div>`;return;}
  if(category==='uniques'){
    const selected=new Set(data),expanded=workspace.expandUniqueSets(data,catalog);
    $('targets').innerHTML=workspace.groupUniques(expanded,catalog).map(g=>`<section class="target-row unique-slot" aria-label="${esc(g.type?typeName(g.type):'未分类')}暗金"><div class="row-heading"><strong>${esc(g.type?typeName(g.type):'未分类')}</strong><small>${g.ids.length}件</small></div><div class="chips">${g.ids.map(id=>`<span class="chip ${selected.has(id)?'':'auto-set'}">${esc(label('uniques',id))}<small>${id}</small>${selected.has(id)?'':'<em class="auto-set-label">套装补全</em>'}</span>`).join('')}</div></section>`).join('');return;
  }
  if(category==='affixes'){
    $('targets').innerHTML=`<div class="target-row"><div class="chips">${chips(data,category)}</div></div>`;return;
  }
  $('targets').innerHTML=data.map((g,i)=>{
    if(category==='bases'&&mode==='endgame'){
      return `<div class="target-row"><div class="row-heading"><strong>${esc(typeName(g.type))}</strong><div class="row-actions"><button data-pick="preferred_bases" data-index="${i}">首选底材</button><button data-pick="bases" data-index="${i}">替代底材</button><button data-delete="${i}" aria-label="移除此分组">×</button></div></div><div class="chips"><small>首选</small>${g.preferred_bases?.length?chips(g.preferred_bases,'bases',g.type):'<small>未指定</small>'}</div><div class="chips" style="margin-top:12px"><small>替代</small>${g.bases.length?chips(g.bases,'bases',g.type):'<small>未选择</small>'}</div></div>`;
    }
    const commands=`${category!=='bases'?`<button data-pick="affixes" data-index="${i}">${category==='equipment'?'选择词条':'词缀'}</button>`:''}${category==='equipment'?'':`<button data-pick="bases" data-index="${i}">底材</button>`}${category==='idols'?`<button data-pick="pair_bases" data-index="${i}">两项层底材</button>`:''}<button data-delete="${i}" aria-label="移除此分组">×</button>`;
    const bases=g.bases.length?chips(g.bases,'bases',g.type):`<small>${category==='bases'?'未选择底材':'底材不限'}</small>`;
    const title=category==='idols'?(g.bases.length?baseNames(g.type,g.bases):`${typeName(g.type)}（底材不限）`):typeName(g.type);
    const references=category==='bases'?'':[['enchanted','附魔'],['corrupted','腐化']].filter(([key])=>g[key]?.length).map(([key,title])=>`<div class="chips" style="margin-top:12px"><small>${title}参考</small>${chips(g[key],'affixes')}</div>`).join('');
    if(category==='equipment'){
      const ordered=g.affixes.length?`<ol class="affix-priorities" aria-label="${esc(title)}词条优先级">${g.affixes.map((id,j)=>`<li class="chip priority-affix" draggable="true" data-priority-row="${j}" data-group-index="${i}"><span class="drag-handle" aria-hidden="true" title="拖动调整优先级">⠿</span><span class="priority-number" aria-label="优先级${j+1}">${j+1}</span><span class="affix-name">${esc(label('affixes',id))}</span><small>ID${id}</small><span class="priority-actions"><button data-priority="-1" data-index="${i}" data-affix-index="${j}" ${j?'':'disabled'} aria-label="提高${esc(title)}${esc(label('affixes',id))}的优先级" title="提高优先级">↑</button><button data-priority="1" data-index="${i}" data-affix-index="${j}" ${j<g.affixes.length-1?'':'disabled'} aria-label="降低${esc(title)}${esc(label('affixes',id))}的优先级" title="降低优先级">↓</button></span></li>`).join('')}</ol>`:'<small>选择这个部位的暗金装备需要的词条。</small>';
      return `<div class="target-row equipment-slot"><div class="row-heading"><strong>${esc(title)}</strong><div class="row-actions">${commands}</div></div>${ordered}${references}</div>`;
    }
    return `<div class="target-row"><div class="row-heading"><strong>${esc(title)}</strong><div class="row-actions">${commands}</div></div><div class="chips">${bases}</div>${category!=='bases'?`<div class="chips" style="margin-top:12px">${g.affixes.length?chips(g.affixes,'affixes'):'<small>未选择词缀</small>'}</div>`:''}${references}</div>`;
  }).join('');
}
function renderSource(){
  const source=build().requirement_sources?.[mode]||build().source;
  const legacy=mode==='leveling'&&build().legacy_leveling;
  $('source-details').hidden=!source&&!legacy;
  const sourceProfiles=Array.isArray(source?.profiles)?source.profiles.filter(p=>p&&typeof p==='object'):[];
  const links=sourceProfiles.map(p=>{
    try{const url=new URL(p.url);if(url.protocol!=='https:'||url.hostname!=='www.lastepochtools.com')return '';return `<p><a href="${esc(url.href)}" target="_blank" rel="noopener">${esc(p.character)} · ${esc(p.account)}</a>，${Array.isArray(p.items)?p.items.length:0}件物品</p>`;}catch{return '';}
  }).join('');
  const fixed=sourceProfiles.flatMap(p=>(Array.isArray(p.fixed_affix_references)?p.fixed_affix_references:[]).filter(r=>r&&Array.isArray(r.ids)).map(r=>`<p class="reference">${esc(p.character)} · ${esc(r.slot)} · 固定属性参考：${esc(r.ids.map(id=>`${label('affixes',id)} (${id})`).join('、'))}</p>`)).join('');
  $('source-info').innerHTML=(source?`<p>${esc(source.name)}${source.scope?` · ${esc(source.scope)}`:''}</p>${links}${(source.warnings||[]).map(w=>`<p class="warning">${esc(w)}</p>`).join('')}${fixed}`:'')+(legacy?'<p>旧练级配置已转换为两份列表；原始数据随整套配置保存。</p>':'');
}
function openPicker(kind,field,values,types,apply,normalOnly=false,single=false,excluded=[]){
  const eligible=normalOnly?values.filter(id=>[0,5].includes(catalog.affixes[id]?.special)):values;
  selection={kind,field,chosen:new Set(eligible.map(String)),types,apply,normalOnly,single,excluded};
  const prioritized=kind==='affixes'&&field==='equipment';
  $('picker-title').textContent=kind==='uniques'?'选择所需暗金':kind==='bases'?'选择底材':prioritized?'选择暗金装备需要的词条':'选择目标词缀';
  $('picker-note').hidden=!prioritized&&field!=='uniques';
  $('picker-note').textContent=prioritized?'已选词条按优先级排列；新增词条放在最后。应用后可拖放或用↑↓调整。':field==='uniques'?'选中任意套装部件，filter会自动收集对应整套；自动补全项在所需暗金页标注。':'';
  $('picker').classList.toggle('unique-picker',kind==='uniques');
  $('picker-drop-context').hidden=kind!=='uniques';
  $('picker-drop-context').textContent='参考：预言100级／命运12／通用池；Boss按T4／开启者的表内上限。';
  $('picker-search').value='';$('only-selected').checked=false;$('show-legacy').checked=false;
  renderPicker();$('picker').showModal();setTimeout(()=>$('picker-search').focus(),50);
}
function renderPicker(){
  const query=$('picker-search').value.trim().toLowerCase();
  const s=selection;
  const prioritized=s.kind==='affixes'&&s.field==='equipment';
  const priorities=new Map([...s.chosen].map((id,i)=>[id,i+1]));
  const all=Object.values(catalog[s.kind]).filter(a=>{
    const drop=s.kind==='uniques'?catalog.unique_drops?.items?.[a.id]:null;
    if(s.excluded.includes(a.id))return false;
    if(s.field==='common-idols'&&(!(a.type||'').startsWith('IDOL_')||a.id===344))return false;
    const selected=s.chosen.has(String(a.id));
    if(s.kind==='affixes'&&s.normalOnly&&![0,5].includes(a.special))return false;
    if(s.kind==='affixes'&&['equipment','leveling'].includes(s.field)&&[4,6].includes(a.special))return false;
    if(s.kind==='bases'&&(!s.types.includes(a.type)))return false;
    if(s.kind==='affixes'&&s.types.length&&!s.types.some(t=>a.types.includes(t))&&!selected)return false;
    if((a.legacy||a.hidden||drop?.kind==='legacy')&&!$('show-legacy').checked&&!selected)return false;
    if($('only-selected').checked&&!selected)return false;
    return `${a.zh} ${a.en} ${a.id}${s.kind==='uniques'?` ${typeName(a.type)} ${drop?.display?.source||''}`:''}`.toLowerCase().includes(query);
  });
  if(prioritized)all.sort((a,b)=>(priorities.get(String(a.id))??Infinity)-(priorities.get(String(b.id))??Infinity));
  $('picker-summary').textContent=`找到${all.length}项 · ${s.kind==='uniques'?'可搜索名字、ID、部位或掉落来源':'中文、英文和ID均可过滤'}`;
  $('selection-count').textContent=`已选${s.chosen.size}项`;
  if(s.kind==='uniques'){
    $('picker-list').innerHTML=workspace.groupUniques(all.map(a=>a.id),catalog).map(g=>`<section class="unique-pick-group" aria-label="${esc(typeName(g.type))}"><h3 class="unique-group-title">${esc(typeName(g.type))}<span>${g.ids.length}</span></h3>${g.ids.map(id=>uniquePickRow(catalog.uniques[id],s)).join('')}</section>`).join('')||'<div class="empty">没有匹配项，试试名字、部位或掉落来源。</div>';
    return;
  }
  $('picker-list').innerHTML=all.map(a=>`<label class="pick-row"><input type="checkbox" data-id="${a.id}" ${s.chosen.has(String(a.id))?'checked':''}>${prioritized&&s.chosen.has(String(a.id))?`<span class="priority-number" aria-label="优先级${priorities.get(String(a.id))}">${priorities.get(String(a.id))}</span>`:''}<div><strong>${esc(a.zh)}</strong><small>${esc(a.en)}${s.kind==='affixes'?` · ${a.prefix?'前缀':'后缀'}${a.special===4?' · 附魔参考':a.special===6?(s.field==='altars'?' · 腐化目标':' · 腐化参考'):a.special===1?' · 实验词缀':''}`:` · 需求等级${a.level}`}${a.legacy||a.hidden?' · 旧／隐藏条目':''}</small></div><span class="id-tag">${a.id}</span></label>`).join('')||'<div class="empty">没有匹配项，试试英文或ID。</div>';
}
function uniquePickRow(item,s){
  const drop=catalog.unique_drops?.items?.[item.id];
  const info=drop?.display;
  const details=`<div class="unique-drop-record"><span>${esc(info?.source||'来源未收录')}</span><strong>${info?.kind==='world'?'预言':'掉落'}：${esc(info?.probabilityText||'概率未公开')}</strong>${info?.curiosityProbabilityText?`<strong>求索：${esc(info.curiosityProbabilityText)}</strong>`:''}</div>`;
  const icon=drop?.iconUrl?.startsWith('https://')?`<img class="unique-icon" src="${esc(drop.iconUrl)}" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer">`:'';
  return `<div class="unique-pick-row"><label class="unique-choice"><input type="checkbox" data-id="${item.id}" aria-label="选择暗金：${esc(item.zh)}" ${s.chosen.has(String(item.id))?'checked':''}>${icon}<span class="unique-identity"><strong>${esc(item.zh)}</strong><small>${esc(item.en)}</small><small>${item.id}${item.set?' · 套装':''}${item.legacy||item.hidden||drop?.kind==='legacy'?' · 旧／隐藏条目':''}</small></span></label><div class="unique-drop-info">${details}</div></div>`;
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
  $('group-help').textContent=category==='equipment'?'选择装备部位，再选择暗金装备需要的词条；优先级可在装备词条页面调整。':'先选类型，再从可搜索列表选择底材和词缀。';
  $('group-type').innerHTML=types.map(t=>`<option value="${t}">${esc(typeName(t))} ${esc(t.startsWith('IDOL_')&&t!=='IDOL_ALTAR'?t.slice(5):'')}</option>`).join('');
  $('group-dialog').showModal();
}
async function preview(){
  if(!workbenchReady())return toast('请先创建或打开包含已启用BD的保存方案。');
  const request=++previewRequest,saveId=state.active_save_id;
  try{
    generated=null;view='preview';render();$('preview-summary').textContent='正在生成规则…';
    $('preview-button').disabled=true;
    const snapshot=JSON.stringify(config),out=await api('/api/generate',{config});
    if(request!==previewRequest||state.active_save_id!==saveId||view!=='preview'||!workbenchReady()||snapshot!==JSON.stringify(config))return;
    generated=out;render();
  }catch(e){if(request===previewRequest){$('preview-summary').textContent='生成失败，请调整方案后重试。';toast(e.message,true);}}finally{if(request===previewRequest)$('preview-button').disabled=!workbenchReady();}
}
function renderPreview(){
  if(!generated)return;
  const selected=config.builds.filter(b=>b.enabled).map(b=>b.name).join('＋');
  $('preview-summary').textContent=`${selected} · 终局＋练级 · ${generated.count}条规则 / ${generated.enabled}条启用。${generated.warnings.join(' ')}`;
  const query=$('preview-search').value.toLowerCase();
  const rows=generated.rules.filter(r=>`${r.name} ${r.sound} ${r.gate} ${r.types.map(typeName).join(' ')} ${r.types.length===1?baseNames(r.types[0],r.bases):''} ${(r.uniques||[]).map(i=>`${label('uniques',i)} ${i}`).join(' ')}`.toLowerCase().includes(query));
  const colors={'3':['金黄','#ffea00'],'4':['金色','#ffaa00'],'5':['橙色','#ff8000'],'7':['红色','#ff002f'],'8':['粉色','#ff8cef'],'12':['蓝色','#006eff']};
  $('preview-rules').innerHTML=`<table class="preview-table"><thead><tr><th>顺序</th><th>档位</th><th>规则与目标</th><th>条件</th></tr></thead><tbody>${rows.map(r=>`<tr><td>${r.number}${r.enabled?'':'<small>关闭</small>'}</td><td><span class="badge tier-${r.tier}">${esc(r.sound)}</span><small${colors[r.color]?` style="color:${colors[r.color][1]}"`:''}>${esc(r.role)} · ${colors[r.color]?colors[r.color][0]:'原色'}</small></td><td>${esc(r.name)}<small>${esc(r.types.map(typeName).join('、'))}</small>${r.category.startsWith('神像')||r.category.startsWith('祭坛')?`<small>底材：${r.bases.length?esc(baseNames(r.types[0],r.bases)):'不限'}</small>`:''}${r.category.startsWith('终局05')?`<small>底材：${esc(r.bases.map(i=>`${label('bases',`${r.types[0]}:${i}`)}(${i})`).join('、'))}</small>`:''}${r.affixes.flat().length<30?`<small>${esc(r.affixes.flat().map(i=>`${label('affixes',i)}(${i})`).join('、'))}</small>`:''}${r.uniques?.length?`<details><summary>${r.uniques.length}种暗金／套装</summary><small>${esc(r.uniques.map(i=>`${label('uniques',i)}(${i})`).join('、'))}</small></details>`:''}</td><td>${esc(r.gate)}<small>${r.action==='HIDE'?'隐藏':'显示'}</small></td></tr>`).join('')}</tbody></table>`;
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

$('templates').onchange=e=>{
  if(e.target.dataset.templateEnable)workspace.setTemplateEnabled(state,templates,e.target.dataset.templateEnable,e.target.checked);
  if(e.target.dataset.templateMain)workspace.setTemplateMain(state,e.target.dataset.templateMain);
  selectionChanged();
};
$('builds').addEventListener('click',e=>{
  const edit=e.target.closest('[data-save]');if(edit){openSave(workspace.activateSave(state,edit.dataset.save));return;}
  const remove=e.target.closest('[data-remove-save]');if(remove){workspace.removeSave(state,remove.dataset.removeSave);activeId=currentSave()?.active_build_id;view='editor';save();render();}
});
$('apply-builds').onclick=()=>{
  try{const saved=workspace.applyTemplates(state,templates,crypto.randomUUID());openSave(saved);toast(`已将${saved.config.builds.length}个BD合成一条保存方案，可继续编辑并导出filter。`);}catch(e){toast(e.message,true);}
};
$('workspace-builds').addEventListener('change',e=>{
  if(e.target.dataset.enable){const b=config.builds.find(b=>b.id===e.target.dataset.enable);b.enabled=e.target.checked;if(!config.builds.find(b=>b.id===config.main_id)?.enabled)config.main_id=config.builds.find(b=>b.enabled)?.id;}
  if(e.target.dataset.main)config.main_id=e.target.dataset.main;
  save();render();
});
$('workspace-builds').onclick=e=>{
  const b=e.target.closest('[data-workspace-build]');if(b){activeId=b.dataset.workspaceBuild;view='editor';save(false);render();return;}
  const remove=e.target.closest('[data-remove-build]');if(remove){config.builds=config.builds.filter(b=>b.id!==remove.dataset.removeBuild);if(config.main_id===remove.dataset.removeBuild)config.main_id=config.builds.find(b=>b.enabled)?.id;save();render();}
};
$('add-save').onclick=()=>{const saved=workspace.addSave(state,workspace.emptyConfig(config),crypto.randomUUID(),'自定义方案');config=saved.config;addCustomBuild();};
$('add-build').onclick=addCustomBuild;
$('rename-save').onclick=()=>{
  const saved=currentSave(),input=document.createElement('input');input.type='text';input.value=saved.name;input.setAttribute('aria-label','方案名称');$('build-title').replaceChildren(input);input.focus();input.select();
  input.onblur=()=>{saved.name=input.value.trim()||'未命名方案';save();render();};input.onkeydown=e=>{if(e.key==='Enter')input.blur();};
};
$('rename-build').onclick=()=>{
  const b=build(),input=document.createElement('input');input.type='text';input.value=b.name;input.setAttribute('aria-label','BD名称');$('current-build').replaceChildren(input);input.focus();input.select();
  input.onblur=()=>{b.name=input.value.trim()||'未命名BD';save();render();};input.onkeydown=e=>{if(e.key==='Enter')input.blur();};
};
$('reset-build').onclick=()=>{$('reset-name').textContent=build().name;$('reset-dialog').showModal();};
$('confirm-reset').onclick=()=>{
  workspace.resetBuild(config,templates,activeId);$('reset-dialog').close();save();render();toast('这个副本已恢复为最新版模板。');
};
$('common-button').onclick=()=>{view='common';render();};
for(const [id,key] of [['common-experimentals-enabled','exalted_experimentals_enabled'],['common-uniques-enabled','common_uniques_enabled'],['common-sets-enabled','common_sets_enabled']]){
  $(id).onchange=e=>{config.common[key]=e.target.checked;save();render();};
}
$('common-idols-enabled').onchange=e=>{config.common.unique_idols_enabled=e.target.checked;save();render();};
$('pick-common-idols').onclick=()=>openPicker('uniques','common-idols',config.common.unique_idols,[],values=>{
  config.common.unique_idols=values;save();render();
});
document.querySelectorAll('[data-mode]').forEach(b=>b.onclick=()=>{mode=b.dataset.mode;category=categories()[0][0];view='editor';render();});
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{if(b.dataset.view==='preview')preview();else{view='editor';render();}});
$('categories').onclick=e=>{const b=e.target.closest('[data-category]');if(b){category=b.dataset.category;render();}};
$('add-target').onclick=()=>{
  if(category==='uniques'||category==='affixes')openPicker(category,mode==='leveling'?'leveling':category,profile()[category],category==='affixes'?catalog.equipment_types:[],values=>{profile()[category]=values;save();render();});
  else showGroupDialog();
};
$('create-group').onclick=()=>{const g=category==='bases'?{type:$('group-type').value,bases:[]}:{type:$('group-type').value,bases:[],affixes:[],corrupted:[],enchanted:[],sources:[]};if(category==='idols')g.pair_bases=[];profile()[category].push(g);$('group-dialog').close();save();render();pickGroup(category==='bases'?'bases':'affixes',profile()[category].length-1);};
$('targets').addEventListener('click',e=>{
  const priority=e.target.closest('[data-priority]');if(priority){if(workspace.moveAffix(profile().equipment[Number(priority.dataset.index)],Number(priority.dataset.affixIndex),Number(priority.dataset.priority))){save();render();}return;}
  const pick=e.target.closest('[data-pick]');if(pick)pickGroup(pick.dataset.pick,Number(pick.dataset.index));
  const del=e.target.closest('[data-delete]');if(del){profile()[category].splice(Number(del.dataset.delete),1);save();render();}
});
function clearAffixDrag(){
  draggingAffix=null;document.querySelectorAll('.priority-affix').forEach(row=>row.classList.remove('dragging','drop-before','drop-after'));
}
function acceptsAffixDrop(row){
  return row&&draggingAffix&&category==='equipment'&&mode==='endgame'&&draggingAffix.saveId===state.active_save_id&&draggingAffix.buildId===activeId&&draggingAffix.group===Number(row.dataset.groupIndex);
}
$('targets').addEventListener('dragstart',e=>{
  const row=e.target.closest('[data-priority-row]');if(!row||category!=='equipment')return;
  draggingAffix={saveId:state.active_save_id,buildId:activeId,group:Number(row.dataset.groupIndex),from:Number(row.dataset.priorityRow)};
  e.dataTransfer.effectAllowed='move';e.dataTransfer.setData('text/plain',String(draggingAffix.from));row.classList.add('dragging');
});
$('targets').addEventListener('dragover',e=>{
  const row=e.target.closest('[data-priority-row]');if(!acceptsAffixDrop(row))return;
  e.preventDefault();e.dataTransfer.dropEffect='move';
  document.querySelectorAll('.priority-affix').forEach(r=>r.classList.remove('drop-before','drop-after'));
  const rect=row.getBoundingClientRect();row.classList.add(e.clientY<rect.top+rect.height/2?'drop-before':'drop-after');
});
$('targets').addEventListener('drop',e=>{
  const row=e.target.closest('[data-priority-row]');if(!acceptsAffixDrop(row)){clearAffixDrag();return;}
  e.preventDefault();
  const rect=row.getBoundingClientRect(),from=draggingAffix.from,group=profile().equipment[draggingAffix.group];
  let to=Number(row.dataset.priorityRow)+(e.clientY<rect.top+rect.height/2?0:1);if(from<to)to--;
  clearAffixDrag();if(workspace.placeAffix(group,from,to)){save();render();}
});
$('targets').addEventListener('dragend',clearAffixDrag);
['picker-search','only-selected','show-legacy'].forEach(id=>$(id).addEventListener('input',renderPicker));
$('picker-list').onchange=e=>{if(e.target.dataset.id){const id=e.target.dataset.id;if(e.target.checked){if(selection.single)selection.chosen.clear();selection.chosen.add(id);}else selection.chosen.delete(id);if(selection.single||selection.kind==='affixes'&&selection.field==='equipment'||$('only-selected').checked)renderPicker();else $('selection-count').textContent=`已选${selection.chosen.size}项`;}};
$('picker-list').addEventListener('error',e=>{if(e.target.matches('.unique-icon'))e.target.hidden=true;},true);
$('apply-selection').onclick=()=>{selection.apply(workspace.selectionValues(selection.chosen,selection.kind==='affixes'&&selection.field==='equipment'));$('picker').close();};
document.querySelectorAll('[data-close]').forEach(b=>b.onclick=()=>$(b.dataset.close).close());
$('sidebar-more').addEventListener('click',e=>{if(e.target.closest('button'))$('sidebar-more').open=false;});
$('import-filter').onclick=()=>{$('import-mode').value=mode;$('import-dialog').showModal();};
$('xml-file').onchange=async e=>{if(e.target.files[0]){$('xml-text').value=await e.target.files[0].text();await analyzeImport();}};
$('analyze-import').onclick=()=>analyzeImport();
$('apply-import').onclick=async()=>{
  const assignments=Object.fromEntries([...document.querySelectorAll('[data-import-rule]')].map(el=>[el.dataset.importRule,el.value]));
  await analyzeImport(assignments);if($('apply-import').disabled)return;
  const id=crypto.randomUUID(),stage=$('import-mode').value;
  const b={id,name:imported.name,enabled:true,profiles:{endgame:emptyProfile(),leveling:emptyLeveling()},source:{name:$('xml-file').files[0]?.name||'粘贴XML',sha256:imported.source_sha256,warnings:imported.warnings,rules:imported.rules}};
  ensureSave(imported.name);b.profiles[stage]=copy(stage==='leveling'?imported.leveling_profile:imported.profile);config.builds.push(b);if(!config.builds.some(b=>b.enabled&&b.id===config.main_id))config.main_id=id;activeId=id;mode=stage;category=categories()[0][0];view='editor';save();render();$('import-dialog').close();toast('已将新BD加入当前保存方案，请核对目标后导出。');
};
$('extra-t7').onchange=e=>{config.extra_t7=e.target.checked;save();render();};
$('preview-button').onclick=preview;$('preview-search').oninput=renderPreview;
$('export-xml').onclick=async()=>{
  if(!workbenchReady())return toast('请先创建或打开包含已启用BD的保存方案。');
  try{const out=await api('/api/generate',{config});await download(out.xml,'LE-filter.xml');toast(`已导出${out.count}条规则，包含终局和练级目标。${out.warnings.join(' ')}`);}catch(e){toast(e.message,true);}
};
$('save-config').onclick=async()=>{try{await download(JSON.stringify(state,null,2),'LE-filter-workspaces.json');toast('已备份全部保存方案及各方案的主BD、两阶段目标和共通规则。');}catch(e){toast(e.message,true);}};
$('save-requirements').onclick=async()=>{
  try{const document=await api('/api/requirements/export',{build:build(),stage:mode});await download(JSON.stringify(document,null,2),'LE-filter-requirements.json');toast(`已保存本BD的${mode==='endgame'?'终局':'练级'}需求。`);}catch(e){toast(e.message,true);}
};
$('import-requirements').onclick=()=>$('requirements-file').click();
$('import-profiles').onclick=()=>$('profiles-dialog').showModal();
function invalidateProfiles(){
  profileReadRequest++;profileReadController?.abort();profileReadController=null;
  profileImport=null;$('apply-profiles').disabled=true;$('profiles-result').textContent='';
  $('read-profiles').disabled=false;$('read-profiles').textContent='读取角色并预览并集';
}
$('profiles-links').oninput=invalidateProfiles;
$('profiles-dialog').addEventListener('close',invalidateProfiles);
$('read-profiles').onclick=async()=>{
  invalidateProfiles();
  const request=profileReadRequest;
  try{
    const urls=LEProfileImport.normalizeLinks($('profiles-links').value);
    profileReadController=new AbortController();
    const signal=AbortSignal.any([profileReadController.signal,AbortSignal.timeout(100000)]);
    $('read-profiles').disabled=true;$('read-profiles').textContent='正在读取…';
    $('profiles-result').textContent=`正在读取${urls.length}个不同角色的当前配装，请稍候…`;
    const bundle=await LEProfileImport.readProfiles(urls,{name:$('profiles-name').value,signal});
    if(request!==profileReadRequest)return;
    await analyzeProfiles(bundle,request);
  }catch(e){if(request===profileReadRequest&&e.name!=='AbortError'){$('profiles-result').textContent=`读取失败：${e.message} 本次未保存任何目标。`;toast(e.message,true);}}
  finally{if(request===profileReadRequest){profileReadController=null;$('read-profiles').disabled=false;$('read-profiles').textContent='读取角色并预览并集';}}
};
async function analyzeProfiles(bundle,request=profileReadRequest){
  profileImport=null;$('apply-profiles').disabled=true;$('profiles-result').textContent='正在核对角色ID与目标分类…';
  if(!$('profiles-dialog').open)$('profiles-dialog').showModal();
  try{
    const result=await api('/api/profiles/import',{bundle});
    if(request!==profileReadRequest)return;
    profileImport=result;
    if(!$('profiles-name').value.trim())$('profiles-name').value=profileImport.name;
    $('profiles-links').value=profileImport.source.profiles.map(p=>p.url).join('\n');
    $('profiles-result').innerHTML=`<h3>${esc(profileImport.source.name)}</h3><div class="import-summary">${endgameCategories.map(([key,title])=>`<span class="stat">${title} <strong>${profileImport.profile[key].length}</strong>${key==='uniques'?'项':'组'}</span>`).join('')}</div><p>腐化／附魔参考单列，练级目标留空。保存后可逐项编辑、预览和导出filter。</p>${profileImport.source.warnings.map(w=>`<p class="warning">${esc(w)}</p>`).join('')}<details><summary>查看${profileImport.source.profiles.length}个来源角色</summary>${profileImport.source.profiles.map(p=>`<p><a href="${esc(p.url)}" target="_blank" rel="noopener">${esc(p.character)} · ${esc(p.account)}</a>，${p.items.length}件物品</p>`).join('')}</details>`;
    $('apply-profiles').disabled=false;
  }catch(e){if(request===profileReadRequest){$('profiles-result').textContent=`导入失败：${e.message}`;toast(e.message,true);}}
}
$('profiles-file').onchange=async e=>{
  invalidateProfiles();const request=profileReadRequest;
  try{const file=e.target.files[0];if(file){if(file.size>1024*1024)throw Error('角色JSON超过1MB。');const text=await file.text();if(request===profileReadRequest)await analyzeProfiles(JSON.parse(text),request);}}
  catch(error){if(request===profileReadRequest){profileImport=null;$('apply-profiles').disabled=true;$('profiles-result').textContent=error.message;toast(error.message,true);}}
  finally{e.target.value='';}
};
$('apply-profiles').onclick=()=>{
  if(!profileImport)return;
  const data={...profileImport,name:$('profiles-name').value.trim()||profileImport.name};
  const saved=workspace.importProfiles(state,data,crypto.randomUUID(),crypto.randomUUID(),$('profiles-destination').value);
  $('profiles-dialog').close();openSave(saved);toast('角色并集已保存为个人BD，可编辑并导出filter。');
};
$('requirements-file').onchange=async e=>{
  try{
    const file=e.target.files[0];if(!file)return;
    const data=await api('/api/requirements/import',{document:JSON.parse(await file.text())});
    ensureSave(data.name);
    const b=workspace.importRequirement(config,templates,data);
    activeId=b.id;mode=data.stage;category=categories()[0][0];view='editor';save();render();toast('已更新当前保存方案中的BD需求，另一阶段及主BD设置保留。');
  }catch(e){toast(e.message,true);}finally{e.target.value='';}
};
$('load-config').onclick=()=>$('config-file').click();
$('config-file').onchange=async e=>{
  try{
    const file=e.target.files[0];if(!file)return;
    const loaded=await validateState(workspace.restore(examples,JSON.parse(await file.text())));
    if(!loaded.saves.length){state.draft_config=loaded.draft_config;state.selection=loaded.selection;save();render();toast('文件没有保存方案，已载入模板选择及共通规则草稿。');return;}
    openSave(workspace.mergeSaves(state,loaded,()=>crypto.randomUUID()));toast(`已加入${loaded.saves.length}条保存方案，已有保存保留。`);
  }catch(e){toast(e.message,true);}finally{e.target.value='';}
};
async function validateState(loaded){
  loaded.draft_config=(await api('/api/validate',{config:loaded.draft_config})).config;
  for(const saved of loaded.saves)saved.config=(await api('/api/validate',{config:saved.config})).config;
  return loaded;
}
async function init(){
  try{
    if(globalThis.LEFilterAPI){document.querySelector('.layout').inert=true;document.querySelector('.top-actions').inert=true;$('save-state').textContent='首次加载，请稍候…';}
    const boot=await api('/api/bootstrap');catalog=boot.catalog;examples=boot.config;templates=workspace.library(examples);
    let saved;
    let stored;try{stored=localStorage.getItem(STORAGE)??localStorage.getItem(LEGACY_STORAGE);}catch{}
    if(stored)saved=JSON.parse(stored);
    state=await validateState(workspace.restore(examples,saved));config=currentSave()?.config||state.draft_config;
    activeId=currentSave()?.active_build_id||config.main_id;$('catalog-version').textContent=catalog.version;render();save();
    document.querySelector('.layout').inert=false;document.querySelector('.top-actions').inert=false;
  }catch(e){toast(`无法启动：${e.message}`,true);}
}
init();
