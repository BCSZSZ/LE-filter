const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');

function bridge(fetchResult){
  const requests=[],workers=[];
  class Worker {
    constructor(url){this.url=url.href;this.messages=[];workers.push(this);}
    postMessage(message){this.messages.push(message);}
    reply(data){this.onmessage({data});}
  }
  const context={URL,Worker,performance:{now:()=>123},document:{currentScript:{src:'https://example.test/browser.js?v=revision'},documentElement:{dataset:{}}},
    fetch:async url=>{requests.push(url.href);return fetchResult();}};
  vm.runInNewContext(fs.readFileSync('tool/web/browser.js','utf8'),context);
  return {api:context.LEFilterAPI,worker:workers[0],requests,dataset:context.document.documentElement.dataset};
}
const snapshot={catalog:{version:'frozen'},config:{builds:[]}};

test('editor bootstrap resolves while the Python worker is still loading',async()=>{
  const {api,worker,requests,dataset}=bridge(()=>({ok:true,json:async()=>snapshot}));
  const result=await Promise.race([api('/api/bootstrap'),new Promise((_,reject)=>setTimeout(()=>reject(Error('bootstrap blocked by worker')),100))]);
  assert.equal(result,snapshot);assert.equal(api.fastBootstrap,true);
  assert.deepEqual(requests,['https://example.test/bootstrap.json?v=revision']);
  assert.equal(worker.messages.length,0);assert.equal(worker.url,'https://example.test/worker.mjs?v=revision');
  assert.equal(await api('/api/bootstrap'),snapshot);assert.equal(requests.length,1);
  const generation=api('/api/generate',{config:{main_id:'bd'}});
  const request=worker.messages[0];assert.equal(request.path,'/api/generate');
  worker.reply({ready:true});assert.equal(dataset.engineReadyMs,'123.0');
  worker.reply({id:request.id,result:{sha256:'same-python-engine'}});
  assert.equal((await generation).sha256,'same-python-engine');
});

test('a missing static snapshot falls back to the original Python bootstrap',async()=>{
  const {api,worker}=bridge(()=>({ok:false}));
  const result=api('/api/bootstrap');await new Promise(resolve=>setImmediate(resolve));
  assert.equal(worker.messages.length,1);const request=worker.messages[0];
  assert.equal(request.path,'/api/bootstrap');worker.reply({id:request.id,result:snapshot});
  assert.equal(await result,snapshot);assert.equal(api.fastBootstrap,false);
});

test('worker startup failures reject pending and future operations without losing the editor',async()=>{
  const {api,worker,dataset}=bridge(()=>({ok:true,json:async()=>snapshot}));
  await api('/api/bootstrap');
  const pending=api('/api/generate',{});
  worker.reply({failure:'runtime unavailable'});
  await assert.rejects(pending,/runtime unavailable/);
  await assert.rejects(api('/api/generate',{}),/runtime unavailable/);
  assert.equal(dataset.engineState,'failed');assert.equal(await api('/api/bootstrap'),snapshot);
});
