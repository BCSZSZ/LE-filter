import fs from "node:fs/promises";
import path from "node:path";
import {pathToFileURL} from "node:url";
import {Workbook, SpreadsheetFile} from "@oai/artifact-tool";

// Run with the bundled artifact-tool runtime, from the repository root.
const root = process.cwd();
const {thresholdOutcome}=await import(pathToFileURL(path.join(root,"tool/probability_web/model.mjs")));
const data = JSON.parse(await fs.readFile(path.join(root,"analysis/prophecy-probabilities.json"),"utf8"));
const output = path.join(root,"outputs/01a135a3-5a09-7e91-83c5-4bd333aeb5ea");
await fs.mkdir(output,{recursive:true});
const workbook = Workbook.create();
const sheet = workbook.worksheets.add("普通崇高预言");
const font = "Microsoft YaHei";
const last = 4 + 2*data.profiles.length;
sheet.showGridLines = false;
sheet.getRange(`A1:K${last}`).format.font = {name:font,size:12,color:"#25332A"};
sheet.getRange(`A1:K${last}`).format.verticalAlignment = "center";
sheet.getRange(`A1:K${last}`).format.rowHeight = 33;
sheet.getRange(`A1:A${last}`).format.columnWidth = 19;
sheet.getRange(`B1:B${last}`).format.columnWidth = 12;
sheet.getRange(`C1:C${last}`).format.columnWidth = 13;
sheet.getRange(`D1:K${last}`).format.columnWidth = 17;
sheet.getRange("A1:K1").merge();
sheet.getRange("A1").values = [["区域 100 级  ·  命运 12 级  ·  腐化 0  ·  普通崇高预言"]];
sheet.getRange("A1:K1").format.font = {name:font,size:15,bold:true,color:"#25332A"};
sheet.getRange("A1:K1").format.rowHeight = 39;
sheet.getRange("A2:K2").merge();
sheet.getRange("A2").values = [["最终崇高装备；平均件数 = 1 ÷ 概率"]];
sheet.getRange("A2:K2").format.rowHeight = 28;
sheet.getRange("A2:K2").format.font = {name:font,size:11,color:"#626B63"};
sheet.getRange("A3:A4").merge();
sheet.getRange("B3:B4").merge();
sheet.getRange("C3:C4").merge();
sheet.getRange("A3").values = [["物品种类"]];
sheet.getRange("B3").values = [["底材职业"]];
sheet.getRange("C3").values = [["指标"]];
const colors = ["#E8EDE8","#F7E9DF","#E3EDF5","#EEE7F3"];
const groups = [["D","E","无镜片"],["F","G","优质镜片"],["H","I","提升前缀镜片"],["J","K","提升后缀镜片"]];
for (let i=0;i<groups.length;i++) {
  const [left,right,label]=groups[i];
  sheet.getRange(`${left}3:${right}3`).merge();
  sheet.getRange(`${left}3`).values = [[label]];
  sheet.getRange(`${left}4:${right}4`).values = [["至少 1T7","至少 2T7"]];
  sheet.getRange(`${left}3:${right}4`).format.fill = colors[i];
}
sheet.getRange("A3:C4").format.fill = "#E8EDE8";
sheet.getRange("A3:K4").format.font = {name:font,size:12,bold:true,color:"#25332A"};
sheet.getRange("A3:K4").format.horizontalAlignment = "center";
const items = new Map(data.equipmentTypes.map(t=>[t.typeID,t.name]));
const careers = new Map(data.classes.map(c=>[c.id,c.id===0?"通用":c.name]));
for(const [index,profile] of data.profiles.entries()){
  const row=5+2*index;
  const p=profile.probabilities["9"];
  const values=["none","quality","origin","finality"].flatMap(lens=>[1,2].map(count=>thresholdOutcome(p[lens],count).probability));
  sheet.getRange(`A${row}:C${row+1}`).values = [
    [items.get(profile.typeID),careers.get(profile.classRequirement),"概率"],
    [null,null,"平均件数"]];
  sheet.getRange(`A${row}:A${row+1}`).merge();
  sheet.getRange(`B${row}:B${row+1}`).merge();
  sheet.getRange(`D${row}:K${row}`).values = [values];
  sheet.getRange(`D${row}:K${row}`).setNumberFormat("0.000000%");
  sheet.getRange(`D${row+1}:K${row+1}`).formulas = [[..."DEFGHIJK"].map(col=>`=1/${col}${row}`)];
  sheet.getRange(`D${row+1}:K${row+1}`).setNumberFormat("#,##0.00");
  sheet.getRange(`A${row+1}:K${row+1}`).format.rowHeight = 29;
  sheet.getRange(`C${row+1}:K${row+1}`).format.font = {name:font,size:11,color:"#626B63"};
  if(index%2===0) sheet.getRange(`A${row}:K${row+1}`).format.fill = "#F5F7F3";
  sheet.getRange(`A${row}:K${row}`).format.borders = {top:{style:"thin",color:"#CCD6C8"}};
}
sheet.getRange(`D5:K${last}`).format.horizontalAlignment = "right";
sheet.freezePanes.freezeRows(4);
sheet.freezePanes.freezeColumns(3);
workbook.recalculate();
console.log((await workbook.inspect({kind:"region",sheetId:sheet.name,range:"A3:K8",maxChars:2500,tableMaxRows:6,tableMaxCols:11})).ndjson);
const errors=await workbook.inspect({kind:"match",searchTerm:"#REF!|#DIV/0!|#VALUE!|#N/A|#NAME\\?|#NUM!|#SPILL!",options:{useRegex:true,maxResults:20},summary:"Workbook error scan",maxChars:1500});
console.log(errors.ndjson);
const preview=await workbook.render({sheetName:sheet.name,range:"A1:K12",scale:1.4,format:"png"});
await fs.writeFile(path.join(root,".cache/prophecy-excel/preview.png"),new Uint8Array(await preview.arrayBuffer()));
const xlsx=await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(path.join(output,"普通崇高预言-T7概率.xlsx"));
console.log(`Exported ${data.profiles.length} profiles with cumulative probabilities and reciprocal formulas`);
