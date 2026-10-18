import {loadPyodide} from '../.site/pyodide/pyodide.mjs';
import {readFileSync, writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';

const pyodide = await loadPyodide({indexURL:fileURLToPath(new URL('../.site/pyodide/', import.meta.url))});
pyodide.unpackArchive(new Uint8Array(readFileSync(new URL('../.site/runtime.zip', import.meta.url))), 'zip', {extractDir:'/app'});
pyodide.runPython("import sys\nsys.path.insert(0, '/app/tool')\nfrom browser_runtime import dispatch_json");
const native = JSON.parse(readFileSync(new URL('../.cache/fixed-common-native.json', import.meta.url), 'utf8'));
const cases = [];
for (const [name, value] of Object.entries(native)) {
  pyodide.globals.set('request_json', JSON.stringify(value.request));
  const result = JSON.parse(pyodide.runPython('dispatch_json(request_json)'));
  assert.deepStrictEqual(result, value.output, name);
  cases.push({name, count:result.count, sha256:result.sha256, completeOutputEqual:true});
}
writeFileSync(new URL('../analysis/fixed-common-rules-wasm-validation.json', import.meta.url), JSON.stringify({
  status:'passed', date:'2026-10-19', runtime:'Pyodide 314.0.7 / Node.js',
  browserDownloadTested:false, gameExecutionTested:false, cases}, null, 2)+'\n');
console.log(`PASS: ${cases.length} complete fixed-common WASM/native outputs match`);
