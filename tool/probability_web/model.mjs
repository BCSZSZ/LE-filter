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

export function chartExtent(corruption) {
  const selected = Number.isFinite(Number(corruption)) ? Math.max(0, Number(corruption)) : 0;
  return {selected, maximum:Math.max(1000, Math.ceil(selected / 1000) * 1000)};
}
