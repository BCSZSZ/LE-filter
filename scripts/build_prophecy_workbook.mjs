import fs from "node:fs/promises";
import path from "node:path";
import {Workbook, SpreadsheetFile} from "@oai/artifact-tool";

// Run with the bundled artifact-tool runtime, from the repository root.
const root = process.cwd();
const data = JSON.parse(await fs.readFile(path.join(root,"analysis/prophecy-probabilities.json"),"utf8"));
const output = path.join(root,"outputs/01a135a3-5a09-7e91-83c5-4bd333aeb5ea");
await fs.mkdir(output,{recursive:true});
const workbook = Workbook.create();
const sheet = workbook.worksheets.add("普通崇高预言");
const font = "Microsoft YaHei";
const last = 4 + data.profiles.length;
sheet.showGridLines = false;
sheet.getRange(`A1:J${last}`).format.font = {name:font,size:12,color:"#25332A"};
sheet.getRange(`A1:J${last}`).format.verticalAlignment = "center";
sheet.getRange(`A1:J${last}`).format.rowHeight = 33;
sheet.getRange(`A1:A${last}`).format.columnWidth = 19;
sheet.getRange(`B1:B${last}`).format.columnWidth = 12;
sheet.getRange(`C1:J${last}`).format.columnWidth = 17;
sheet.getRange("A1:J1").merge();
sheet.getRange("A1").values = [["区域 100 级  ·  命运 12 级  ·  腐化 0  ·  普通崇高预言"]];
sheet.getRange("A1:J1").format.font = {name:font,size:15,bold:true,color:"#25332A"};
sheet.getRange("A1:J1").format.rowHeight = 39;
sheet.getRange("A2:J2").format.rowHeight = 12;
sheet.getRange("A3:A4").merge();
sheet.getRange("B3:B4").merge();
sheet.getRange("A3").values = [["物品种类"]];
sheet.getRange("B3").values = [["底材职业"]];
const colors = ["#E8EDE8","#F7E9DF","#E3EDF5","#EEE7F3"];
const groups = [["C","D","无镜片"],["E","F","优质镜片"],["G","H","提升前缀镜片"],["I","J","提升后缀镜片"]];
for (let i=0;i<groups.length;i++) {
  const [left,right,label]=groups[i];
  sheet.getRange(`${left}3:${right}3`).merge();
  sheet.getRange(`${left}3`).values = [[label]];
  sheet.getRange(`${left}4:${right}4`).values = [["恰好 1T7","恰好 2T7"]];
  sheet.getRange(`${left}3:${right}4`).format.fill = colors[i];
}
sheet.getRange("A3:B4").format.fill = "#E8EDE8";
sheet.getRange("A3:J4").format.font = {name:font,size:12,bold:true,color:"#25332A"};
sheet.getRange("C3:J4").format.horizontalAlignment = "center";
const items = new Map(data.equipmentTypes.map(t=>[t.typeID,t.name]));
const careers = new Map(data.classes.map(c=>[c.id,c.id===0?"通用":c.name]));
const rows = data.profiles.map(profile=>{
  const p=profile.probabilities["9"];
  return [items.get(profile.typeID),careers.get(profile.classRequirement),
    ...["none","quality","origin","finality"].flatMap(lens=>[p[lens][1],p[lens][2]])];
});
sheet.getRange(`A5:J${last}`).values = rows;
sheet.getRange(`C5:J${last}`).setNumberFormat("0.000000%");
sheet.getRange(`C5:J${last}`).format.horizontalAlignment = "right";
for (let r=5;r<=last;r++) {
  if (r%2===1) sheet.getRange(`A${r}:J${r}`).format.fill = "#F5F7F3";
  if (r===5 || rows[r-5][0]!==rows[r-6][0]) {
    sheet.getRange(`A${r}:J${r}`).format.borders = {top:{style:"thin",color:"#CCD6C8"}};
  }
}
sheet.freezePanes.freezeRows(4);
sheet.freezePanes.freezeColumns(2);
workbook.recalculate();
console.log((await workbook.inspect({kind:"region",sheetId:sheet.name,range:"A3:J8",maxChars:3000,tableMaxRows:6,tableMaxCols:10})).ndjson);
const errors=await workbook.inspect({kind:"match",searchTerm:"#REF!|#DIV/0!|#VALUE!|#N/A|#NAME\\?|#NUM!|#SPILL!",options:{useRegex:true,maxResults:20},summary:"Workbook error scan",maxChars:1500});
console.log(errors.ndjson);
const preview=await workbook.render({sheetName:sheet.name,range:"A1:J13",scale:1.4,format:"png"});
await fs.writeFile(path.join(root,".cache/prophecy-excel/preview.png"),new Uint8Array(await preview.arrayBuffer()));
const xlsx=await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(path.join(output,"普通崇高预言-T7概率.xlsx"));
console.log(`Exported ${rows.length} profiles`);
