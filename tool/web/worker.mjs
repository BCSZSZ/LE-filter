import {loadPyodide} from './pyodide/pyodide.mjs';

const ready = (async () => {
  const pyodide = await loadPyodide({indexURL:new URL('./pyodide/',import.meta.url).href});
  const response = await fetch(new URL('runtime.zip',import.meta.url));
  if(!response.ok)throw Error('规则和示例数据加载失败。');
  pyodide.unpackArchive(await response.arrayBuffer(),'zip',{extractDir:'/app'});
  pyodide.runPython("import sys\nsys.path.insert(0, '/app/tool')\nfrom browser_runtime import dispatch_json");
  return pyodide;
})();

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
