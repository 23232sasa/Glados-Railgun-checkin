## 当前账户配置（2026-09-13更新）

当前工作流每天北京时间08:00运行，也支持 Actions → GLaDOS daily check-in → Run workflow。GitHub调度可能延迟；此仓库为公开仓库，长期无活动时定时任务可能被停用，请定期检查 Actions。

1. Settings → Secrets and variables → Actions → Secrets：新增 `GLADOS_COOKIE`，值为登录会话Cookie。兼容原有 `GLADOS_COOKIES`，两者同时存在时优先前者。不要将Cookie提交到代码或日志。
2. 同页面 Variables：新增 `GLADOS_DOMAIN`，填写获取Cookie时地址栏的准确域名，不带 https:// 或路径。目前允许 glados.cloud、glados.rocks、glados.space、railgun.info。不能凭猜测选择；其他域名需先核实归属再修改代码。
3. 可选变量 `GLADOS_EXCHANGE_PLAN`：plan100、plan200 或 plan500，默认 plan500。按既有接口方案，分别在积分至少100、200、500时尝试兑换。实际兑换结果与权益以服务端为准。
4. 在 Actions 手动运行一次。签到成功或已签到后，达到门槛才兑换；签到/兑换失败会令任务失败。此版本不执行第三方推送、日志自动删除或保活操作。

脚本只向指定域名发送Cookie，拒绝HTTP跳转。更换域名必须使用该域名对应的Cookie。Cookie过期需自行更新。重新登录不保证旧会话必然撤销，请使用平台支持的会话撤销方式。

以下为上游原始说明；若有冲突，以本节及当前工作流为准。

---

# Glados自动签到

## 食用方式：

### 注册一个GLaDOS的账号([注册地址](https://glados.space/landing/0A58E-NV28S-6U3QV-33VMG))

#### 我的邀请码：([0A58E-NV28S-6U3QV-33VMG](https://0a58e-nv28s-6u3qv-33vmg.glados.space)) 

#### 我的优惠码（9折）：([DEVILSTORE](https://0a58e-nv28s-6u3qv-33vmg.glados.space)) 

### **Fork**本仓库

![图片加载失败](imgs/1.png)

### 添加**secret**

1. 跳转至自己的仓库的`Settings`->`Secrets and variables`->`Action`

2. 添加1个`repository secret`，命名为`GLADOS_COOKIES`，其值对应GLaDOS账号的cookie值中的有效部分（获取方式如下）

- 在GLaDOS的签到页面按`F12`

- 切换到`Network`页面下，刷新

![图片加载失败](imgs/2.png)

- 点击第一个选项卡后在`Request Headers`下找到`Cookie`，右键复制cookie的值即可

  > 参考格式：koa:sess=eyJ1c2xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxAwMH0=; koa:sess.sig=xJkOxxxxxxxxxxxxxxxtnM;

![图片加载失败](imgs/3.png)

- 多账号请在 `COOKIES` 中 添加多个 `cookies` 中间使用 `&`连接即可。（例如： `c1&c3&c3...`）

3. 配置积分兑换策略（非必须）

- 添加1个`repository secret`，命名为`GLADOS_EXCHANGE_PLAN`，配置自动兑换积分策略：

| 值 | 积分要求 | 兑换天数 |
|---|---------|---------|
| `plan100` | 100 积分 | 10 天 |
| `plan200` | 200 积分 | 30 天 |
| `plan500` | 500 积分 | 100 天 (默认) |

> 不配置时默认为 `plan500`，即积分达到 500 时自动兑换 100 天

4. 手机推送（非必须）

- 添加1个`repository secret`，命名为`PUSHDEER_SENDKEY`，其值对应 PushDeer key: ([获取地址](https://www.pushdeer.com/product.html))。

### **star**自己的仓库

![图片加载失败](imgs/4.png)

## 文件结构

```shell
│  checkin.py	# 签到脚本
│
├─.github
│  └─workflows
│          gladosCheck.yml	# Actions 配置文件
```

## 更新日志

- **2026-01**: 重构代码，添加log输出方便定位，支持新版网址，支持配置积分兑换策略。
- **2026-04**: 优化代码逻辑，优化日志输出，支持[新版域名](https://railgun.info) ，在 GLADOS_COOKIES 中添加新版域名下的 cookies 即可使用。


## 问题排查与定位
- 大家可以通过查询 actions 中的 running checkin 日志快速定位问题，有其他问题提交issue。

  <img width="1684" height="844" alt="image" src="https://github.com/user-attachments/assets/45348a5f-43e4-45f5-8fdf-ce84d343b30d" />

## 声明

本项目不保证稳定运行与更新, 因GitHub相关规定可能会删库, 请注意备份







