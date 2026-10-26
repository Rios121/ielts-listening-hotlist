#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 listening_data.json 转成 LLM 总结的中间输入：WD/input/batch_01..08.md（每批 10 篇）。"""
import argparse, json, os

TYPE_LABEL = {
    'fill-in-the-blank': '填空',
    'single-choice': '单选',
    'multiple-choice': '多选',
    'matching': '匹配',
    'map': '地图/标注',
}


def trim(s, n=300):
    s = (s or '').strip()
    return s if len(s) <= n else s[:n] + ' …'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", default=".", help="工作目录（含 listening_data.json）")
    args = ap.parse_args()
    wd = args.workdir
    d = json.load(open(os.path.join(wd, "listening_data.json"), encoding="utf-8"))
    out_dir = os.path.join(wd, "input")
    os.makedirs(out_dir, exist_ok=True)

    batches = []
    for slot in ['Part 1', 'Part 2', 'Part 3', 'Part 4']:
        recs = [r for r in d['records'] if r['slot'] == slot and not r.get('_failed')]
        for i in range(0, len(recs), 10):
            batches.append((slot, recs[i:i + 10]))

    for bi, (slot, chunk) in enumerate(batches, 1):
        lines = []
        for r in chunk:
            lines.append('\n\n' + '=' * 60)
            lines.append(f"【{slot} #{r['rank']}】 {r['title']}"
                         + (f"（{r['titleZh']}）" if r.get('titleZh') else ''))
            if r.get('subtitle'):
                lines.append('副标题: ' + trim(r['subtitle'], 200))
            segs = r.get('transcript_segments', [])
            lines.append(f'--- 录音原文 transcript（{len(segs)} 段）---')
            for idx, s in enumerate(segs):
                lines.append(f'[{idx}] {trim(s, 400)}')
            notes = r.get('notes', [])
            if notes:
                lines.append('--- 笔记题干（填空题，空格用【题号】标出）---')
                for n in notes:
                    lines.append('• ' + trim(n, 200))
            lines.append('--- 题目与解析 ---')
            for q in r['questions']:
                lines.append('')
                tlabel = TYPE_LABEL.get(q['type'], q['type'])
                stem = q['question'] or q.get('groupDesc') or ''
                lines.append(f"Q{q['qNumber']} [{tlabel}] " + trim(stem, 150))
                if q.get('options'):
                    lines.append('  选项: ' + ' | '.join(
                        f"{o['num']}. {trim(o['text'], 50)}" for o in q['options']))
                for a in q['analyses']:
                    lab = a['label'] or '解析'
                    lines.append(f'  [{lab}] {trim(a["content"], 400)}')
        fn = os.path.join(out_dir, f'batch_{bi:02d}.md')
        with open(fn, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        print(f'{slot} -> {fn} ({os.path.getsize(fn) // 1024} KB)')


if __name__ == "__main__":
    main()
