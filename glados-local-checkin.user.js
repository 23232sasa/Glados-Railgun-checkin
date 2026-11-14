// ==UserScript==
// @name         GLaDOS 本地真实浏览器签到助手
// @namespace    https://github.com/23232sasa/Glados-Railgun-checkin
// @version      0.1.0
// @description  在本人已登录的真实 Chrome 中打开 GLaDOS 官方签到页，按北京时间点击签到；需要真人验证时保留交互，不伪造 Turnstile token。
// @match        https://glados.network/console/checkin*
// @match        https://glados.cloud/console/checkin*
// @match        https://glados.one/console/checkin*
// @run-at       document-idle
// @grant        none
// ==/UserScript==

/*
 * 与 GitHub-hosted Actions 的区别：
 *   - 使用用户自己的真实浏览器、已有的登录状态和本地网络；
 *   - 点击官方网页按钮，交由网页本身执行 Cloudflare 验证及签到请求；
 *   - 遇到互动型 Turnstile 时需要用户本人完成验证，不能自动绕过；
 *   - 不读取 Cookie，不把任何凭据或签到数据发送到第三方。
 *
 * 仅在网页标签页打开时运行。若想每天定时打开标签页，
 * 在 Windows 任务计划程序里每天 17:05 执行：
 *     powershell -NoProfile -Command "Start-Process 'https://glados.network/console/checkin'"
 * 每个 Chrome 用户配置文件只能处理当前已登录的 GLaDOS 账号。
 */

(() => {
  'use strict';

  const TIME_ZONE = 'Asia/Shanghai';
  const HOUR = 17;
  const MINUTE = 5;
  const POLL_INTERVAL_MS = 15000;
  const CANDIDATE_LABELS = [
    /^(每日)?签到$/i,
    /^立即签到$/i,
    /^签到(领取|得积分)?$/i,
    /^check[ -]?in( now| today)?$/i,
    /^daily check[ -]?in$/i,
    /^record (today'?s )?observation$/i,
    /^start observation$/i,
  ];

  const panel = document.createElement('div');
  panel.setAttribute('data-glados-local-checkin', 'true');
  panel.style.cssText = [
    'position:fixed','right:16px','bottom:16px','z-index:2147483647',
    'width:min(320px,calc(100vw - 32px))','box-sizing:border-box',
    'background:#17212f','color:#fff','border-radius:12px',
    'box-shadow:0 8px 28px rgba(0,0,0,.28)',
    'padding:12px','font:13px/1.5 system-ui,sans-serif',
  ].join(';');
  const heading = document.createElement('div');
  heading.textContent = 'GLaDOS 本地签到助手';
  heading.style.cssText = 'font-weight:700;margin-bottom:4px';
  const status = document.createElement('div');
  status.style.cssText = 'white-space:pre-wrap;margin-bottom:8px';
  const retry = document.createElement('button');
  retry.textContent = '手动重新查找并点击签到';
  retry.style.cssText = 'cursor:pointer;border:0;border-radius:6px;padding:6px 9px;background:#dceaff;color:#17212f';
  panel.append(heading,status,retry);
  (document.body || document.documentElement).appendChild(panel);

  const say = (message) => {
    status.textContent = message;
    console.log('[GLaDOS 本地签到助手]', message);
  };

  const getClock = () => {
    const parts = Intl.DateTimeFormat('en-US',{
      timeZone: TIME_ZONE, year:'numeric',month:'2-digit',day:'2-digit',
      hour:'2-digit',minute:'2-digit',hourCycle:'h23',
    }).formatToParts(new Date());
    const p = Object.fromEntries(parts.map(item => [item.type,item.value]));
    return {day:`${p.year}-${p.month}-${p.day}`, minuteOfDay:Number(p.hour)*60+Number(p.minute)};
  };

  const storageKey = () => `glados-local-assist:${location.hostname}:${getClock().day}`;

  const visible = (el) => {
    if (el.disabled || el.getAttribute('aria-disabled') === 'true') return false;
    const style = getComputedStyle(el);
    return style.display !== 'none' && style.visibility !== 'hidden'
      && el.getClientRects().length > 0;
  };

  const buttonLabel = (el) => (
    el.getAttribute('aria-label') ||
    el.getAttribute('title') ||
    el.value ||
    el.innerText ||
    el.textContent ||
    ''
  ).trim().replace(/\s+/g,' ');

  const findCheckinButton = () => {
    const candidates = document.querySelectorAll('button,[role="button"],input[type="button"],input[type="submit"]');
    return [...candidates].find(el =>
      visible(el) && CANDIDATE_LABELS.some(pattern=>pattern.test(buttonLabel(el)))
    );
  };

  let active = false;
  const attempt = (manual=false) => {
    if (active) return;
    const clock = getClock();
    if (!manual && clock.minuteOfDay < HOUR*60+MINUTE) {
      say('等待北京时间 17:05。请保持页面打开，或每天定时打开此标签页。');
      return;
    }
    if (!manual && localStorage.getItem(storageKey())) {
      say('今天已自动尝试过一次。请查看官方页面与积分流水；失败可按下方按钮重新尝试。');
      return;
    }
    const button = findCheckinButton();
    if (!button) {
      say('未发现可点击的官方签到按钮。可能已经签到、尚未登录，或网站改版。请在网页上检查。');
      return;
    }
    active = true;
    localStorage.setItem(storageKey(),new Date().toISOString());
    say('已找到官方签到按钮，正在点击。此动作不代表签到成功。');
    try {
      button.click();
      say('已点击官方签到按钮。若出现 Cloudflare 人机验证，请本人完成；随后检查积分流水。');
    } catch (err) {
      say('按钮点击失败：'+String(err?.message || err));
    } finally {
      active = false;
    }
  };

  retry.addEventListener('click',()=> {
    localStorage.removeItem(storageKey());
    attempt(true);
  });

  setTimeout(()=>attempt(false),2500);
  setInterval(()=>attempt(false),POLL_INTERVAL_MS);
})();
