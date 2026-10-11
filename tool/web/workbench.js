/* Official templates and browser-owned working copies have separate lifetimes. */
(function(root){
  const copy = value => JSON.parse(JSON.stringify(value));
  const emptyProfile = () => ({uniques:[],equipment:[],altars:[],idols:[],bases:[]});
  const emptyLeveling = () => ({affixes:[],bases:[]});
  function freeze(value){
    Object.values(value).forEach(v=>{if(v&&typeof v==='object')freeze(v);});
    return Object.freeze(value);
  }
  function library(examples){return freeze(copy(examples.builds));}
  function restore(examples,saved){
    const config=copy(saved||examples);
    if(!saved)config.builds=config.builds.filter(b=>b.enabled);
    for(const b of config.builds){
      if(!b.template_id&&examples.builds.some(t=>t.id===b.id))b.template_id=b.id;
    }
    return config;
  }
  function useTemplate(config,templates,id){
    const template=templates.find(t=>t.id===id);
    if(!template)throw Error('找不到这个模板。');
    let b=config.builds.find(b=>b.id===id)||config.builds.find(b=>b.template_id===id);
    const reused=!!b;
    if(!b){b={...copy(template),template_id:id};config.builds.push(b);}
    b.enabled=true;
    if(!config.builds.some(b=>b.enabled&&b.id===config.main_id))config.main_id=b.id;
    return {build:b,reused};
  }
  function resetBuild(config,templates,id){
    const index=config.builds.findIndex(b=>b.id===id),b=config.builds[index];
    const template=templates.find(t=>t.id===(b?.template_id||b?.id));
    if(!template)throw Error('这个保存没有对应的官方模板。');
    config.builds[index]={...copy(template),id:b.id,name:b.name,enabled:b.enabled,template_id:template.id};
    return config.builds[index];
  }
  function importRequirement(config,templates,data){
    let b=config.builds.find(b=>b.id===data.id);
    if(!b){
      b={id:data.id,name:data.name,enabled:false,profiles:{endgame:emptyProfile(),leveling:emptyLeveling()}};
      if(templates.some(t=>t.id===data.id))b.template_id=data.id;
      config.builds.push(b);
    }
    b.name=data.name;b.profiles[data.stage]=copy(data.profile);
    b.requirement_sources||={};b.requirement_sources[data.stage]=copy(data.source);
    return b;
  }
  const api={library,restore,useTemplate,resetBuild,importRequirement};
  root.LEWorkbench=api;
  if(typeof module!=='undefined')module.exports=api;
})(globalThis);
