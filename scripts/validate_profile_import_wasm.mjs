import {loadPyodide} from '../.site/pyodide/pyodide.mjs';
import {readFileSync,writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';

const pyodide=await loadPyodide({indexURL:fileURLToPath(new URL('../.site/pyodide/',import.meta.url))});
pyodide.unpackArchive(new Uint8Array(readFileSync(new URL('../.site/runtime.zip',import.meta.url))),'zip',{extractDir:'/app'});
pyodide.runPython("import sys\nsys.path.insert(0, '/app/tool')\nfrom browser_runtime import dispatch_json");
const native=JSON.parse(readFileSync(new URL('../.cache/profile-import/native.json',import.meta.url),'utf8'));
const cases=[];
for(const [name,value] of Object.entries(native)){
  pyodide.globals.set('request_json',JSON.stringify(value.request));
  const actual=JSON.parse(pyodide.runPython('dispatch_json(request_json)'));
  assert.deepStrictEqual(actual,value.output,name);
  cases.push({name,completeOutputEqual:true,...(actual.count?{count:actual.count}:{}),...(actual.error?{error:actual.error}:{})});
}
writeFileSync(new URL('../analysis/profile-import-wasm-validation.json',import.meta.url),JSON.stringify({date:'2026-10-18',status:'passed',runtime:'Pyodide 314.0.7 / Node.js',cases,browserDownloadTested:false,gameClientTested:false},null,2)+'\n');
console.log(`PASS: ${cases.length} complete packaged WASM/native outputs equal`);
