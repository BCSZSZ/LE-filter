import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createRelay,normalizeLinks,UPSTREAM,WORKBENCH_ORIGIN} from '../services/letools-relay/relay.mjs';
import client from './web/profile-import.js';
import workbench from './web/workbench.js';

const fixture=JSON.parse(readFileSync(new URL('../sources/builds/maxroll-character-api-2026-10-18.json',import.meta.url))),rows=fixture.responses,urls=rows.map(x=>x.url);
const request=(payload,origin=WORKBENCH_ORIGIN)=>new Request('https://relay.example/api/profiles/read',{method:'POST',headers:{'Content-Type':'application/json',Origin:origin},body:JSON.stringify(payload)});
function upstream({fail,change,now}={}){
  const calls=[];
  const handle=createRelay({now,fetcher:async(url,options)=>{
    calls.push({url,options});assert(url.startsWith(UPSTREAM));assert.equal(options.method,'GET');assert.equal(options.redirect,'manual');
    const row=rows.find(x=>url.endsWith('/'+x.response.characterName));
    if(fail&&row===rows[1])return Response.json({error:'not_found'});
    if(!row)return new Response('Missing',{status:404});
    const raw=structuredClone(row.response);if(change)change(raw);
    return Response.json(raw);
  }});
  return {handle,calls};
}

test('browser and relay normalize the same public links and reject other destinations',()=>{
  const alias=urls[0].replace('www.','').replace('/profile/','/profile/zh/');
  for(const normalize of [normalizeLinks,client.normalizeLinks]){
    assert.deepEqual(normalize(alias+'\n'+urls[0]),[urls[0]]);
    for(const input of ['',{},['https://evil.example/profile/a/character/b'],[urls[0]+'?x=1'],[urls[0]+'#x'],[urls[0].replace('MAONG','%2f')],[urls[0].replace('MAONG','%ff')],[urls[0].replace('MAONG','%7f')],[urls[0].replace('MAONG','a'.repeat(129))],Array.from({length:13},(_,i)=>urls[0]+i)])assert.throws(()=>normalize(input));
    assert.deepEqual(normalize('https://lastepochtools.com/profile/测试/character/角色'),['https://www.lastepochtools.com/profile/%E6%B5%8B%E8%AF%95/character/%E8%A7%92%E8%89%B2']);
  }
});
test('native API fixture passes relay and browser gates, retaining all 76 items',async()=>{
  const {handle,calls}=upstream();
  const result=await client.readProfiles([...urls,urls[0]],{name:'个人并集',fetcher:async(_,options)=>handle(request(JSON.parse(options.body)))});
  assert.equal(result.profiles.length,4);assert.equal(calls.length,4);assert.equal(result.name,'个人并集');
  assert.deepEqual(result.profiles.map(p=>p.url),urls);
  assert.equal(result.profiles.reduce((sum,p)=>sum+p.save.savedItems.length,0),76);
  assert(calls.every(c=>c.options.headers.Accept==='application/json'));
  assert(result.profiles.every(p=>p.provider==='Maxroll'&&p.api_url.startsWith(UPSTREAM)));
  assert(!JSON.stringify(result).includes('skillTrees'));
});
test('preflight and responses permit the workbench, with no wildcard or credentials',async()=>{
  const {handle,calls}=upstream();
  const preflight=await handle(new Request('https://relay.example/api/profiles/read',{method:'OPTIONS',headers:{Origin:WORKBENCH_ORIGIN}}));
  assert.equal(preflight.status,204);assert.equal(preflight.headers.get('Access-Control-Allow-Origin'),WORKBENCH_ORIGIN);
  assert.equal(preflight.headers.get('Access-Control-Allow-Credentials'),null);
  const denied=await handle(request({links:urls},'https://evil.example'));
  assert.equal(denied.status,403);assert.equal(denied.headers.get('Access-Control-Allow-Origin'),null);assert.equal(calls.length,0);
});
test('invalid input and oversized bodies never reach upstream',async()=>{
  const {handle,calls}=upstream();
  for(const body of [{links:['http://127.0.0.1/']},{links:[]},{links:urls,name:{}},{links:urls,name:'a'.repeat(101)}])assert.equal((await handle(request(body))).status,400);
  assert.equal((await handle(request({links:urls,padding:'a'.repeat(17000)}))).status,413);
  assert.equal(calls.length,0);
});
test('one failed or mismatched character returns an error without a partial bundle',async()=>{
  for(const options of [{fail:true},{change:raw=>raw.characterName='another-character'}]){
    const {handle}=upstream(options),response=await handle(request({links:urls})),body=await response.json();
    assert.equal(response.status,502);assert(body.error);assert.equal(body.profiles,undefined);
  }
});
test('redirect responses are rejected without following them',async()=>{
  let calls=0;
  const handle=createRelay({fetcher:async(url,options)=>{
    calls++;assert(url.startsWith(UPSTREAM));assert.equal(options.redirect,'manual');
    return new Response(null,{status:302,headers:{Location:'https://evil.example/'}});
  }});
  const response=await handle(request({links:[urls[0]]}));
  assert.equal(response.status,502);assert.equal(calls,1);assert.match((await response.json()).error,/302/);
});
test('duplicate requests share successful reads for five minutes and failures can retry',async()=>{
  let time=100;
  const {handle,calls}=upstream({now:()=>time});
  const responses=await Promise.all([handle(request({links:[urls[0],urls[0]]})),handle(request({links:[urls[0]]}))]);
  assert(responses.every(r=>r.status===200));assert.equal(calls.length,1);
  await handle(request({links:[urls[0]]}));assert.equal(calls.length,1);
  time+=300001;await handle(request({links:[urls[0]]}));assert.equal(calls.length,2);
  const failure=upstream({fail:true});
  await failure.handle(request({links:[urls[1]]}));await failure.handle(request({links:[urls[1]]}));assert.equal(failure.calls.length,2);
});
test('frontend rejects wrong counts/order and displays upstream errors',async()=>{
  for(const body of [{format:'bad'},{format:'letools-profile-bundle',version:1,profiles:[]},{format:'letools-profile-bundle',version:1,profiles:[{url:urls[1]}]}]){
    await assert.rejects(()=>client.readProfiles([urls[0]],{fetcher:async()=>Response.json(body)}),/不一致/);
  }
  await assert.rejects(()=>client.readProfiles([urls[0]],{fetcher:async()=>Response.json({error:'角色未公开'},{status:502})}),/角色未公开/);
  await assert.rejects(()=>client.readProfiles([urls[0]],{fetcher:async()=>{throw Error('network');}}),/暂不可用/);
});
test('personal imports preserve template bytes, existing saves and independent stages',()=>{
  const end={uniques:[256],equipment:[],altars:[],idols:[],bases:[]};
  const examples={version:1,main_id:'template',extra_t7:true,builds:[{id:'template',name:'模版',enabled:true,profiles:{endgame:end,leveling:{affixes:[88],bases:[]}}}]};
  const templates=workbench.library(examples),before=JSON.stringify(templates),state=workbench.restore(examples);
  const old=workbench.applyTemplates(state,templates,'old'),snapshot=JSON.stringify(old);
  const imported={name:'角色并集',profile:end,source:{profiles:[{url:urls[0]}]}};
  const saved=workbench.importProfiles(state,imported,'personal','new');
  assert.equal(state.saves.length,2);assert.equal(JSON.stringify(old),snapshot);assert.equal(saved.config.main_id,'personal');
  assert.deepEqual(saved.config.builds[0].profiles.leveling,{affixes:[],bases:[]});
  assert.equal(saved.config.builds[0].template_id,undefined);assert.equal(JSON.stringify(templates),before);
  const restored=workbench.restore(examples,JSON.parse(JSON.stringify(state)));
  workbench.importProfiles(restored,imported,'personal2','unused','current-save');
  assert.equal(workbench.activeSave(restored).config.main_id,'personal');assert.equal(restored.saves.length,2);
  assert.equal(workbench.activeSave(restored).config.builds.length,2);
});
