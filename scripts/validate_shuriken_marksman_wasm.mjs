import {loadPyodide} from '../.site/pyodide/pyodide.mjs';
import {readFileSync, writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';

try {
  const pyodide = await loadPyodide({indexURL: fileURLToPath(new URL('../.site/pyodide/', import.meta.url))});
  pyodide.unpackArchive(new Uint8Array(readFileSync(new URL('../.site/runtime.zip', import.meta.url))), 'zip', {extractDir:'/app'});
  pyodide.runPython("import sys\nsys.path.insert(0, '/app/tool')\nfrom browser_runtime import dispatch_json");
  const boot = JSON.parse(pyodide.runPython('dispatch_json(\'{"path":"/api/bootstrap"}\')'));
  assert.equal(boot.config.builds.length, 6);
  const shuriken = boot.config.builds.find(b => b.id === 'heartseeker-shuriken-marksman');
  assert.equal(shuriken.name, '追心手里剑');
  assert.equal(shuriken.enabled, false);
  const native = JSON.parse(readFileSync(new URL('../.cache/shuriken-marksman-native.json', import.meta.url), 'utf8'));
  const cases = [];
  for (const [name, value] of Object.entries(native)) {
    pyodide.globals.set('request_json', JSON.stringify(value.request));
    const result = JSON.parse(pyodide.runPython('dispatch_json(request_json)'));
    assert.deepStrictEqual(result, value.output, name);
    cases.push({name, count:result.count, sha256:result.sha256, completeOutputEqual:true});
  }
  const result = {status:'passed', date:'2026-10-18', runtime:'Pyodide 314.0.7 / Node.js',
    scope:'Six independent templates; packaged complete XML, metadata and warnings match native Python.',
    browserDownloadTested:false, gameExecutionTested:false, cases};
  writeFileSync(new URL('../analysis/shuriken-marksman-wasm-validation.json', import.meta.url), JSON.stringify(result,null,2)+'\n');
  console.log(`PASS: six templates, ${cases.length} packaged WASM/native complete outputs match`);
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
