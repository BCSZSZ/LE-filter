import {test} from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {selectProfile,probabilities,chartExtent,naturalProbability,naturalRarityWeights,sourceRows} from "./probability_web/model.mjs";

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
test("corruption affects ordinary drops and keeps prophecy probabilities fixed",()=>{
  assert.deepEqual(chartExtent(""),{selected:0,maximum:1000});
  assert.deepEqual(chartExtent(350),{selected:350,maximum:1000});
  assert.deepEqual(chartExtent(2350),{selected:2350,maximum:3000});
  assert.deepEqual(data.corruptionAffectsProbability,{prophecy:false,natural:true});
  assert.equal(data.areaLevelAffectsProbability,false);
  assert.equal(data.itemLevel,100);
  const ring=selectProfile(data,21,0);
  assert.deepEqual(sourceRows(data,ring,12,"prophecy",0,3),sourceRows(data,ring,12,"prophecy",1000,1));
  assert.notDeepEqual(naturalProbability(data,ring,12,0,3),naturalProbability(data,ring,12,1000,3));
});

test("ordinary probabilities condition on final exalted equipment at all ranks",()=>{
  for(const profile of data.profiles) for(const rank of [0,4,9,11,12]) for(const corruption of [0,100,300,1000,100000]) {
    const distribution=naturalProbability(data,profile,rank,corruption,3);
    assert.ok(distribution.every(p=>p>=0 && p<=1));
    assert.ok(Math.abs(distribution.reduce((a,b)=>a+b,0)-1)<1e-10);
    assert.equal(sourceRows(data,profile,rank,"natural",corruption,3).length,1);
  }
  const ring=selectProfile(data,21,0);
  assert.ok(naturalProbability(data,ring,0,0,3)[1]>0);
  assert.equal(probabilities(ring,0)[0].distribution,null);
  const empty={naturalComponents:{"0":Array.from({length:5},()=>({p_T7_count:[1,0,0,0,0],p_exalted:0}))},typeID:21};
  assert.equal(naturalProbability(data,empty,0,0,3),null);
});

test("player class corrects type selection independently of equipment career",()=>{
  const ring=selectProfile(data,21,0);
  const mage=naturalRarityWeights(data,0,1,21),rogue=naturalRarityWeights(data,0,4,21);
  assert.ok(mage[2]<rogue[2]);
  assert.notDeepEqual(naturalProbability(data,ring,12,0,1),naturalProbability(data,ring,12,0,4));
  // C=0 has one unmodified draw. Check Bayes conditioning from the raw intervals.
  const raw=[.13-(.00156+.0073),.22,.49,.09,.07];
  const coefficient=data.naturalRarity.typeSelection.players.find(p=>p.id===3).raw2EquipmentFactorByType[21];
  raw[2]*=coefficient;
  const total=raw.reduce((a,b)=>a+b,0),actual=naturalRarityWeights(data,0,3,21);
  raw.forEach((value,i)=>assert.ok(Math.abs(value/total-actual[i])<1e-14));
  for(const p of data.naturalRarity.typeSelection.players) for(const type of data.equipmentTypes) {
    const weights=naturalRarityWeights(data,300,p.id,type.typeID);
    assert.ok(Math.abs(weights.reduce((a,b)=>a+b,0)-1)<1e-14);
  }
});
