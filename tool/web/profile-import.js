/* Fetch character targets through our relay; no source-site script execution. */
(function(root){
  const ENDPOINT='https://le-filter-profile-api.astutestoat4.chatgpt.site/api/profiles/read';
  function normalizeLinks(input){
    if(typeof input!=='string'&&!Array.isArray(input))throw Error('请填写LETools角色链接。');
    const values=Array.isArray(input)?input:input.trim().split(/\s+/),urls=[];
    if(values.length>100)throw Error('一次读取1–12个角色；重复链接只读取一次。');
    for(const value of values){
      if(!value)continue;
      let url;try{url=new URL(value);}catch{throw Error('每行填写一个完整的LETools角色链接。');}
      const match=url.pathname.match(/^\/profile\/(?:[a-z]{2}\/)?([^/]+)\/character\/([^/]+)\/?$/);
      if(url.protocol!=='https:'||!['www.lastepochtools.com','lastepochtools.com'].includes(url.host)||url.username||url.password||url.search||url.hash||!match)throw Error('只支持 https://www.lastepochtools.com/profile/账号/character/角色 链接。');
      let parts;try{parts=match.slice(1).map(decodeURIComponent);}catch{throw Error('账号或角色名编码不正确。');}
      if(parts.some(x=>!x||x.length>128||/[\u0000-\u001f\u007f/\\?#]/.test(x)))throw Error('账号或角色名格式不正确。');
      const canonical=`https://www.lastepochtools.com/profile/${encodeURIComponent(parts[0])}/character/${encodeURIComponent(parts[1])}`;
      if(!urls.includes(canonical))urls.push(canonical);
    }
    if(!urls.length||urls.length>12)throw Error('一次读取1–12个角色；重复链接只读取一次。');
    return urls;
  }
  async function readProfiles(input,{name='',signal,fetcher=root.fetch?.bind(root)}={}){
    const links=normalizeLinks(input);
    let response;
    const local=root.location?.protocol==='http:'&&['127.0.0.1','localhost'].includes(root.location.hostname)&&!root.LEFilterAPI;
    try{response=await fetcher(local?'/api/profiles/read':ENDPOINT,{method:'POST',credentials:'omit',headers:{'Content-Type':'application/json'},body:JSON.stringify({links,name}),signal});}
    catch(error){if(error.name==='AbortError')throw error;throw Error(error.name==='TimeoutError'?'读取超时，请稍后重试。':'角色读取服务暂不可用，请稍后重试。');}
    let bundle;try{bundle=await response.json();}catch{throw Error('角色读取服务返回异常，请稍后重试。');}
    if(!response.ok)throw Error(bundle.error||'角色读取失败，请稍后重试。');
    if(bundle.format!=='letools-profile-bundle'||bundle.version!==1||!Array.isArray(bundle.profiles)
       ||bundle.profiles.length!==links.length||bundle.profiles.some((p,i)=>p.url!==links[i]))throw Error('读取结果与所选角色不一致，本次未导入。');
    return bundle;
  }
  const api={normalizeLinks,readProfiles};root.LEProfileImport=api;if(typeof module!=='undefined')module.exports=api;
})(globalThis);
