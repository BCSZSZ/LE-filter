import {selectProfile, sourceRows, chartExtent, naturalRarityWeights, thresholdOutcome} from "./model.mjs";

const data=await fetch("probabilities.json").then(response=>{
  if(!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
});
const $=id=>document.getElementById(id);
const format=value=>`${(value*100).toFixed(6)}%`;
const formatAverage=value=>`平均 ${Number.isFinite(value) ? value.toLocaleString("zh-CN",{minimumFractionDigits:2,maximumFractionDigits:2}) : "∞"} 件出 1 件`;
const makeOption=(value,label)=>new Option(label,value);
const classNames=new Map(data.classes.map(c=>[c.id,c.id===0 ? "通用" : c.name]));
for(const type of data.equipmentTypes) $("item").add(makeOption(type.typeID,type.name));
for(const career of data.naturalRarity.typeSelection.players) $("player-career").add(makeOption(career.id,career.name));
for(let rank=0;rank<=12;rank++) $("rank").add(makeOption(rank,rank));
$("rank").value="12";
$("item").value="21";
$("player-career").value="3";
let previousCareer=8;

function updateCareers(){
  const available=data.profiles.filter(p=>p.typeID===Number($("item").value));
  $("career").replaceChildren(...available.map(p=>makeOption(p.classRequirement,classNames.get(p.classRequirement))));
  $("career").value=available.some(p=>p.classRequirement===previousCareer)
    ? String(previousCareer) : String(available[0].classRequirement);
  $("career").disabled=available.length===1;
}

function drawChart(id,count,rows,extent){
  const svg=$(id),width=Math.max(320,Math.round(svg.clientWidth)),height=300,left=80,right=20,top=28,bottom=50;
  svg.setAttribute("viewBox",`0 0 ${width} ${height}`);
  const active=rows.filter(row=>row.distribution);
  const values=active.flatMap(row=>row.points.map(point=>point.outcomes[count].probability));
  const maxValue=Math.max(0,...values),minValue=values.length ? Math.min(...values) : 0;
  const natural=active.length===1 && active[0].id==="natural";
  const spread=Math.max(maxValue-minValue,1e-8);
  const floor=natural ? Math.max(0,minValue-spread*.2) : 0;
  const ceiling=natural ? maxValue+spread*.2 : maxValue>0 ? maxValue*1.2 : .01;
  const precision=Math.min(6,Math.max(count===1 ? 1 : 2,2-Math.floor(Math.log10((ceiling-floor)*100))));
  const x=corruption=>left+corruption/extent.maximum*(width-left-right);
  const y=value=>height-bottom-(value-floor)/(ceiling-floor)*(height-top-bottom);
  const text=(a,b,label,anchor="middle",css="")=>`<text x="${a}" y="${b}" text-anchor="${anchor}" class="${css}">${label}</text>`;
  let content="";
  for(let i=0;i<=4;i++){
    const v=floor+(ceiling-floor)*i/4,yy=y(v);
    content+=`<line class="grid" x1="${left}" y1="${yy}" x2="${width-right}" y2="${yy}"/>`;
    content+=text(left-12,yy+5,`${(v*100).toFixed(precision)}%`,"end");
    content+=text(x(extent.maximum*i/4),height-bottom+27,Math.round(extent.maximum*i/4));
  }
  content+=`<line class="selected" x1="${x(extent.selected)}" y1="${top}" x2="${x(extent.selected)}" y2="${height-bottom}"/>`;
  for(const row of active){
    const path=row.points.map((point,i)=>`${i ? "L" : "M"}${x(point.corruption)} ${y(point.outcomes[count].probability)}`).join("");
    content+=`<path class="curve" stroke="${row.color}" d="${path}"/>`;
    content+=`<circle cx="${x(extent.selected)}" cy="${y(row.outcomes[count].probability)}" r="4.5" fill="${row.color}"><title>${row.name}：${format(row.outcomes[count].probability)}；${formatAverage(row.outcomes[count].averageItems)}；腐化 ${extent.selected}</title></circle>`;
  }
  content+=text(width-right,height-4,"巨石腐化","end","axis-label");
  svg.innerHTML=content;
}

function render(){
  const rank=Number($("rank").value),source=$("source").value,natural=source==="natural";
  const playerCareer=Number($("player-career").value);
  const profile=selectProfile(data,$("item").value,$("career").value);
  const extent=chartExtent($("corruption").value);
  const valuesAt=corruption=>sourceRows(data,profile,rank,source,corruption,playerCareer).map(row=>{
    return {...row,outcomes:Object.fromEntries([1,2].map(minimum=>[minimum,thresholdOutcome(row.distribution,minimum)]))};
  });
  const rows=valuesAt(extent.selected);
  const locations=natural ? [...new Set([...Array.from({length:201},(_,i)=>extent.maximum*i/200),100,300,600,1000,extent.selected])].filter(c=>c<=extent.maximum).sort((a,b)=>a-b) : [0,extent.maximum];
  const samples=locations.map(c=>({corruption:c,rows:valuesAt(c)}));
  for(const row of rows) row.points=samples.map(sample=>({corruption:sample.corruption,outcomes:sample.rows.find(r=>r.id===row.id).outcomes})).filter(point=>point.outcomes[1].probability!==null);
  $("probabilities").replaceChildren(...rows.map(row=>{
    const tr=document.createElement("tr"),th=document.createElement("th");
    th.scope="row";
    th.innerHTML=`<span class="lens-name"><i class="dot" style="--color:${row.color}"></i>${row.name}</span>${row.english ? `<span class="english">${row.english}</span>` : ""}`;
    tr.append(th);
    for(const count of [1,2]){
      const td=document.createElement("td");
      if(row.distribution){
        const probability=document.createElement("span"),average=document.createElement("span");
        probability.className="probability-value";
        probability.textContent=format(row.outcomes[count].probability);
        average.className="average-items";
        average.textContent=formatAverage(row.outcomes[count].averageItems);
        td.append(probability,average);
      } else {
        td.textContent="未解锁";
        td.className="unavailable";
      }
      tr.append(td);
    }
    return tr;
  }));
  $("source-heading").textContent=natural ? "来源" : "镜片";
  $("player-career").disabled=!natural;
  $("lens-section").hidden=natural;
  $("natural-rules").hidden=!natural;
  document.querySelector(".download").hidden=natural;
  $("probability-scope").textContent=natural
    ? "每件最终崇高装备 · 普通随机掉落 · 额外地图稀有度 0%"
    : "每件最终崇高装备 · 普通崇高预言";
  $("legend").innerHTML=rows.filter(r=>r.distribution).map(row=>`<span><i style="--color:${row.color}"></i>${row.name}</span>`).join("");
  drawChart("chart-one",1,rows,extent);
  drawChart("chart-two",2,rows,extent);
  $("generation-order").textContent=natural ? "稀有度与词缀数量 → 自然阶数 → 命运崇高保底" : "自然阶数 → 镜片升阶 → 保证崇高";
  $("generation-scope").textContent=natural
    ? "100 级普通随机掉落，不含额外保证稀有及特殊词缀来源。额外地图稀有度 0%，无活动暗金加成。装备职业按底材归属计算。"
    : "普通崇高预言奖励固定 100 级，其单件 T7 概率不受巨石腐化影响。装备职业按底材归属计算。";
  $("cof-rule").textContent=`命运 0–3 级：M = 1、Q = 1。4–8 级：M = 1.5、Q = 1。9–12 级：M = 1.5、Q = 2。${natural ? "11 级起，初始稀有装备另有 25% 机会开启崇高保底。" : "普通崇高预言 4 级解锁，优质镜片 9 级解锁；12 级增加奖励数量，单件概率不变。"}`;
  const raw=natural ? naturalRarityWeights(data,extent.selected,playerCareer,profile.typeID) : data.rawRarityProbabilities;
  $("affix-count-rule").textContent=natural
    ? `当前腐化下，0／1／2／3／4 词缀起点的概率依次为 ${raw.map(p=>`${(p*100).toFixed(3)}%`).join("／")}。前缀、后缀各最多 2 条，同一词缀不重复。1／2 词缀起点的自然 T5 → T6 概率额外乘 5%。`
    : "词缀数为 1／2／3／4 的概率依次为 0.5%／0.995%／39.402%／59.103%；前缀、后缀各最多 2 条，同一词缀不重复。1／2 词缀起点的自然 T5 → T6 概率额外乘 5%。";
}

$("settings").addEventListener("submit",event=>event.preventDefault());
$("item").addEventListener("change",()=>{updateCareers();render();});
$("career").addEventListener("change",()=>{if(Number($("career").value)) previousCareer=Number($("career").value);render();});
for(const id of ["source","rank","player-career"]) $(id).addEventListener("change",render);
$("corruption").addEventListener("input",()=>{if($("corruption").validity.valid) render();});
updateCareers();
render();
window.addEventListener("resize",render);
