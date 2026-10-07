// Only the static publication loads this bridge; the local app keeps its API.
{
  const worker = new Worker(new URL('worker.mjs', document.currentScript.src), {type:'module'});
  const pending = new Map();
  let nextId = 0;
  worker.onmessage = ({data}) => {
    const item = pending.get(data.id);
    if(!item)return;
    pending.delete(data.id);
    if(data.error)item.reject(Error(data.error));else item.resolve(data.result);
  };
  worker.onerror = error => {
    for(const item of pending.values())item.reject(Error(error.message || '规则引擎加载失败，请刷新页面。'));
    pending.clear();
  };
  globalThis.LEFilterAPI = (path,payload) => new Promise((resolve,reject) => {
    const id = ++nextId;
    pending.set(id,{resolve,reject});
    worker.postMessage({id,path,payload});
  });
}
