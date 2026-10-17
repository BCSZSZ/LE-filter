export const lenses = [
  {id:"none",name:"无镜片",english:"",color:"#535b55",unlock:4},
  {id:"quality",name:"优质镜片",english:"Lens of Quality",color:"#b1532e",unlock:9},
  {id:"origin",name:"提升前缀镜片",english:"Lens of Origin",color:"#2c6b9b",unlock:4},
  {id:"finality",name:"提升后缀镜片",english:"Lens of Finality",color:"#7d5897",unlock:4},
];

export function selectProfile(data, type, career) {
  const available = data.profiles.filter(p => p.typeID === Number(type));
  return available.find(p => p.classRequirement === Number(career)) ?? available[0];
}

export function probabilities(profile, rank) {
  const regime = Number(rank) >= 9 ? "9" : "4";
  return lenses.map(lens => ({...lens,
    distribution: Number(rank) >= lens.unlock ? profile.probabilities[regime][lens.id] : null,
  }));
}

export function naturalRegime(rank) {
  return Number(rank) >= 11 ? "11" : Number(rank) >= 9 ? "9" : Number(rank) >= 4 ? "4" : "0";
}

export function naturalRarityWeights(data, corruption, playerCareer, typeID) {
  const model=data.naturalRarity;
  const c=Math.max(0,Number(corruption)||0), power=model.corruptionPower;
  const monsterPower=c<=100 ? power.linearTo100*c
    : power.powerCoefficient*c**power.power+power.linear*c+power.constant;
  const increasedRarity=model.corruptionRarityMod*monsterPower+model.otherIncreasedItemRarity;
  const extra=model.extraRollsPerIIR*increasedRarity;
  const n=Math.floor(extra),fraction=extra-n;
  const cutoff=(model.setChance+model.uniqueChance*model.uniqueDropEventMultiplier)
    *(1+model.uniqueSetIIRLogMultiplier*Math.log1p(increasedRarity));
  const cdf=value=>value<=cutoff ? 0 : (value-cutoff)/(1-cutoff)
    *((1-fraction)*value**n+fraction*value**(n+1));
  const cumulative=[0,...model.boundaries.slice(0,-1).map(cdf),1];
  const raw=cumulative.slice(1).map((value,i)=>Math.max(0,value-cumulative[i]));
  const selection=model.typeSelection.players.find(player=>player.id===Number(playerCareer));
  if(!selection) throw new Error("Unknown player class");
  // Bayes conditioning on an equipment type: only raw2 can divert into idols.
  raw[2]*=selection.raw2EquipmentFactorByType[String(typeID)];
  const total=raw.reduce((a,b)=>a+b,0);
  return raw.map(probability=>probability/total);
}

export function naturalProbability(data,profile,rank,corruption,playerCareer) {
  const weights=naturalRarityWeights(data,corruption,playerCareer,profile.typeID);
  const components=profile.naturalComponents[naturalRegime(rank)];
  const count=Array.from({length:5},(_,k)=>components.reduce((sum,row,n)=>sum+weights[n]*row.p_T7_count[k],0));
  const exalted=components.reduce((sum,row,n)=>sum+weights[n]*row.p_exalted,0);
  if(exalted<=0) return null;
  count[0]-=1-exalted;
  return count.map(value=>Math.max(0,value/exalted));
}

export function sourceRows(data,profile,rank,source,corruption,playerCareer) {
  if(source==="prophecy") return probabilities(profile,rank);
  return [{id:"natural",name:"普通掉落",english:"",color:"#386d51",
    distribution:naturalProbability(data,profile,rank,corruption,playerCareer)}];
}

export function thresholdOutcome(distribution,minimum) {
  if(distribution===null) return {probability:null,averageItems:null};
  const probability=distribution.slice(minimum).reduce((sum,value)=>sum+value,0);
  return {probability,averageItems:probability>0 ? 1/probability : Infinity};
}

export function chartExtent(corruption) {
  const selected = Number.isFinite(Number(corruption)) ? Math.max(0, Number(corruption)) : 0;
  return {selected, maximum:Math.max(1000, Math.ceil(selected / 1000) * 1000)};
}
