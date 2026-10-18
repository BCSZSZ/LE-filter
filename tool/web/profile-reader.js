/* A user-run bookmark reads LETools on its own origin, then returns target data. */
(function(root){
  function normalizeLinks(input){
    const values=Array.isArray(input)?input:String(input).trim().split(/\s+/);
    const urls=[];
    for(const value of values){
      if(!value)continue;
      let url;try{url=new URL(value);}catch{throw Error('每行填写一个完整的LETools角色链接。');}
      const match=url.pathname.match(/^\/profile\/(?:[a-z]{2}\/)?([^/]+)\/character\/([^/]+)\/?$/);
      if(url.protocol!=='https:'||!['www.lastepochtools.com','lastepochtools.com'].includes(url.host)||url.username||url.password||url.search||url.hash||!match)throw Error('只支持 https://www.lastepochtools.com/profile/账号/character/角色 链接。');
      const parts=match.slice(1).map(x=>decodeURIComponent(x));
      if(parts.some(x=>!x||/[\u0000-\u001f/\\?#]/.test(x)))throw Error('账号或角色名格式不正确。');
      const canonical=`https://www.lastepochtools.com/profile/${encodeURIComponent(parts[0])}/character/${encodeURIComponent(parts[1])}`;
      if(!urls.includes(canonical))urls.push(canonical);
    }
    if(!urls.length||urls.length>12)throw Error('一次读取1–12个角色；重复链接只读取一次。');
    return urls;
  }

  async function runReader(options,env=globalThis){
    const {document,location}=env;
    if(location.origin!=='https://www.lastepochtools.com'){
      env.alert('先打开列表中的第一个LETools角色页面，再点击收藏栏中的读取书签。');return;
    }
    const links=normalizeLinks(options.links),back=new URL(options.returnURL);
    if(back.protocol!=='https:'&&!(back.protocol==='http:'&&['127.0.0.1','localhost'].includes(back.hostname)))throw Error('返回工作台地址无效。');
    const old=document.getElementById('le-filter-profile-reader');if(old)old.remove();
    const panel=document.createElement('div');panel.id='le-filter-profile-reader';
    panel.style.cssText='position:fixed;z-index:2147483647;top:24px;left:24px;right:24px;max-width:720px;padding:24px;background:#131c2a;color:#fff;border:2px solid #edbc69;border-radius:12px;font:16px/1.6 sans-serif;box-shadow:0 8px 48px #000';
    const status=document.createElement('p');panel.append(status);document.body.append(panel);
    const profiles=[];
    const request=async url=>{
      const response=await env.fetch(url,{credentials:'same-origin',signal:env.AbortSignal.timeout(30000)});
      if(!response.ok)throw Error(`来源站返回HTTP ${response.status}；请在浏览器打开该角色确认可访问后重试。`);
      return response;
    };
    const compactItem=item=>{
      if(item==null)return {id:null,affixes:[]};
      if(typeof item!=='object')throw Error('来源物品数据格式已变化，请更新读取工具。');
      const result={id:item.id||null,affixes:[]};
      const compactAffix=affix=>{
        if(!affix||typeof affix.id!=='string')throw Error('来源词缀编码格式已变化。');
        return {id:affix.id,...(Number.isInteger(affix.tier)?{tier:affix.tier}:{})};
      };
      if(!Array.isArray(item.affixes||[]))throw Error('来源词缀列表格式已变化。');
      result.affixes=(item.affixes||[]).map(compactAffix);
      for(const key of ['sealedAffix','primordialAffix','corruptedAffix'])if(item[key])result[key]=compactAffix(item[key]);
      return result;
    };
    try{
      for(const [index,url] of links.entries()){
        status.textContent=`读取 ${index+1}/${links.length}：${decodeURIComponent(url.split('/').at(-1))}…`;
        let raw;
        if(location.href.split(/[?#]/)[0].replace(/\/$/,'')===url&&env._profileDataPromise){
          raw=await env._profileDataPromise;
        }else{
          const html=await (await request(url)).text();
          /* Read the token named by the page's own prefetch; never execute HTML/scripts. */
          const variable=html.match(/fetch\s*\(\s*['"]\/api\/internal\/profile_data\/['"]\s*\+\s*([\w$]+)/)?.[1];
          if(!variable)throw Error('页面未包含角色数据入口，可能正在验证访问；请先打开该角色页面后重试。');
          const escaped=variable.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
          const token=html.match(new RegExp('\\b(?:let|var|const)\\s+'+escaped+'\\s*=\\s*[\'\"]([a-f0-9]{32})[\'\"]'))?.[1];
          if(!token)throw Error('角色数据入口已变化，请更新读取工具。');
          raw=await (await request('/api/internal/profile_data/'+token)).json();
        }
        const data=raw?.buildInfo?.data;
        if(!data||!data.equipment||!Array.isArray(data.idols))throw Error('角色未公开、没有装备数据，或来源站格式已变化。');
        const expected=normalizeLinks([`https://www.lastepochtools.com/profile/${encodeURIComponent(raw.charInfo?.accountName||'')}/character/${encodeURIComponent(raw.charInfo?.characterName||'')}`])[0];
        if(expected.toLowerCase()!==url.toLowerCase())throw Error('来源返回的账号／角色与所选链接不一致。');
        profiles.push({url,data_version:raw.buildInfo.data_version,last_updated:raw.charInfo?.lastUpdated,
          data:{equipment:Object.fromEntries(Object.entries(data.equipment).map(([slot,item])=>[slot,compactItem(item)])),idols:data.idols.map(compactItem)}});
      }
      const bundle={format:'letools-profile-bundle',version:1,name:options.name,profiles};
      const json=JSON.stringify(bundle),blob=new env.Blob([json],{type:'application/json'}),file=document.createElement('a');
      file.href=env.URL.createObjectURL(blob);file.download='LETools-profiles.json';file.textContent='下载角色JSON（备用）';file.style.cssText='display:block;color:#edbc69;margin-top:12px';panel.append(file);
      back.hash='profile-import='+encodeURIComponent(json);
      const link=document.createElement('a');link.href=back.href;link.target='_blank';link.rel='noopener';link.textContent='返回工作台，预览并集';link.style.cssText='display:block;color:#8ddbc8;font-weight:bold;margin-top:12px';panel.append(link);
      status.textContent=`${profiles.length}个角色读取完成。点击下方返回工作台核对目标，再保存为个人方案。`;
      return bundle;
    }catch(error){status.textContent=`读取失败：${error.message} 本次未导入任何目标。`;throw error;}
  }

  function makeBookmarklet(links,returnURL,name=''){
    const options={links:normalizeLinks(links),returnURL,name:name.trim()};
    const source='void(async()=>{const normalizeLinks='+normalizeLinks.toString()+';await ('+runReader.toString()+')('+JSON.stringify(options)+').catch(()=>{});})()';
    return 'javascript:'+encodeURIComponent(source);
  }
  function bundleFromHash(hash){
    if(!hash.startsWith('#profile-import='))return null;
    if(hash.length>1000000)throw Error('角色数据过大，请使用角色JSON文件。');
    return JSON.parse(decodeURIComponent(hash.slice('#profile-import='.length)));
  }
  const api={normalizeLinks,makeBookmarklet,runReader,bundleFromHash};
  root.LEProfileReader=api;if(typeof module!=='undefined')module.exports=api;
})(globalThis);
