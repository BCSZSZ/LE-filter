import {selectProfile, probabilities, chartExtent} from "./model.mjs";

const data = await fetch("probabilities.json").then(response => {
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
});
const $ = id => document.getElementById(id);
const format = value => `${(value * 100).toFixed(6)}%`;
const makeOption = (value, label) => new Option(label, value);
const classNames = new Map(data.classes.map(c => [c.id, c.id === 0 ? "通用" : c.name]));
for (const type of data.equipmentTypes) $("item").add(makeOption(type.typeID, type.name));
for (let rank=0; rank<=12; rank++) $("rank").add(makeOption(rank, rank));
$("rank").value = "12";
$("item").value = "21";
let previousCareer = 8;

function updateCareers() {
  const available = data.profiles.filter(p => p.typeID === Number($("item").value));
  $("career").replaceChildren(...available.map(p => makeOption(p.classRequirement, classNames.get(p.classRequirement))));
  $("career").value = available.some(p => p.classRequirement === previousCareer)
    ? String(previousCareer) : String(available[0].classRequirement);
  $("career").disabled = available.length === 1;
}

function drawChart(id, count, rows) {
  const svg = $(id), width=Math.max(320,Math.round(svg.clientWidth)), height=300, left=73, right=20, top=28, bottom=50;
  svg.setAttribute("viewBox",`0 0 ${width} ${height}`);
  const active = rows.filter(row => row.distribution);
  const maxValue = Math.max(...active.map(row => row.distribution[count]), 0);
  const ceiling = maxValue > 0 ? maxValue * 1.2 : .01;
  const {selected, maximum} = chartExtent($("corruption").value);
  const x = corruption => left + corruption/maximum*(width-left-right);
  const y = value => height-bottom-value/ceiling*(height-top-bottom);
  const text = (a,b,label,anchor="middle",css="") => `<text x="${a}" y="${b}" text-anchor="${anchor}" class="${css}">${label}</text>`;
  let content = "";
  for (let i=0; i<=4; i++) {
    const v=ceiling*i/4, yy=y(v);
    content += `<line class="grid" x1="${left}" y1="${yy}" x2="${width-right}" y2="${yy}"/>`;
    content += text(left-12, yy+5, `${(v*100).toFixed(count===1 ? 1 : 2)}%`, "end");
    content += text(x(maximum*i/4),height-bottom+27,Math.round(maximum*i/4));
  }
  content += `<line class="selected" x1="${x(selected)}" y1="${top}" x2="${x(selected)}" y2="${height-bottom}"/>`;
  for (const row of active) {
    const yy=y(row.distribution[count]);
    content += `<path class="curve" stroke="${row.color}" d="M${left} ${yy}H${width-right}"/>`;
    content += `<circle cx="${x(selected)}" cy="${yy}" r="4.5" fill="${row.color}"><title>${row.name}：${format(row.distribution[count])}；腐化 ${selected}</title></circle>`;
  }
  content += text(width-right,height-4,"巨石腐化","end","axis-label");
  svg.innerHTML = content;
}

function render() {
  const rank=Number($("rank").value);
  const profile=selectProfile(data,$("item").value,$("career").value);
  const rows=probabilities(profile,rank);
  $("probabilities").replaceChildren(...rows.map(row => {
    const tr=document.createElement("tr");
    const th=document.createElement("th");
    th.scope="row";
    th.innerHTML=`<span class="lens-name"><i class="dot" style="--color:${row.color}"></i>${row.name}</span>${row.english ? `<span class="english">${row.english}</span>` : ""}`;
    tr.append(th);
    for (const count of [1,2]) {
      const td=document.createElement("td");
      td.textContent=row.distribution ? format(row.distribution[count]) : "未解锁";
      if (!row.distribution) td.className="unavailable";
      tr.append(td);
    }
    return tr;
  }));
  $("legend").innerHTML=rows.filter(r=>r.distribution).map(row=>`<span><i style="--color:${row.color}"></i>${row.name}</span>`).join("");
  drawChart("chart-one",1,rows);
  drawChart("chart-two",2,rows);
  $("cof-rule").textContent=`命运 0–3 级：M = 1、Q = 1，普通崇高预言未解锁。4–8 级：M = 1.5、Q = 1。9–12 级：M = 1.5、Q = 2。当前 ${rank} 级${rank>=9 ? "：M = 1.5、Q = 2。" : rank>=4 ? "：M = 1.5、Q = 1。" : "。"}12 级奖励数量翻倍，单件概率不变。`;
}

$("settings").addEventListener("submit",event=>event.preventDefault());
$("item").addEventListener("change",()=>{updateCareers();render();});
$("career").addEventListener("change",()=>{if (Number($("career").value)) previousCareer=Number($("career").value);render();});
for (const id of ["rank","area","corruption"]) $(id).addEventListener("input",()=>{
  if ($(id).validity.valid) render();
});
updateCareers();
render();
window.addEventListener("resize",render);
