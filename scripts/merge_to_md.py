#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合并 summaries/batch_XX.md 成最终 markdown，目录做成可点击跳转的锚点链接。"""
import argparse, json, os, re, datetime

PART_OF_SLOT = {'Part 1': 1, 'Part 2': 2, 'Part 3': 3, 'Part 4': 4}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", default=".", help="工作目录（含 listening_data.json 与 summaries/）")
    args = ap.parse_args()
    wd = args.workdir
    data = json.load(open(os.path.join(wd, "listening_data.json"), encoding="utf-8"))
    sum_dir = os.path.join(wd, "summaries")

    today = datetime.date.today().strftime("%Y-%m-%d")
    out_path = os.path.join(wd, f"听力7天热榜_备考速查_{today}.md")

    header = []
    header.append("# 雅思听力 · 7 天热榜备考速查")
    header.append("")
    header.append(f"> 数据来源：雅思机考平台「一周高频榜单」听力榜 · 生成日期 {today}")
    header.append("> 覆盖 Part 1 / Part 2 / Part 3 / Part 4 各 20 篇（共 80 篇），目录点击可跳转。")
    header.append("> 用法：P1 看答案词；P2/P3 记信号词+坑；P4 对照题干精听原句。")
    header.append("")
    header.append("## 目录")
    header.append("")
    for slot in ['Part 1', 'Part 2', 'Part 3', 'Part 4']:
        pn = PART_OF_SLOT[slot]
        header.append(f"### {slot}")
        recs = [r for r in data['records'] if r['slot'] == slot and not r.get('_failed')]
        for r in recs:
            rank = r['rank']
            zh = r.get('titleZh') or ''
            anchor = f"p{pn}-{rank}"
            label = f"P{pn} #{rank} {r['title']}" + (f"（{zh}）" if zh else "")
            header.append(f"- [{label}](#{anchor})")
        header.append("")
    header.append("---")
    header.append("")

    title_re = re.compile(r'^###\s+\[P(\d)\s+#(\d+)\]')

    def insert_anchors(text):
        out_lines = []
        for line in text.splitlines():
            m = title_re.match(line.strip())
            if m:
                pn, rank = int(m.group(1)), int(m.group(2))
                out_lines.append(f'<a id="p{pn}-{rank}"></a>')
            out_lines.append(line)
        return "\n".join(out_lines)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(header))
        for slot, (a, b) in zip(['Part 1', 'Part 2', 'Part 3', 'Part 4'],
                                [('01', '02'), ('03', '04'), ('05', '06'), ('07', '08')]):
            f.write(f"# {slot}\n\n")
            for bn in (a, b):
                fn = os.path.join(sum_dir, f"batch_{bn}.md")
                if not os.path.exists(fn):
                    print(f"[merge] 缺少 {fn}，跳过")
                    continue
                text = open(fn, encoding="utf-8").read().rstrip()
                f.write(insert_anchors(text) + "\n\n")

    print(f"[merge] 已生成 {out_path} ({os.path.getsize(out_path) // 1024} KB)")


if __name__ == "__main__":
    main()
