import {loadPyodide} from './pyodide/pyodide.mjs';

const runtimeURL=new URL('runtime.zip',import.meta.url);
runtimeURL.search=new URL(import.meta.url).search;
const archive=fetch(runtimeURL).then(async response=>{
  if(!response.ok)throw Error('规则和示例数据加载失败。');
  return response.arrayBuffer();
});
const ready = (async () => {
  const [pyodide,bytes]=await Promise.all([
    loadPyodide({indexURL:new URL('./pyodide/',import.meta.url).href}),archive
  ]);
  pyodide.unpackArchive(bytes,'zip',{extractDir:'/app'});
  pyodide.runPython("import sys\nsys.path.insert(0, '/app/tool')\nfrom browser_runtime import dispatch_json");
  return pyodide;
})();
ready.then(()=>self.postMessage({ready:true}),error=>self.postMessage({failure:error.message}));

self.onmessage = async ({data}) => {
  try {
    const pyodide = await ready;
    pyodide.globals.set('request_json',JSON.stringify({path:data.path,payload:data.payload}));
    const result = JSON.parse(pyodide.runPython('dispatch_json(request_json)'));
    self.postMessage(result.error?{id:data.id,error:result.error}:{id:data.id,result});
  } catch(error) {
    self.postMessage({id:data.id,error:error.message});
  }
};
