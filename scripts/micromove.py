#!/usr/bin/env python3
"""MicroMove local reminder engine. Python 3.10+, no network or dependencies."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import sqlite3
import sys
from urllib.parse import urlsplit

DEFAULT = {'enabled': False, 'times': ['11:00', '16:00'], 'snooze_until': 0, 'url': ''}
MESSAGE = '这段忙完了吗？给自己充一点电，30 秒也可以。'


def data_dir():
    # Stable across plugin cache versions and both hosts; never inside a repository.
    return Path(os.environ.get('MICROMOVE_DATA_DIR', str(Path.home() / '.micromove'))).expanduser()


@contextmanager
def state():
    root = data_dir()
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    db = sqlite3.connect(root / 'state.sqlite3', timeout=0.2)
    try:
        db.execute('CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY, value TEXT)')
        db.execute('BEGIN IMMEDIATE')
        row = db.execute('SELECT value FROM state WHERE id=1').fetchone()
        value = json.loads(row[0]) if row else dict(DEFAULT)
        yield value
        db.execute('INSERT OR REPLACE INTO state VALUES (1, ?)', (json.dumps(value),))
        db.commit()
    finally:
        db.close()


def clock_time(value):
    try:
        t = datetime.strptime(value, '%H:%M')
        if t.strftime('%H:%M') != value:
            raise ValueError()
        return value
    except ValueError:
        raise argparse.ArgumentTypeError('时间格式应为 HH:MM，例如 11:00')


def minutes(value):
    try:
        n = int(value)
        if not 1 <= n <= 1440:
            raise ValueError()
        return n
    except ValueError:
        raise argparse.ArgumentTypeError('分钟数必须在 1–1440 之间')


def web_url(value):
    p = urlsplit(value)
    if p.scheme not in ('https', 'http') or not p.hostname or p.username or p.password:
        raise argparse.ArgumentTypeError('请输入不含登录凭据的 http(s) 网页地址')
    if p.scheme == 'http' and p.hostname not in ('localhost', '127.0.0.1', '::1'):
        raise argparse.ArgumentTypeError('远程页面必须使用 HTTPS')
    return value


def due(s, now):
    """At most one reminder per slot/day; missed slots expire after 30 minutes."""
    if not s['enabled']:
        return False
    timestamp = now.timestamp()
    if s['snooze_until']:
        if timestamp < s['snooze_until']:
            return False
        s['snooze_until'] = 0
        s['seen'] = [now.strftime('%Y-%m-%d') + '/' + t for t in s['times']
                     if t <= now.strftime('%H:%M')]
        return True
    day = now.strftime('%Y-%m-%d')
    seen = [k for k in s.get('seen', []) if k.startswith(day + '/')]
    s['seen'] = seen
    for t in s['times']:
        hour, minute = map(int, t.split(':'))
        slot = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        key = day + '/' + t
        if 0 <= (now - slot).total_seconds() < 1800 and key not in seen:
            seen.append(key)
            return True
    return False


def reminder(s):
    return {'title': 'MicroMove · 回个电', 'message': MESSAGE,
            'actions': ['现在动一下', '10 分钟后提醒'], 'url': s['url'] or None}


def run_hook():
    try:
        # Discard conversation fields; bounded input is never persisted.
        event = json.loads(sys.stdin.read(65537))
        if not isinstance(event, dict) or event.get('stop_hook_active'):
            return {}
        if event.get('hook_event_name') not in ('SessionStart', 'Stop'):
            return {}
        with state() as s:
            if due(s, datetime.now().astimezone()):
                return {'systemMessage': MESSAGE + ' MicroMove：回复“现在动一下”或“10 分钟后提醒”。'}
    except (ValueError, OSError, sqlite3.Error, KeyError, TypeError):
        # A wellness reminder must never break the coding workflow.
        pass
    return {}


def main():
    # Hooks communicate over UTF-8 pipes, including on legacy Windows locales.
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    p = argparse.ArgumentParser(description=__doc__)
    commands = p.add_subparsers(dest='command', required=True)
    for name in ('status', 'enable', 'pause', 'check', 'demo', 'start', 'done', 'hook'):
        commands.add_parser(name)
    snooze = commands.add_parser('snooze')
    snooze.add_argument('minutes', type=minutes, nargs='?', default=10)
    config = commands.add_parser('configure')
    config.add_argument('--times', nargs='+', type=clock_time)
    config.add_argument('--url', type=web_url)
    args = p.parse_args()
    if args.command == 'hook':
        print(json.dumps(run_hook(), ensure_ascii=False))
        return
    try:
        with state() as s:
            now = datetime.now().astimezone()
            if args.command == 'enable':
                s['enabled'] = True
            elif args.command == 'pause':
                s['enabled'] = False
                s['snooze_until'] = 0
            elif args.command == 'configure':
                if args.times is not None:
                    s['times'] = sorted(set(args.times))
                if args.url is not None:
                    s['url'] = args.url
            elif args.command == 'snooze':
                if not s['enabled']:
                    raise ValueError('提醒已暂停，请先 enable；稍后提醒不会偷偷重新开启。')
                s['snooze_until'] = (now + timedelta(minutes=args.minutes)).timestamp()
            elif args.command == 'done':
                s['snooze_until'] = 0
                s['seen'] = [now.strftime('%Y-%m-%d') + '/' + t for t in s['times']
                             if t <= now.strftime('%H:%M')]
            if args.command == 'check':
                result = reminder(s) if due(s, now) else {'due': False}
            elif args.command in ('demo', 'start'):
                result = reminder(s)
                if not s['url']:
                    result['note'] = '尚未配置团队跟练网页；本原型不生成动作处方。'
            else:
                result = {**s, 'timezone': str(now.tzinfo), 'delivery': 'event-driven',
                          'note': '仅在 SessionStart / Stop 或 check 时检查，不是后台闹钟。'}
            print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, sqlite3.Error) as e:
        p.exit(1, f'MicroMove: {e}\n')


if __name__ == '__main__':
    main()
