# LETools角色读取后端

该服务仅为[现有工作台](https://bcszsz.github.io/LE-filter/)读取公开角色配装。`relay.mjs`固定调用Maxroll的`/lastepoch/characters/{account}/{character}`，检查返回角色名并只保留已装备物品的容器号／序列化字节。来源账号取自固定请求路径；响应不包含账号名，不能声称从响应额外核验了账号。目标并集分类、个人保存与filter生成仍由现有工作台负责，后端没有写模版的接口。

LETools的`import_character.php`已在本机验证，但现有Cloudflare出口被其403拦截，因此不作为生产请求路径。Maxroll云端读取已验证。接口发现、官方API调查和76件物品的独立对照见[导入说明](../../docs/PROFILE_IMPORT.md)。

服务部署在Sites的Cloudflare Workers运行环境，使用Vinext API路由包装；`hosting.json`记录既有Sites身份，沿用该身份更新。完整Vinext源码由Sites独立仓库管理，当前本地checkout为`E:/Code/LE-filter-backend-relay`；这里保留实际业务模块与路由，便于随工作台审核。

更新时按Sites技能获取当前项目的源码凭据并用source helper打开，保留项目身份及公开访问范围。将仓库里的业务源码复制到打开的独立checkout：

```powershell
python -X utf8 scripts/prepare_profile_relay.py E:/Code/LE-filter-backend-relay
node --test tool/test_profile_relay.mjs
```

然后在后端checkout使用Sites构建、源码同步、打包和部署流程。凭据仅从stdin传入受管理helper；不要写入文件或命令行。Windows的npm命令转发若不能定位npm自身入口，可用Node调用已安装npm的`npm-cli.js`运行同一`build`脚本；源码helper打包需要Git Bash在该进程PATH内，GNU tar使用`TAR_OPTIONS=--force-local`处理盘符路径。不要修改系统配置。

部署后先验证`/health`、从工作台Origin发起的OPTIONS和四个公开角色的POST，再发布GitHub Pages。前端`tool/web/profile-import.js`保留当前后端地址；若部署工具返回新地址，以实际返回值为准更新并重新验证。已有角色JSON入口可以读取备份，线上主流程直接读取URL。
