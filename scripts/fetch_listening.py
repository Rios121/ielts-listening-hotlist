#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓取雅思机考平台七天热榜听力题库（Part 1/2/3/4 各 20 篇）+ 录音原文 + 笔记题干 + 答案解析。

默认使用内置数据源，开箱即用；也可用 --base 或环境变量 IELTS_HOTLIST_API 覆盖。

输出 WD/listening_data.json，结构：
{"records":[{rank, slot, title, titleZh, transcript_segments, notes, totalQuestions, questions:[...]}],
 "fail":[...]}
"""
import argparse, json, os, re, sys, time, urllib.request, urllib.error, html

BASE = "https://www.9fnnn.com/api"  # 默认数据源，可用 --base 覆盖


def http_get(path, token=None, timeout=45):
    req = urllib.request.Request(BASE + path, headers={
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
    })
    if token:
        req.add_header("token", token)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"_error": e.code, "_body": e.read().decode("utf-8", "replace")[:300]}
    except Exception as e:
        return {"_error": str(e)}


def _grep_token(ls_dir):
    pat = re.compile(r'["\']token["\']\s*[:=]\s*["\']([A-Za-z0-9_\-\.]{10,})["\']')
    for root, _dirs, files in os.walk(ls_dir):
        for fn in files:
            if not (fn.endswith(".log") or fn.endswith(".ldb")):
                continue
            try:
                with open(os.path.join(root, fn), "rb") as f:
                    data = f.read()
            except Exception:
                continue
            try:
                text = data.decode("utf-8", "ignore")
            except Exception:
                text = ""
            m = pat.search(text)
            if m:
                return m.group(1)
    return None


def find_token_from_localstorage():
    appdata = os.environ.get("APPDATA") or os.environ.get("LOCALAPPDATA") or ""
    if not appdata or not os.path.isdir(appdata):
        return None
    for name in os.listdir(appdata):
        full = os.path.join(appdata, name)
        if not os.path.isdir(full):
            continue
        ls = os.path.join(full, "Local Storage")
        if not os.path.isdir(ls):
            continue
        token = _grep_token(ls)
        if token:
            return token
    return None


def transcript_segments(part):
    """提取录音原文，返回每句/每段文本列表。"""
    aj = part.get("articleJson") or part.get("article") or ""
    if isinstance(aj, str):
        try:
            aj = json.loads(aj)
        except Exception:
            return [aj] if aj else []
    if isinstance(aj, dict):
        segs = aj.get("segments", [])
        if segs and isinstance(segs[0], dict) and "text" in segs[0]:
            return [s.get("text", "").strip() for s in segs if s.get("text", "").strip()]
        out = []
        for seg in segs:
            for s in seg.get("sentences", []):
                t = s.get("text", "").strip()
                if t:
                    out.append(t)
        return out
    return []


def extract_notes(contentHtml):
    """从填空题笔记的 contentHtml 提取笔记正文，空格用【题号】标出。"""
    if not contentHtml:
        return []
    text = re.sub(r'<input[^>]*placeholder="(\d+)"[^>]*>', r'【\1】', contentHtml)
    rows = re.findall(r'<td[^>]*>(.*?)</td>', text, re.S)
    out = []
    for r in rows:
        r = re.sub(r'<[^>]+>', '', r)
        r = html.unescape(r).strip()
        if r and r not in ('↓',):
            out.append(r)
    return out


def build_questions(part):
    qs = []
    for g in part.get("groups", []):
        for q in g.get("questions", []):
            opts = []
            for o in q.get("options", []):
                opts.append({"num": o.get("optionNum"),
                             "text": o.get("option") or o.get("optionContent")})
            analyses = []
            for an in q.get("analyses", []):
                analyses.append({"label": an.get("labelsOne"), "content": an.get("content")})
            qs.append({
                "qNumber": q.get("qNumber"),
                "type": q.get("type"),
                "question": q.get("question"),
                "groupDesc": g.get("description"),
                "options": opts,
                "analyses": analyses,
            })
    return qs


def main():
    global BASE
    ap = argparse.ArgumentParser(description="抓取雅思听力热榜")
    ap.add_argument("--workdir", default=".", help="工作目录（默认当前目录）")
    ap.add_argument("--base", default=None, help="API 基址（可选，默认内置）")
    args = ap.parse_args()
    BASE = (args.base or os.environ.get("IELTS_HOTLIST_API") or BASE).rstrip("/")

    wd = args.workdir
    os.makedirs(wd, exist_ok=True)

    token = None
    albums = http_get("/practice/v1/high-frequency/albums")
    if "_error" in albums or not albums.get("data") or not albums["data"].get("list"):
        print("[fetch] 热榜接口异常，尝试探测本地 token 重试…")
        token = find_token_from_localstorage()
        if token:
            albums = http_get("/practice/v1/high-frequency/albums", token=token)
        else:
            print("[fetch] 未找到本地 token，放弃。请确认已安装并登录该平台 App。")
            sys.exit(1)

    data_list = albums.get("data", {}).get("list", [])
    rows = []
    for a in data_list:
        if a.get("channel") != "listening":
            continue
        for s in a.get("slots", []):
            for r in s.get("list", []):
                rr = dict(r)
                rr["slotLabel"] = s.get("label")
                rows.append(rr)
    print(f"[fetch] 听力热榜共 {len(rows)} 篇")

    records, fail = [], []
    for i, r in enumerate(rows, 1):
        uid = r.get("id")
        exam = http_get(f"/practice/v1/units/{uid}/exam", token=token)
        if "_error" in exam or exam.get("code") != "200" or not exam.get("data"):
            fail.append((r.get("rank"), r.get("slotLabel"), r.get("title"),
                         exam.get("_error") or exam.get("code")))
            records.append({"rank": r.get("rank"), "slot": r.get("slotLabel"),
                            "title": r.get("title"), "_failed": True})
            print(f"[{i}/{len(rows)}] FAIL {r.get('slotLabel')} #{r.get('rank')} {r.get('title')}")
            continue
        data = exam["data"]
        part = (data.get("parts") or [{}])[0]
        notes = []
        for g in part.get("groups", []):
            notes += extract_notes(g.get("contentHtml"))
        records.append({
            "rank": r.get("rank"),
            "slot": r.get("slotLabel"),
            "title": r.get("title"),
            "titleZh": r.get("titleZh"),
            "subtitle": part.get("subtitle") or r.get("subtitle"),
            "totalQuestions": part.get("total"),
            "transcript_segments": transcript_segments(part),
            "notes": notes,
            "questions": build_questions(part),
        })
        print(f"[{i}/{len(rows)}] OK {r.get('slotLabel')} #{r.get('rank')} {r.get('title')}")
        time.sleep(0.15)

    out = os.path.join(wd, "listening_data.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"records": records, "fail": fail}, f, ensure_ascii=False, indent=1)
    print(f"[fetch] 完成，失败 {len(fail)} 篇，已写入 {out}")


if __name__ == "__main__":
    main()
