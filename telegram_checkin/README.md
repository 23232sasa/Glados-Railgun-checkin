# Telegram 多账号签到

支持至少16个账号（列表无16个上限，4个账号并发执行）。目标机器人 `@sheeridverifier_bot`，命令 `/checkin`。

## 首次配置

1. 在自己的电脑安装 Python 3.11 或更新版本。下载本目录。
2. 从 https://my.telegram.org 获取自己的 API ID 和 API hash。
3. 终端执行 `python -m pip install -r requirements.txt`，然后 `python login.py`。
4. 输入账号数量并逐个登录。验证码和两步验证密码仅在本机输入。电脑需要能直接访问 Telegram；此工具未配置代理，连接不上时先解决网络。
5. 登录后用户目录生成 `telegram-sessions-private.json`。不要提交、截图或分享此文件。
6. 在仓库 Settings → Secrets and variables → Actions 添加三个 Repository secrets：
   - `TG_API_ID`：API ID
   - `TG_API_HASH`：API hash
   - `TG_SESSIONS`：上述 JSON 文件的全部内容
7. 添加 Repository variable `TG_ENABLED`，值为 `true`。未启用时工作流跳过，不发送命令。
8. Actions → Telegram daily check-in → Run workflow。Summary 按账号序号显示结果。

## 时间及判断

北京时间08:00到23:00每小时调度一次；GitHub 可能延迟，不能保证准点。每个账号距上次命令不足一小时则跳过。手动运行同样遵守当天成功后停止和一小时冷却，但允许08:00前运行。

只有去掉空白后包含“出席率成功”的机器人回复算成功；“今天已经签到了”不算成功。若真实回复不是该文字格式，需调整匹配规则。处理中的回复会轮询两分钟，含消息编辑；超时后下次运行先核对历史。

运行前查机器人当天历史：已有成功回复就跳过，因此手机手动签到也能同步。缓存保存账号哈希、成功日期及重试时间，不保存会话。缓存被清理时，通过消息历史恢复成功状态和最近命令；若历史被删除则无法完整恢复。Telegram限流时尊重等待时间；缓存失效时服务端仍可能再次拒绝请求。

某账号失败不阻止其他账号。失败显示红叉，下一次计划运行重试。不要同时让旧App自动签到，避免两端同时发命令。当前尚需配置真实会话后进行联网验收。

## 安全

GitHub Secrets 保存登录会话。获得会话的人可以登录账号，可通过 Telegram 设置中的设备管理撤销。日志只输出账号序号和结果，不输出手机号、会话或回复原文。登录工具完成全部登录后才写出文件；中途失败需重新运行。
