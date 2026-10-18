const test=require('node:test'),assert=require('node:assert/strict');
const R=require('./web/profile-reader.js'),W=require('./web/workbench.js');
const url='https://www.lastepochtools.com/profile/a/character/one',url2='https://www.lastepochtools.com/profile/b/character/two';
const data={equipment:{head:{id:'UAzBMoVgNiA',affixes:[{id:'AGwRhQ',tier:7,r:[0.5]}],ir:[1]}},idols:[]};
function env(fail=false){
  const calls=[],elements=[];
  const element=()=>({style:{},append(...nodes){elements.push(...nodes);},remove(){}});
  return {calls,elements,location:{origin:'https://www.lastepochtools.com',href:url},AbortSignal,URL,Blob,
    document:{getElementById:()=>null,createElement:element,body:element()},
    _profileDataPromise:Promise.resolve({buildInfo:{data,data_version:'version152'},charInfo:{accountName:'a',characterName:'one'}}),
    fetch:async (path,options)=>{
      calls.push({path,options});
      if(fail)return {ok:false,status:403};
      if(path===url2)return {ok:true,text:async()=>`<script>let ab12_token = 'abcdef0123456789abcdef0123456789';</script><script>fetch('/api/internal/profile_data/' + ab12_token)</script>`};
      assert.equal(path,'/api/internal/profile_data/abcdef0123456789abcdef0123456789');
      return {ok:true,json:async()=>({buildInfo:{data,data_version:'version152'},charInfo:{accountName:'b',characterName:'two'}})};
    }};
}
test('links are canonical, bounded and reject arbitrary destinations',()=>{
  assert.deepEqual(R.normalizeLinks(url+'\n'+url),[url]);
  assert.deepEqual(R.normalizeLinks('https://lastepochtools.com/profile/zh/a/character/one'),[url]);
  for(const bad of ['https://evil.example/profile/a/character/one',url+'?x=1',url+'/snapshot/aberroth','javascript:alert(1)',url.replace('/one','/%2f')])assert.throws(()=>R.normalizeLinks(bad));
});
test('reader uses current public page data and fetches remaining profiles serially on the same origin',async()=>{
  const context=env(),result=await R.runReader({links:[url,url2],returnURL:'https://bcszsz.github.io/LE-filter/',name:'玩家并集'},context);
  assert.equal(result.profiles.length,2);assert.equal(context.calls.length,2);
  assert(context.calls.every(c=>c.options.credentials==='same-origin'));
  assert.deepEqual(result.profiles[0].data.equipment.head,{id:'UAzBMoVgNiA',affixes:[{id:'AGwRhQ',tier:7}]});
  const back=context.elements.find(e=>e.textContent==='返回工作台，预览并集');
  assert.deepEqual(R.bundleFromHash(new URL(back.href).hash),JSON.parse(JSON.stringify(result)));
});
test('a failed URL leaves no partial callback or downloadable union',async()=>{
  const context=env(true);
  await assert.rejects(()=>R.runReader({links:[url,url2],returnURL:'https://bcszsz.github.io/LE-filter/'},context),/403/);
  assert(!context.elements.some(e=>e.download||e.target));
  assert(context.elements.some(e=>e.textContent?.includes('本次未导入任何目标')));
});
test('generated bookmarklet is standalone executable code and quotes names safely',()=>{
  const bookmark=R.makeBookmarklet([url],'https://bcszsz.github.io/LE-filter/','"<script>');
  assert(bookmark.startsWith('javascript:'));
  assert(!bookmark.includes('\n'));
  assert.doesNotThrow(()=>new Function(decodeURIComponent(bookmark.slice('javascript:'.length))));
  assert.equal(R.bundleFromHash('#other'),null);
});
test('serialized bookmarklet runs with only browser globals and preserves its callback',async()=>{
  const context=env(),vm=require('node:vm');
  const bookmark=R.makeBookmarklet([url,url2],'https://bcszsz.github.io/LE-filter/','完整书签');
  vm.runInNewContext(decodeURIComponent(bookmark.slice('javascript:'.length)),context);
  await new Promise(setImmediate);
  const back=context.elements.find(e=>e.textContent==='返回工作台，预览并集');
  assert(back);assert.equal(R.bundleFromHash(new URL(back.href).hash).profiles.length,2);
});
test('profile union creates a personal scheme and retains templates, old schemes and the other stage',()=>{
  const end={uniques:[256],equipment:[],altars:[],idols:[],bases:[]},examples={version:1,main_id:'template',extra_t7:true,builds:[{id:'template',name:'模版',enabled:true,profiles:{endgame:end,leveling:{affixes:[88],bases:[]}}}]};
  const templates=W.library(examples),before=JSON.stringify(templates),state=W.restore(examples);
  const old=W.applyTemplates(state,templates,'old'),snapshot=JSON.stringify(old);
  const imported={name:'角色并集',profile:end,source:{profiles:[{url}]}};
  const saved=W.importProfiles(state,imported,'personal','new');
  assert.equal(state.saves.length,2);assert.equal(JSON.stringify(old),snapshot);assert.equal(saved.config.main_id,'personal');
  assert.deepEqual(saved.config.builds[0].profiles.leveling,{affixes:[],bases:[]});
  assert.equal(saved.config.builds[0].template_id,undefined);assert.equal(JSON.stringify(templates),before);
  const restored=W.restore(examples,JSON.parse(JSON.stringify(state)));
  W.importProfiles(restored,imported,'personal2','unused','current-save');
  assert.equal(W.activeSave(restored).config.main_id,'personal');assert.equal(restored.saves.length,2);
  assert.equal(W.activeSave(restored).config.builds.length,2);
});
