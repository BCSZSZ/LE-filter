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
test('editing, renaming and deleting a saved copy cannot change the official library',()=>{
  const examples=fixtures(),original=copy(examples),templates=W.library(examples),config=W.restore(examples);
  const b=config.builds[0];b.name='我的魔力巫妖';b.profiles.endgame.idols=[];config.builds=[];
  assert.deepEqual(templates,original.builds);assert.deepEqual(examples,original);
  assert.ok(Object.isFrozen(templates[0].profiles.endgame.idols));
  assert.equal(W.useTemplate(config,templates,templates[0].id).build.profiles.endgame.idols.length,5);
});
test('migration and reload preserve old edits, deselected builds, both stages and common choices',()=>{
  const examples=fixtures(),old=copy(examples);old.builds[0].name='旧保存';old.builds[0].profiles.endgame.idols=[];
  old.builds[1].profiles.leveling.affixes=[406];old.common.unique_idols=[];
  const before=copy(old),restored=W.restore(examples,old);
  assert.deepEqual(restored.builds[0].profiles,before.builds[0].profiles);
  assert.equal(restored.builds[0].name,'旧保存');assert.equal(restored.builds[1].enabled,false);
  assert.deepEqual(restored.builds[1].profiles.leveling,before.builds[1].profiles.leveling);
  assert.deepEqual(restored.common,before.common);assert.deepEqual(old,before);
  assert.deepEqual(W.restore(examples,JSON.parse(JSON.stringify(restored))),restored);
});
test('loading a template again resumes saved edits; explicit reset restores only that copy',()=>{
  const examples=fixtures(),templates=W.library(examples),config=W.restore(examples);
  const first=W.useTemplate(config,templates,templates[0].id).build;first.name='我的名字';first.profiles.endgame.idols=[];
  first.enabled=false;
  const again=W.useTemplate(config,templates,templates[0].id);assert.ok(again.reused);assert.equal(config.builds.length,1);
  assert.deepEqual(again.build.profiles.endgame.idols,[]);
  const other=W.useTemplate(config,templates,templates[1].id).build;other.profiles.leveling.affixes=[406];
  const otherBefore=copy(other),main=config.main_id,common=copy(config.common);
  const reset=W.resetBuild(config,templates,first.id);
  assert.deepEqual(reset.profiles,templates[0].profiles);assert.equal(reset.name,'我的名字');assert.equal(reset.enabled,true);
  assert.deepEqual(other,otherBefore);assert.equal(config.main_id,main);assert.deepEqual(config.common,common);
});
test('same-id requirements import updates only that saved stage and never the template',()=>{
  const examples=fixtures(),templates=W.library(examples),config=W.restore(examples),original=copy(templates);
  const b=config.builds[0],leveling=copy(b.profiles.leveling),main=config.main_id;
  const data={id:b.id,name:'玩家补充',stage:'endgame',profile:{uniques:[],equipment:[],idols:[],altars:[],bases:[]},source:{name:'玩家JSON'}};
  W.importRequirement(config,templates,data);
  assert.equal(b.enabled,true);assert.equal(config.main_id,main);assert.deepEqual(b.profiles.leveling,leveling);
  assert.deepEqual(b.profiles.endgame,data.profile);assert.deepEqual(templates,original);
  b.profiles.endgame.uniques.push(211);assert.deepEqual(data.profile.uniques,[]);
});
test('new imported requirements stay unselected; defaults copy only selected examples',()=>{
  const examples=fixtures(),templates=W.library(examples),config=W.restore(examples);
  assert.equal(config.builds.length,1);
  const b=W.importRequirement(config,templates,{id:'my-build',name:'自定义',stage:'leveling',profile:{affixes:[406],bases:[]},source:{}});
  assert.equal(b.enabled,false);assert.deepEqual(b.profiles.endgame,{uniques:[],equipment:[],idols:[],altars:[],bases:[]});
  assert.equal(config.main_id,examples.main_id);assert.equal(templates.length,2);
});
