// Reads public character equipment only. Filter policies stay in tool/engine.py.
export const UPSTREAM = 'https://planners.maxroll.gg/lastepoch/characters/';
export const WORKBENCH_ORIGIN = 'https://bcszsz.github.io';
const MAX_BODY = 16 * 1024, MAX_RESPONSE = 512 * 1024, TTL = 5 * 60 * 1000;

class ImportError extends Error {
  constructor(message, status = 400) { super(message); this.status = status; }
}

export function normalizeLinks(input) {
  if (typeof input !== 'string' && !Array.isArray(input)) throw new ImportError('请填写LETools角色链接。');
  const values = Array.isArray(input) ? input : input.trim().split(/\s+/), urls = [];
  if (values.length > 100) throw new ImportError('一次读取1–12个角色；重复链接只读取一次。');
  for (const value of values) {
    if (!value) continue;
    let url; try { url = new URL(value); } catch { throw new ImportError('每行填写一个完整的LETools角色链接。'); }
    const match = url.pathname.match(/^\/profile\/(?:[a-z]{2}\/)?([^/]+)\/character\/([^/]+)\/?$/);
    if (url.protocol !== 'https:' || !['www.lastepochtools.com', 'lastepochtools.com'].includes(url.host)
        || url.username || url.password || url.search || url.hash || !match) {
      throw new ImportError('只支持 https://www.lastepochtools.com/profile/账号/character/角色 链接。');
    }
    let parts; try { parts = match.slice(1).map(decodeURIComponent); } catch { throw new ImportError('账号或角色名编码不正确。'); }
    if (parts.some(x => !x || x.length > 128 || /[\u0000-\u001f\u007f/\\?#]/.test(x))) throw new ImportError('账号或角色名格式不正确。');
    const canonical = `https://www.lastepochtools.com/profile/${encodeURIComponent(parts[0])}/character/${encodeURIComponent(parts[1])}`;
    if (!urls.includes(canonical)) urls.push(canonical);
  }
  if (!urls.length || urls.length > 12) throw new ImportError('一次读取1–12个角色；重复链接只读取一次。');
  return urls;
}

async function readJSON(response, limit) {
  if (Number(response.headers.get('Content-Length')) > limit) throw new ImportError('角色数据超过大小限制。', 502);
  const reader = response.body?.getReader();
  if (!reader) throw new ImportError('返回数据为空。', 502);
  let length = 0; const chunks = [];
  try {
    while (true) {
      const { done, value } = await reader.read(); if (done) break;
      length += value.byteLength;
      if (length > limit) throw new ImportError('返回数据超过大小限制。', 413);
      chunks.push(value);
    }
  } catch (error) { await reader.cancel().catch(() => {}); throw error; }
  const bytes = new Uint8Array(length); let offset = 0;
  for (const value of chunks) { bytes.set(value, offset); offset += value.length; }
  try { return JSON.parse(new TextDecoder().decode(bytes)); } catch { throw new ImportError('返回数据不是有效JSON。', 502); }
}

export function compactCharacter(raw, url) {
  const parts = new URL(url).pathname.split('/').map(decodeURIComponent), account = parts[2], character = parts[4];
  if (raw?.error || !raw) throw new ImportError(`无法读取 ${character}：角色未公开、账号／角色名不正确，或来源站暂时不可用。`, 502);
  if (typeof raw.characterName !== 'string' || raw.characterName.toLowerCase() !== character.toLowerCase()) {
    throw new ImportError(`来源返回的角色与 ${character} 链接不一致。`, 502);
  }
  if (!Array.isArray(raw.savedItems) || raw.savedItems.length > 2000) throw new ImportError(`${character}缺少装备数据，或来源格式已变化。`, 502);
  if (raw.savedItems.some(item => !item || typeof item !== 'object' || !Number.isInteger(item.containerID))) throw new ImportError('来源物品位置格式已变化。', 502);
  const items = raw.savedItems.filter(item => item && (item.containerID >= 2 && item.containerID <= 12 || [29, 123].includes(item.containerID)));
  if (!items.length || items.length > 37) throw new ImportError(`${character}没有可读取的装备，或物品数量不正确。`, 502);
  const savedItems = items.map(item => {
    if (!Number.isInteger(item.containerID) || !Array.isArray(item.data) || item.data.length < 10 || item.data.length > 256
        || item.data.some(n => !Number.isInteger(n) || n < 0 || n > 255)) throw new ImportError('来源物品格式已变化。', 502);
    return { containerID: item.containerID, data: item.data };
  });
  return { url, provider: 'Maxroll', api_url: UPSTREAM + encodeURIComponent(account) + '/' + encodeURIComponent(character),
    ...(typeof raw.lastUpdated === 'string' || typeof raw.lastUpdated === 'number' ? { last_updated: raw.lastUpdated } : {}),
    save: { characterName: raw.characterName, savedItems } };
}

export function createRelay({ fetcher = (...args) => fetch(...args), now = Date.now } = {}) {
  const cache = new Map(), pending = new Map();
  async function character(url) {
    const hit = cache.get(url); if (hit?.expires > now()) return hit.value;
    if (pending.has(url)) return pending.get(url);
    if (pending.size >= 24) throw new ImportError('角色读取服务繁忙，请稍后重试。', 429);
    const task = (async () => {
      const parts = new URL(url).pathname.split('/').map(decodeURIComponent), name = parts[4];
      let response;
      try {
        // Workers supports manual redirects; reject the 3xx response below.
        response = await fetcher(UPSTREAM + encodeURIComponent(parts[2]) + '/' + encodeURIComponent(name), { method: 'GET', redirect: 'manual',
          headers: { Accept: 'application/json', 'User-Agent': 'LE-filter character importer' }, signal: AbortSignal.timeout(20000) });
      } catch (error) {
        console.error('Character API request failed', error.name, error.message);
        throw new ImportError(`${name}读取${error.name === 'TimeoutError' || error.name === 'AbortError' ? '超时' : '失败'}，请稍后重试。`, 502);
      }
      if (!response.ok) {
        console.error('Character API HTTP error', response.status);
        await response.body?.cancel();
        throw new ImportError(`${name}来源站返回HTTP ${response.status}，请稍后重试。`, 502);
      }
      let raw; try { raw = await readJSON(response, MAX_RESPONSE); }
      catch { throw new ImportError(`${name}返回数据无效或超过大小限制，请稍后重试。`, 502); }
      const value = compactCharacter(raw, url);
      if (cache.size >= 256) cache.delete(cache.keys().next().value);
      cache.set(url, { expires: now() + TTL, value }); return value;
    })();
    pending.set(url, task);
    try { return await task; } finally { pending.delete(url); }
  }

  return async function handle(request) {
    const origin = request.headers.get('Origin'), url = new URL(request.url);
    const allowed = origin === WORKBENCH_ORIGIN || /^http:\/\/(?:127\.0\.0\.1|localhost)(?::\d+)?$/.test(origin || '') || origin === url.origin;
    const headers = { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', Vary: 'Origin',
      ...(allowed ? { 'Access-Control-Allow-Origin': origin, 'Access-Control-Allow-Methods': 'POST, OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Max-Age': '600' } : {}) };
    const reply = (data, status = 200) => new Response(JSON.stringify(data), { status, headers });
    if (origin && !allowed) return reply({ error: '请求来源不受支持。' }, 403);
    if (url.pathname === '/health' && request.method === 'GET') return reply({ ok: true, service: 'le-filter-profile-api', version: 1 });
    if (url.pathname !== '/api/profiles/read') return reply({ error: 'Not found' }, 404);
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers });
    if (request.method !== 'POST') return reply({ error: '请使用POST读取角色。' }, 405);
    try {
      if (!request.headers.get('Content-Type')?.toLowerCase().startsWith('application/json')) throw new ImportError('请求需要JSON格式。');
      let payload;
      try { payload = await readJSON(request, MAX_BODY); } catch (error) { throw new ImportError(error.message, error.status === 413 ? 413 : 400); }
      if (!payload || typeof payload !== 'object' || Array.isArray(payload)) throw new ImportError('读取参数不正确。');
      const urls = normalizeLinks(payload.links);
      if (payload.name != null && (typeof payload.name !== 'string' || payload.name.length > 100)) throw new ImportError('个人BD名称请限制在100字以内。');
      const profiles = new Array(urls.length); let next = 0, failed;
      // Three requests at a time, with stable input order and a complete-result gate.
      await Promise.all(Array.from({ length: Math.min(3, urls.length) }, async () => {
        while (!failed && next < urls.length) {
          const index = next++;
          try { profiles[index] = await character(urls[index]); } catch (error) { failed ||= error; }
        }
      }));
      if (failed) throw failed;
      return reply({ format: 'letools-profile-bundle', version: 1, name: payload.name?.trim() || '', profiles });
    } catch (error) { return reply({ error: error instanceof ImportError ? error.message : '角色读取服务暂不可用，请稍后重试。' }, error instanceof ImportError ? error.status : 502); }
  };
}

export const handle = createRelay();
