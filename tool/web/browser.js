// Only the static publication loads this bridge; the local app keeps its API.
{
  const bridgeURL=new URL(document.currentScript.src),workerURL=new URL('worker.mjs',bridgeURL),bootstrapURL=new URL('bootstrap.json',bridgeURL);
  workerURL.search=bootstrapURL.search=bridgeURL.search;
  const worker = new Worker(workerURL, {type:'module'});
  const pending = new Map();
  let nextId = 0,failure;
  document.documentElement.dataset.engineState='loading';
  const fail=message=>{
    failure=Error(message || '规则引擎加载失败，请刷新页面。');
    document.documentElement.dataset.engineState='failed';
    for(const item of pending.values())item.reject(failure);
    pending.clear();
  };
  worker.onmessage = ({data}) => {
    if(data.ready){document.documentElement.dataset.engineState='ready';document.documentElement.dataset.engineReadyMs=performance.now().toFixed(1);return;}
    if(data.failure){fail(data.failure);return;}
    const item = pending.get(data.id);
    if(!item)return;
    pending.delete(data.id);
    if(data.error)item.reject(Error(data.error));else item.resolve(data.result);
  };
  worker.onerror = error => fail(error.message);
  const request = (path,payload) => new Promise((resolve,reject) => {
    if(failure){reject(failure);return;}
    const id = ++nextId;
    pending.set(id,{resolve,reject});
    worker.postMessage({id,path,payload});
  });
  const api=(path,payload)=>path==='/api/bootstrap'?bootstrap:request(path,payload);
  api.fastBootstrap=false;
  const bootstrap=fetch(bootstrapURL).then(async response=>{
    if(!response.ok)throw Error('编辑数据加载失败。');
    const result=await response.json();
    if(!result.catalog||!result.config)throw Error('编辑数据格式不正确。');
    api.fastBootstrap=true;return result;
  }).catch(()=>request('/api/bootstrap'));
  globalThis.LEFilterAPI=api;
}
