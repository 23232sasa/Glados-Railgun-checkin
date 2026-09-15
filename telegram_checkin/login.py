"""Run only on your own computer, never in Actions."""
import asyncio
import getpass
import json
import os
from pathlib import Path
from telethon import TelegramClient
from telethon.sessions import StringSession


async def main():
    api_id = int(input('Telegram API ID: ').strip())
    api_hash = getpass.getpass('Telegram API hash: ').strip()
    count = int(input('账号数量（例如16）: '))
    if count < 1:
        raise ValueError('至少一个账号')
    target = Path.home() / 'telegram-sessions-private.json'
    if target.exists():
        raise ValueError('请先安全保存或移走已有的 telegram-sessions-private.json')
    sessions, ids = [], set()
    for i in range(count):
        print(f'登录账号 {i + 1}/{count}')
        client = TelegramClient(StringSession(), api_id, api_hash)
        try:
            await client.start(phone=lambda: input('手机号（带国家区号）: '),
                               password=lambda: getpass.getpass('两步验证密码: '),
                               code_callback=lambda: getpass.getpass('验证码: '))
            me = await client.get_me()
            if me.id in ids:
                raise ValueError('重复登录了同一个账号')
            ids.add(me.id)
            sessions.append(client.session.save())
        finally:
            await client.disconnect()
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as f:
        json.dump(sessions, f)
    print(f'登录完成。将此文件内容存入 GitHub Secret TG_SESSIONS：{target}')
    print('不要上传此文件到仓库或发送到聊天。另保存 TG_API_ID 和 TG_API_HASH。')


if __name__ == '__main__':
    asyncio.run(main())
