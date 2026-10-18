const test=require('node:test');
const assert=require('node:assert/strict');
const path=require('node:path');
const W=require('./web/workbench.js');
const copy=x=>JSON.parse(JSON.stringify(x));
function fixtures(){
  const documents=['flay-lich-allie-guide','bleed-skeleton-roamer-guide-835'].map(id=>require(path.join('..','requirements',id+'.endgame.json')));
  return {version:1,main_id:documents[0].id,extra_t7:true,common:{unique_idols_enabled:true,unique_idols:[211]},builds:documents.map((d,i)=>({
    id:d.id,name:d.name,enabled:i===0,profiles:{endgame:copy(d.targets),leveling:{affixes:[502],bases:[]}},requirement_sources:{endgame:copy(d.source)}
  }))};
}
function setup(){const examples=fixtures();return {examples,templates:W.library(examples),state:W.restore(examples)};}

test('fresh visits and multi-selecting templates create no saved copies',()=>{
  const {templates,state}=setup();
  assert.deepEqual(state.saves,[]);assert.equal(state.active_save_id,null);assert.deepEqual(state.draft_config.builds,[]);
  W.setTemplateEnabled(state,templates,templates[1].id,true);W.setTemplateMain(state,templates[1].id);
  assert.deepEqual(state.selection,{ids:templates.map(t=>t.id),main_id:templates[1].id});
  assert.deepEqual(state.saves,[]);assert.deepEqual(state.draft_config.builds,[]);
  W.setTemplateEnabled(state,templates,templates[1].id,false);
  assert.equal(state.selection.main_id,templates[0].id);
  W.setTemplateEnabled(state,templates,templates[0].id,false);
  assert.equal(state.selection.main_id,null);assert.throws(()=>W.applyTemplates(state,templates,'empty'));
  assert.deepEqual(state.saves,[]);
});

test('Apply creates exactly one editable combined scheme with the chosen main BD',()=>{
  const {examples,templates,state}=setup(),before=copy(examples);
  W.setTemplateEnabled(state,templates,templates[1].id,true);W.setTemplateMain(state,templates[1].id);
  const saved=W.applyTemplates(state,templates,'combined');
  assert.equal(state.saves.length,1);assert.equal(W.activeSave(state),saved);
  assert.equal(saved.config.main_id,templates[1].id);assert.equal(saved.config.builds.length,2);
  for(const b of saved.config.builds){const t=templates.find(t=>t.id===b.id);assert.deepEqual(b.profiles,t.profiles);assert.deepEqual(b.requirement_sources,t.requirement_sources);assert.equal(b.enabled,true);}
  assert.equal(saved.config.builds[0].profiles.endgame.idols.length,5);
  assert.deepEqual(saved.config.builds[0].profiles.endgame.altars[0].bases,[3]);
  saved.name='我的组合';saved.config.builds[0].profiles.endgame.idols=[];saved.config.common.unique_idols=[];
  assert.deepEqual(templates,before.builds);assert.deepEqual(examples,before);assert.ok(Object.isFrozen(templates[0].profiles.endgame.idols));
});

test('changing pending selections never changes the current saved scheme or its main BD',()=>{
  const {examples,templates,state}=setup();W.setTemplateEnabled(state,templates,templates[1].id,true);
  const saved=W.applyTemplates(state,templates,'old');saved.config.builds[0].profiles.leveling.affixes=[406];
  const before=copy(state.saves);
  W.setTemplateMain(state,templates[1].id);W.setTemplateEnabled(state,templates,templates[0].id,false);W.selectDefaults(state,examples);
  assert.deepEqual(state.saves,before);assert.equal(state.active_save_id,'old');
});

test('applying again creates a fresh single record and keeps existing edits',()=>{
  const {templates,state}=setup();const old=W.applyTemplates(state,templates,'old');
  old.name='旧编辑';old.config.builds[0].profiles.endgame.idols=[];old.config.builds[0].profiles.leveling.affixes=[406];old.config.common.unique_idols=[];
  const before=copy(old);W.setTemplateEnabled(state,templates,templates[1].id,true);W.setTemplateMain(state,templates[1].id);
  const fresh=W.applyTemplates(state,templates,'new');
  assert.equal(state.saves.length,2);assert.equal(fresh.config.builds.length,2);assert.deepEqual(old,before);
  assert.equal(fresh.config.builds[0].profiles.endgame.idols.length,5);assert.deepEqual(fresh.config.builds[0].profiles.leveling.affixes,[502]);
  assert.equal(fresh.config.main_id,templates[1].id);assert.deepEqual(fresh.config.common.unique_idols,[]);
  fresh.config.common.unique_idols.push(211);assert.deepEqual(old.config.common.unique_idols,[]);
  assert.throws(()=>W.applyTemplates(state,templates,'new'));assert.equal(state.saves.length,2);
});

test('reopening and reloading saved schemes retain independent targets, main BDs and draft choices',()=>{
  const {examples,templates,state}=setup();const first=W.applyTemplates(state,templates,'first');
  first.config.builds[0].name='改名';first.config.builds[0].profiles.endgame.idols=[];
  W.setTemplateEnabled(state,templates,templates[1].id,true);W.setTemplateMain(state,templates[1].id);
  const second=W.applyTemplates(state,templates,'second');second.active_build_id=templates[0].id;second.config.extra_t7=false;
  W.activateSave(state,'first');assert.deepEqual(first.config.builds[0].profiles.endgame.idols,[]);assert.equal(first.config.main_id,templates[0].id);
  const restored=W.restore(examples,JSON.parse(JSON.stringify(state)));
  assert.deepEqual(restored,state);assert.equal(W.activeSave(restored).id,'first');assert.equal(restored.selection.main_id,templates[1].id);
  assert.equal(W.activateSave(restored,'second').active_build_id,templates[0].id);assert.equal(W.activeSave(restored).config.main_id,templates[1].id);
});

test('legacy browser saves migrate into one scheme, retaining disabled BDs, both stages and references',()=>{
  const examples=fixtures(),old=copy(examples);old.builds[0].name='旧保存';old.builds[0].profiles.endgame.idols=[];
  old.builds[1].profiles.leveling.affixes=[406];old.builds[1].source={name:'原始来源'};old.builds[0].legacy_leveling={equipment:['原记录']};old.common.unique_idols=[];old.extra_t7=false;
  const before=copy(old),restored=W.restore(examples,old),config=W.activeSave(restored).config;
  assert.equal(restored.saves.length,1);assert.equal(config.builds.length,2);
  config.builds.forEach((b,i)=>{assert.deepEqual(b.profiles,before.builds[i].profiles);assert.equal(b.enabled,before.builds[i].enabled);assert.equal(b.name,before.builds[i].name);});
  assert.deepEqual(config.builds[1].source,before.builds[1].source);assert.deepEqual(config.builds[0].legacy_leveling,before.builds[0].legacy_leveling);
  assert.deepEqual(config.common,before.common);assert.equal(config.extra_t7,false);assert.equal(config.main_id,before.main_id);assert.deepEqual(old,before);
  assert.deepEqual(W.restore(examples,JSON.parse(JSON.stringify(restored))),restored);
});

test('legacy custom BDs remain editable without adding them to the official library',()=>{
  const examples=fixtures(),old=copy(examples);old.builds[0].id='custom';old.main_id='custom';
  const state=W.restore(examples,old);
  assert.equal(W.activeSave(state).config.main_id,'custom');assert.deepEqual(state.selection.ids,[]);assert.equal(examples.builds.length,2);
  const empty=W.restore(examples,{...old,builds:[],main_id:null});assert.deepEqual(empty.saves,[]);assert.deepEqual(empty.draft_config.common,old.common);
});

test('importing a backup adds independent complete schemes without replacing current saves',()=>{
  const {examples,templates,state}=setup();const first=W.applyTemplates(state,templates,'first');
  W.setTemplateEnabled(state,templates,templates[1].id,true);W.setTemplateMain(state,templates[1].id);W.applyTemplates(state,templates,'second');W.activateSave(state,'first');
  const original=copy(state),incoming=W.restore(examples,original);let sequence=0;
  W.mergeSaves(state,incoming,()=>`imported-${++sequence}`);
  assert.equal(state.saves.length,4);assert.deepEqual(state.saves.slice(0,2),original.saves);assert.equal(state.active_save_id,'imported-1');
  assert.deepEqual(state.saves[3].config,original.saves[1].config);W.activeSave(state).config.builds[0].profiles.endgame.idols=[];
  assert.equal(first.config.builds[0].profiles.endgame.idols.length,5);assert.deepEqual(incoming,original);
});

test('explicit BD reset affects only that member of the active combined scheme',()=>{
  const {templates,state}=setup();W.setTemplateEnabled(state,templates,templates[1].id,true);
  const saved=W.applyTemplates(state,templates,'combined'),config=saved.config,b=config.builds[0];b.name='玩家名称';b.profiles.endgame.idols=[];
  const otherBefore=copy(config.builds[1]),main=config.main_id,common=copy(config.common);
  W.resetBuild(config,templates,b.id);
  assert.deepEqual(config.builds[0].profiles,templates[0].profiles);assert.equal(config.builds[0].name,'玩家名称');assert.deepEqual(config.builds[1],otherBefore);
  assert.equal(config.main_id,main);assert.deepEqual(config.common,common);assert.equal(state.saves.length,1);
});

test('same-id requirements update one stage in one scheme and preserve ownership and main BD',()=>{
  const {templates,state}=setup();const first=W.applyTemplates(state,templates,'first'),second=W.applyTemplates(state,templates,'second');
  const b=second.config.builds[0],leveling=copy(b.profiles.leveling),firstBefore=copy(first),templateBefore=copy(templates);
  const data={id:b.id,name:'玩家补充',stage:'endgame',profile:{uniques:[],equipment:[],idols:[],altars:[],bases:[]},source:{name:'玩家JSON'}};
  W.importRequirement(second.config,templates,data);
  assert.equal(b.enabled,true);assert.equal(second.config.main_id,b.id);assert.deepEqual(b.profiles.leveling,leveling);
  assert.deepEqual(b.profiles.endgame,data.profile);assert.deepEqual(first,firstBefore);assert.deepEqual(templates,templateBefore);
  b.profiles.endgame.uniques.push(211);assert.deepEqual(data.profile.uniques,[]);
  b.enabled=false;second.config.main_id=null;W.importRequirement(second.config,templates,data);assert.equal(b.enabled,false);
});

test('explicitly imported new BDs join only the active scheme and can establish its main BD',()=>{
  const {examples,templates,state}=setup();const saved=W.addSave(state,W.emptyConfig(examples),'custom','自定义方案');
  const b=W.importRequirement(saved.config,templates,{id:'my-build',name:'自定义',stage:'leveling',profile:{affixes:[406],bases:[]},source:{}});
  assert.equal(b.enabled,true);assert.equal(saved.config.main_id,b.id);assert.deepEqual(b.profiles.endgame,{uniques:[],equipment:[],idols:[],altars:[],bases:[]});
  assert.equal(state.saves.length,1);assert.equal(templates.length,2);
});

test('deleting a scheme preserves all other schemes and pending template choices',()=>{
  const {templates,state}=setup();W.applyTemplates(state,templates,'first');const second=W.applyTemplates(state,templates,'second'),before=copy(second),draft=copy(state.selection);
  W.removeSave(state,'first');assert.equal(state.saves.length,1);assert.deepEqual(second,before);assert.deepEqual(state.selection,draft);
  W.removeSave(state,'second');assert.equal(state.active_save_id,null);assert.deepEqual(state.saves,[]);assert.deepEqual(state.selection,draft);
});

test('malformed backups and duplicate BD identities are rejected before loading',()=>{
  const {examples,templates,state}=setup();W.applyTemplates(state,templates,'first');
  for(const change of [s=>s.saves.push(copy(s.saves[0])),s=>s.active_save_id='missing',s=>s.saves[0].config.builds.push(copy(s.saves[0].config.builds[0])),s=>s.saves[0].config.main_id='missing']){
    const broken=copy(state);change(broken);assert.throws(()=>W.restore(examples,broken));
  }
  assert.deepEqual(W.restore(examples,state),state);
});

test('equipment selection retains priorities and appends new targets instead of sorting by ID',()=>{
  const chosen=new Set(['34','502','715']);
  assert.deepEqual(W.selectionValues(chosen,true),[34,502,715]);
  chosen.add('2');chosen.add('36');chosen.delete('502');
  assert.deepEqual(W.selectionValues(chosen,true),[34,715,2,36]);
  assert.deepEqual(W.selectionValues(chosen),[2,34,36,715]);
  assert.deepEqual([...chosen],['34','715','2','36']);
});

test('common switches survive saved schemes, reload and backup without changing templates',()=>{
  const {examples,templates,state}=setup(),saved=W.applyTemplates(state,templates,'common-switches');
  const before=copy(templates);
  saved.config.common.exalted_experimentals_enabled=true;
  saved.config.common.common_uniques_enabled=false;
  saved.config.common.common_sets_enabled=true;
  const restored=W.restore(examples,JSON.parse(JSON.stringify(state)));
  const second=W.applyTemplates(restored,templates,'inherited-switches');
  assert.deepEqual(second.config.common,saved.config.common);
  W.mergeSaves(restored,state,()=> 'imported-switches');
  assert.deepEqual(W.activeSave(restored).config.common,saved.config.common);
  assert.deepEqual(templates,before);
});

test('adjusted equipment priorities survive reload and backup imports without altering template or targets',()=>{
  const {examples,templates,state}=setup(),saved=W.applyTemplates(state,templates,'priorities');
  const group=saved.config.builds[0].profiles.endgame.equipment.find(g=>g.type==='ONE_HANDED_AXE');
  const before=copy(saved.config),templateBefore=copy(templates),targetSet=[...group.affixes].sort((a,b)=>a-b);
  assert.equal(W.moveAffix(group,0,-1),false);assert.equal(W.moveAffix(group,group.affixes.length-1,1),false);
  assert.equal(W.moveAffix(group,2,-1),true);assert.deepEqual(group.affixes,[943,718,2,724]);
  const restored=W.restore(examples,JSON.parse(JSON.stringify(state)));
  W.mergeSaves(restored,state,()=> 'imported-priorities');
  const imported=W.activeSave(restored).config.builds[0].profiles.endgame.equipment.find(g=>g.type==='ONE_HANDED_AXE');
  assert.deepEqual(imported.affixes,[943,718,2,724]);assert.deepEqual([...imported.affixes].sort((a,b)=>a-b),targetSet);
  assert.deepEqual(saved.config.builds[0].profiles.leveling,before.builds[0].profiles.leveling);
  assert.equal(saved.config.main_id,before.main_id);assert.deepEqual(templates,templateBefore);
});

test('drag placement retains every target, stage and saved scheme after reload',()=>{
  const {examples,templates,state}=setup(),saved=W.applyTemplates(state,templates,'drag');
  const group=saved.config.builds[0].profiles.endgame.equipment[0],before=copy(saved.config);
  assert.equal(W.placeAffix(group,0,2),true);assert.deepEqual(group.affixes,[502,715,34]);
  assert.equal(W.placeAffix(group,2,0),true);assert.deepEqual(group.affixes,[34,502,715]);
  assert.equal(W.placeAffix(group,0,3),false);assert.equal(W.placeAffix(group,0,0),false);
  W.placeAffix(group,1,0);
  assert.deepEqual(W.restore(examples,JSON.parse(JSON.stringify(state))).saves[0].config.builds[0].profiles.endgame.equipment[0].affixes,[502,34,715]);
  assert.deepEqual(saved.config.builds[0].profiles.leveling,before.builds[0].profiles.leveling);
  assert.deepEqual(saved.config.builds[0].profiles.endgame.equipment.slice(1),before.builds[0].profiles.endgame.equipment.slice(1));
  assert.deepEqual(templates[0].profiles.endgame.equipment[0].affixes,[34,502,715]);
});

test('set completion is derived for display and never replaces explicitly selected items',()=>{
  const catalog={item_sets:require('../sources/item-sets.json').sets},selected=[79,171],before=copy(selected);
  assert.deepEqual(W.expandUniqueSets(selected,catalog),[79,171,77,78,170]);
  assert.deepEqual(selected,before);assert.deepEqual(W.expandUniqueSets([77,79],catalog),[77,79,78]);
  assert.deepEqual(W.expandUniqueSets([],catalog),[]);assert.deepEqual(W.expandUniqueSets([6],catalog),[6]);
  for(const group of Object.values(catalog.item_sets))for(const uid of group.members){
    assert.deepEqual(W.expandUniqueSets([uid],catalog).sort((a,b)=>a-b),group.members);
  }
});
