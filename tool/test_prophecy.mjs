import {test} from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {selectProfile,probabilities,chartExtent} from "./probability_web/model.mjs";

const data=JSON.parse(fs.readFileSync(new URL("../analysis/prophecy-probabilities.json",import.meta.url),"utf8"));
test("every legitimate item/career combination keeps its own exact pool",()=>{
  for(const p of data.profiles) assert.equal(selectProfile(data,p.typeID,p.classRequirement).id,p.id);
  const sentinel=selectProfile(data,1,4),mage=selectProfile(data,1,2);
  assert.notEqual(probabilities(sentinel,12)[0].distribution[2],probabilities(mage,12)[0].distribution[2]);
  assert.equal(selectProfile(data,21,8).id,"ring-none");
});
test("unlocked prophecy and lenses follow the actual faction ranks",()=>{
  const p=selectProfile(data,21,0);
  assert.ok(probabilities(p,3).every(l=>l.distribution===null));
  assert.deepEqual(probabilities(p,4).map(l=>Boolean(l.distribution)),[true,false,true,true]);
  assert.deepEqual(probabilities(p,8),probabilities(p,4));
  assert.deepEqual(probabilities(p,12),probabilities(p,9));
  assert.ok(probabilities(p,12)[0].distribution[2]>probabilities(p,4)[0].distribution[2]);
});
test("corruption changes only chart bounds and the selected marker",()=>{
  assert.deepEqual(chartExtent(""),{selected:0,maximum:1000});
  assert.deepEqual(chartExtent(350),{selected:350,maximum:1000});
  assert.deepEqual(chartExtent(2350),{selected:2350,maximum:3000});
  assert.equal(data.corruptionAffectsProbability,false);
  assert.equal(data.areaLevelAffectsProbability,false);
  assert.equal(data.itemLevel,100);
});
