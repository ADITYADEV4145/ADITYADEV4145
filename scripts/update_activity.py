"""Refresh the README's seven-day ASCII commit-activity graph."""
import argparse
from datetime import datetime, timedelta, timezone
import json
import math
import os
from pathlib import Path
import re
from urllib.request import Request, urlopen

START = '<!-- START_SECTION:ascii_graph -->'
END = '<!-- END_SECTION:ascii_graph -->'
QUERY = '''query($from:DateTime!, $to:DateTime!) {
  user(login:"ADITYADEV4145") {
    contributionsCollection(from:$from, to:$to) {
      commitContributionsByRepository(maxRepositories:100) {
        contributions(first:100) {
          nodes { occurredAt commitCount }
          pageInfo { hasNextPage }
        }
      }
    }
  }
}'''


def fetch(now):
    start = (now-timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
    body = {'query': QUERY, 'variables': {'from': start.isoformat(), 'to': now.isoformat()}}
    request = Request('https://api.github.com/graphql', data=json.dumps(body).encode(),
                      headers={'Authorization': f'Bearer {os.environ["GH_TOKEN"]}',
                               'Content-Type': 'application/json',
                               'User-Agent': 'ADITYADEV4145-profile'})
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def daily_counts(payload, today):
    if payload.get('errors'):
        raise ValueError('GitHub returned errors; keeping the previous graph.')
    dates = [today-timedelta(days=6-i) for i in range(7)]
    counts = dict.fromkeys(dates, 0)
    repositories = payload['data']['user']['contributionsCollection']['commitContributionsByRepository']
    if len(repositories) >= 100:
        raise ValueError('Repository limit reached; refusing to publish incomplete totals.')
    for repository in repositories:
        data = repository['contributions']
        if data['pageInfo']['hasNextPage']:
            raise ValueError('Contribution results are incomplete.')
        for node in data['nodes']:
            day = datetime.fromisoformat(node['occurredAt'].replace('Z', '+00:00')).astimezone(timezone.utc).date()
            value = node['commitCount']
            if not isinstance(value, int) or value < 0:
                raise ValueError('Invalid commit count.')
            if day in counts:
                counts[day] += value
    return list(counts.values())


def graph(counts):
    cumulative = [0]
    for count in counts:
        cumulative.append(cumulative[-1]+count)
    height, width = max(3, min(10, cumulative[-1])), 70
    tick = max(1, math.ceil(cumulative[-1]/height))
    maximum = tick*height
    rows = []
    for x in range(width+1):
        day = min(6, x//10)
        fraction = (x-day*10)/10
        value = cumulative[day] + (cumulative[day+1]-cumulative[day])*fraction
        rows.append(height-round(value/maximum*height))
    cells = {}
    def edge(a, b):
        ax, ay = a
        bx, by = b
        da, db = ('R', 'L') if bx>ax else ('D', 'U') if by>ay else ('U', 'D')
        cells.setdefault(a, set()).add(da)
        cells.setdefault(b, set()).add(db)
    for x in range(1, width+1):
        previous, current = rows[x-1], rows[x]
        edge((x-1, previous), (x, previous))
        if current != previous:
            step = 1 if current>previous else -1
            for y in range(previous, current, step):
                edge((x, y), (x, y+step))
    glyphs = {frozenset(k):v for k,v in [
        ('LR','─'), ('UD','│'), ('LU','╯'), ('DR','╭'), ('LD','╮'), ('UR','╰'),
        ('L','─'), ('R','─'), ('U','│'), ('D','│')]}
    lines = []
    for y in range(height+1):
        label = (height-y)*tick
        plot = ''.join(glyphs.get(frozenset(cells.get((x,y), set())), ' ') for x in range(width+1))
        lines.append(f'{label:5d} commits ┤{plot}'.rstrip())
    prefix = '              '
    lines.append(prefix+'┼'+('─'*9+'┬')*6+'─'*9+'┤')
    labels = [' ']*(width+1)
    for i, label in enumerate(['-7d','-6d','-5d','-4d','-3d','-2d','-1d','now']):
        start = min(width-len(label)+1, max(0, i*10-len(label)//2))
        labels[start:start+len(label)] = label
    lines.append(prefix+''.join(labels).rstrip())
    return '\n'.join(lines)


def update(content, plot):
    if content.count(START)!=1 or content.count(END)!=1:
        raise ValueError('Expected exactly one ASCII graph section.')
    pattern = re.escape(START)+r'.*?'+re.escape(END)
    if not re.search(pattern, content, re.DOTALL):
        raise ValueError('ASCII graph markers are out of order.')
    return re.sub(pattern, lambda _: f'{START}\n\n```text\n{plot}\n```\n\n{END}', content, flags=re.DOTALL)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path)
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    payload = json.loads(args.input.read_text()) if args.input else fetch(now)
    counts = daily_counts(payload, now.date())
    path = Path(__file__).resolve().parents[1] / 'README.md'
    result = update(path.read_text(encoding='utf-8'), graph(counts))
    path.write_text(result, encoding='utf-8')
    print(f'Updated seven-day ASCII graph: {sum(counts)} GitHub commit contributions.')
