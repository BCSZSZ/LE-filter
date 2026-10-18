/* Template selection is a draft; each saved scheme owns a complete engine config. */
(function(root){
  const copy = value => JSON.parse(JSON.stringify(value));
  const FORMAT = 'le-filter-workspaces';
  const emptyProfile = () => ({uniques:[],equipment:[],altars:[],idols:[],bases:[]});
  const emptyLeveling = () => ({affixes:[],bases:[]});
  function freeze(value){
    Object.values(value).forEach(v=>{if(v&&typeof v==='object')freeze(v);});
    return Object.freeze(value);
  }
  function library(examples){return freeze(copy(examples.builds));}
  function emptyConfig(examples){return {...copy(examples),main_id:null,builds:[]};}
  function defaultSelection(examples){
    const ids=examples.builds.filter(b=>b.enabled).map(b=>b.id);
    return {ids,main_id:ids.includes(examples.main_id)?examples.main_id:ids[0]||null};
  }
  function configShape(config){
    if(!config||config.version!==1||!Array.isArray(config.builds))throw Error('方案配置格式不正确。');
    const ids=new Set();
    for(const b of config.builds){
      if(!b||typeof b.id!=='string'||!b.id||ids.has(b.id)||typeof b.name!=='string'||typeof b.enabled!=='boolean'||!b.profiles?.endgame||!b.profiles?.leveling)throw Error('方案中的BD格式不正确或ID重复。');
      ids.add(b.id);
    }
    const selected=config.builds.filter(b=>b.enabled);
    if(selected.length&&!selected.some(b=>b.id===config.main_id))throw Error('请从方案已启用的BD中选择主BD。');
  }
  function attachOrigins(config,examples){
    for(const b of config.builds)if(!b.template_id&&examples.builds.some(t=>t.id===b.id))b.template_id=b.id;
  }
  function schemeName(config){return config.builds.filter(b=>b.enabled).map(b=>b.name).join(' ＋ ')||'我的方案';}
  function activeSave(state){return state.saves.find(s=>s.id===state.active_save_id);}
  function addSave(state,config,id,name=schemeName(config)){
    configShape(config);
    if(typeof id!=='string'||!id||state.saves.some(s=>s.id===id))throw Error('保存方案的ID重复或无效。');
    const saved={id,name,config:copy(config),active_build_id:config.main_id};
    state.saves.push(saved);state.active_save_id=id;
    return saved;
  }
  function restore(examples,saved){
    const state={format:FORMAT,version:2,selection:defaultSelection(examples),draft_config:emptyConfig(examples),saves:[],active_save_id:null};
    if(!saved)return state;
    if(saved.version===1&&Array.isArray(saved.builds)){
      configShape(saved);
      const config=copy(saved);attachOrigins(config,examples);
      const ids=config.builds.filter(b=>b.enabled).map(b=>b.template_id).filter(Boolean);
      state.selection={ids:[...new Set(ids)],main_id:config.builds.find(b=>b.id===config.main_id)?.template_id||ids[0]||null};
      state.draft_config={...copy(config),main_id:null,builds:[]};
      if(config.builds.length)addSave(state,config,'legacy-workspace',schemeName(config));
      return state;
    }
    if(saved.format!==FORMAT||saved.version!==2||!Array.isArray(saved.saves)||!Array.isArray(saved.selection?.ids))throw Error('这不是支持的保存方案文件。');
    const restored=copy(saved),ids=new Set();
    configShape(restored.draft_config);
    if(restored.draft_config.builds.length)throw Error('模板选择草稿不能包含BD副本。');
    for(const s of restored.saves){
      if(!s||typeof s.id!=='string'||!s.id||ids.has(s.id)||typeof s.name!=='string')throw Error('保存方案格式不正确或ID重复。');
      configShape(s.config);attachOrigins(s.config,examples);ids.add(s.id);
    }
    restored.selection.ids=[...new Set(restored.selection.ids)].filter(id=>examples.builds.some(t=>t.id===id));
    if(!restored.selection.ids.includes(restored.selection.main_id))restored.selection.main_id=restored.selection.ids[0]||null;
    if(restored.active_save_id!==null&&!ids.has(restored.active_save_id))throw Error('找不到当前保存方案。');
    return restored;
  }
  function setTemplateEnabled(state,templates,id,enabled){
    if(!templates.some(t=>t.id===id))throw Error('找不到这个模板。');
    const ids=new Set(state.selection.ids);
    if(enabled)ids.add(id);else ids.delete(id);
    state.selection.ids=templates.filter(t=>ids.has(t.id)).map(t=>t.id);
    if(!ids.has(state.selection.main_id))state.selection.main_id=state.selection.ids[0]||null;
  }
  function setTemplateMain(state,id){
    if(!state.selection.ids.includes(id))throw Error('请先勾选这个BD。');
    state.selection.main_id=id;
  }
  function applyTemplates(state,templates,id){
    const selected=templates.filter(t=>state.selection.ids.includes(t.id));
    if(!selected.length)throw Error('请先选择至少一个已有模版。');
    if(!selected.some(t=>t.id===state.selection.main_id))throw Error('请从已选模板中选择主BD。');
    const settings=activeSave(state)?.config||state.draft_config;
    const config={...copy(settings),main_id:state.selection.main_id,builds:selected.map(t=>({...copy(t),enabled:true,template_id:t.id}))};
    return addSave(state,config,id);
  }
  function activateSave(state,id){
    const saved=state.saves.find(s=>s.id===id);
    if(!saved)throw Error('找不到这个保存方案。');
    state.active_save_id=id;return saved;
  }
  function removeSave(state,id){
    const index=state.saves.findIndex(s=>s.id===id);
    if(index<0)return;
    state.saves.splice(index,1);
    if(state.active_save_id===id)state.active_save_id=state.saves[Math.min(index,state.saves.length-1)]?.id||null;
  }
  function mergeSaves(state,incoming,newId){
    let active;
    for(const saved of incoming.saves){
      const added=addSave(state,saved.config,newId(),saved.name);
      added.active_build_id=saved.active_build_id;
      if(saved.id===incoming.active_save_id)active=added;
    }
    if(active)state.active_save_id=active.id;
    return activeSave(state);
  }
  function resetBuild(config,templates,id){
    const index=config.builds.findIndex(b=>b.id===id),b=config.builds[index];
    const template=templates.find(t=>t.id===(b?.template_id||b?.id));
    if(!template)throw Error('这个BD没有对应的已有模版。');
    config.builds[index]={...copy(template),id:b.id,name:b.name,enabled:b.enabled,template_id:template.id};
    return config.builds[index];
  }
  function importRequirement(config,templates,data){
    let b=config.builds.find(b=>b.id===data.id);
    if(!b){
      b={id:data.id,name:data.name,enabled:true,profiles:{endgame:emptyProfile(),leveling:emptyLeveling()}};
      if(templates.some(t=>t.id===data.id))b.template_id=data.id;
      config.builds.push(b);
      if(!config.builds.some(b=>b.enabled&&b.id===config.main_id))config.main_id=b.id;
    }
    b.name=data.name;b.profiles[data.stage]=copy(data.profile);
    b.requirement_sources||={};b.requirement_sources[data.stage]=copy(data.source);
    return b;
  }
  function importProfiles(state,data,buildId,saveId,destination='new-save'){
    let saved=activeSave(state);
    if(destination==='new-save'||!saved)saved=addSave(state,emptyConfig(saved?.config||state.draft_config),saveId,data.name);
    if(saved.config.builds.some(b=>b.id===buildId))throw Error('个人BD的ID重复。');
    const b={id:buildId,name:data.name,enabled:true,profiles:{endgame:copy(data.profile),leveling:emptyLeveling()},requirement_sources:{endgame:copy(data.source)}};
    saved.config.builds.push(b);
    if(!saved.config.builds.some(b=>b.enabled&&b.id===saved.config.main_id))saved.config.main_id=b.id;
    saved.active_build_id=b.id;return saved;
  }
  function selectionValues(chosen,preserveOrder=false){
    const values=[...chosen].map(Number);
    return preserveOrder?values:values.sort((a,b)=>a-b);
  }
  function moveAffix(group,index,offset){
    const next=index+offset;
    if(!Number.isInteger(index)||![-1,1].includes(offset)||index<0||index>=group.affixes.length||next<0||next>=group.affixes.length)return false;
    [group.affixes[index],group.affixes[next]]=[group.affixes[next],group.affixes[index]];
    return true;
  }
  function placeAffix(group,from,to){
    if(!Number.isInteger(from)||!Number.isInteger(to)||from<0||to<0||from>=group.affixes.length||to>=group.affixes.length||from===to)return false;
    const [id]=group.affixes.splice(from,1);group.affixes.splice(to,0,id);return true;
  }
  function expandUniqueSets(ids,catalog){
    const result=new Set(ids),selected=new Set(ids);
    for(const group of Object.values(catalog.item_sets))if(group.members.some(id=>selected.has(id)))group.members.forEach(id=>result.add(id));
    return [...result];
  }
  function groupUniques(ids,catalog){
    const groups=new Map();
    for(const id of ids){
      const type=catalog.uniques[String(id)]?.type||null;
      if(!groups.has(type))groups.set(type,{type,ids:[]});
      groups.get(type).ids.push(id);
    }
    const order=new Map(catalog.equipment_types.map((type,i)=>[type,i]));
    return [...groups.values()].sort((a,b)=>(order.get(a.type)??order.size)-(order.get(b.type)??order.size));
  }
  function uniquePickerGroups(ids,chosen,catalog){
    const selected=[],remaining=[];
    for(const group of groupUniques(ids,catalog)){
      const others=[];
      for(const id of group.ids)(chosen.has(String(id))?selected:others).push(id);
      if(others.length)remaining.push({type:group.type,ids:others});
    }
    return selected.length?[{selected:true,ids:selected},...remaining]:remaining;
  }
  function prepareFastState(state,defaults){
    const configs=[state.draft_config,...state.saves.map(s=>s.config)];
    // Only current profiles can bypass the blocking migration. Python retains
    // all target validation and the conversion of legacy leveling formats.
    if(configs.some(c=>c.common!==undefined&&(c.common===null||typeof c.common!=='object'||Array.isArray(c.common))||c.builds.some(b=>
      !Array.isArray(b.profiles.leveling.affixes)||!Array.isArray(b.profiles.leveling.bases)||
      'leveling_slots' in b.profiles.endgame||
      ['uniques','equipment','altars','idols','bases'].some(k=>!Array.isArray(b.profiles.endgame[k])))))return false;
    const settings=configs.map(c=>({...copy(defaults),...c.common}));
    if(settings.some(c=>!Array.isArray(c.unique_idols)||c.unique_idols.some(id=>!Number.isInteger(id)||!defaults.unique_idols.includes(id))||
      Object.keys(defaults).some(k=>typeof defaults[k]==='boolean'&&typeof c[k]!=='boolean')))return false;
    configs.forEach((c,i)=>{c.common=settings[i];c.common.unique_idols=[...new Set(c.common.unique_idols)].sort((a,b)=>a-b);});
    return true;
  }
  const api={library,restore,emptyConfig,activeSave,addSave,setTemplateEnabled,setTemplateMain,applyTemplates,activateSave,removeSave,mergeSaves,resetBuild,importRequirement,importProfiles,selectionValues,moveAffix,placeAffix,expandUniqueSets,groupUniques,uniquePickerGroups,prepareFastState};
  root.LEWorkbench=api;
  if(typeof module!=='undefined')module.exports=api;
})(globalThis);
