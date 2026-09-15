import asyncio
import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from telethon import TelegramClient
from telethon.errors import FloodWaitError
from telethon.sessions import StringSession

BOT = 'sheeridverifier_bot'
TZ = ZoneInfo('Asia/Shanghai')
STATE = Path('telegram-state/state.json')


def succeeded(text):
    text = re.sub(r'\s+', '', text or '')
    return '出席率成功' in text and '今天已经签到了' not in text


async def account(index, session, api_id, api_hash, state, gate):
    async with gate:
        client = TelegramClient(StringSession(session), api_id, api_hash,
                                flood_sleep_threshold=0, request_retries=1,
                                connection_retries=2)
        key = None
        try:
            await client.connect()
            if not await client.is_user_authorized():
                raise ValueError('Session expired')
            me = await client.get_me()
            # Store only an irreversible account key, never phone/session data.
            import hashlib
            key = hashlib.sha256(str(me.id).encode()).hexdigest()
            now = datetime.now(TZ)
            day = now.date().isoformat()
            entry = state.setdefault(key, {})
            if entry.get('day') == day:
                return '今日已成功，跳过'
            if entry.get('retry_at', 0) > time.time():
                return '等待重试时间'
            bot = await client.get_entity(BOT)
            if not getattr(bot, 'bot', False):
                raise ValueError('Target is not a bot')
            last_sent = 0
            # Server history persists across Actions runs and includes mobile activity.
            async for msg in client.iter_messages(bot, limit=None):
                if msg.date.astimezone(TZ).date() != now.date():
                    break
                if not msg.out and succeeded(msg.raw_text):
                    entry['day'] = day
                    return '今日已有成功回复，跳过'
                if msg.out and (msg.raw_text or '').strip() == '/checkin':
                    last_sent = max(last_sent, msg.date.timestamp())
            if time.time() - last_sent < 3600:
                return '距上次签到不足1小时，跳过'
            sent = await client.send_message(bot, '/checkin')
            entry['retry_at'] = time.time() + 3600
            # Poll to handle both new replies and edits to a processing message.
            for _ in range(24):
                await asyncio.sleep(5)
                async for msg in client.iter_messages(bot, min_id=sent.id, limit=100):
                    if not msg.out and succeeded(msg.raw_text):
                        entry['day'] = msg.date.astimezone(TZ).date().isoformat()
                        return '签到成功'
            return '失败：未收到指定成功回复，下次重试'
        except FloodWaitError as exc:
            if key:
                state.setdefault(key, {})['retry_at'] = time.time() + max(3600, exc.seconds)
            return '失败：Telegram限流，等待后重试'
        except Exception as exc:
            # Exception messages can contain account data; log type only.
            return '失败：' + type(exc).__name__
        finally:
            await client.disconnect()


async def main():
    if os.getenv('GITHUB_EVENT_NAME') == 'schedule' and datetime.now(TZ).hour < 8:
        print('北京时间08:00前，不自动签到')
        return
    sessions = json.loads(os.environ['TG_SESSIONS'])
    if not isinstance(sessions, list) or not sessions or not all(isinstance(s, str) and s.strip() for s in sessions):
        raise ValueError('TG_SESSIONS must be a nonempty JSON list of session strings')
    if len(set(sessions)) != len(sessions):
        raise ValueError('Duplicate sessions')
    api_id, api_hash = int(os.environ['TG_API_ID']), os.environ['TG_API_HASH']
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    gate = asyncio.Semaphore(4)
    async def bounded(i, session):
        # Timeout includes queue time; 16 accounts normally finish in 9 minutes.
        try:
            return await asyncio.wait_for(account(i, session, api_id, api_hash, state, gate), 1800)
        except asyncio.TimeoutError:
            return '失败：执行超时'
    results = await asyncio.gather(*(bounded(i, s) for i, s in enumerate(sessions, 1)))
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state))
    lines = [f'账号{i}: {r}' for i, r in enumerate(results, 1)]
    print('\n'.join(lines))
    if os.getenv('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as f:
            f.write('\n'.join('- ' + line for line in lines) + '\n')
    if any(r.startswith('失败') for r in results):
        raise SystemExit(1)


if __name__ == '__main__':
    asyncio.run(main())
