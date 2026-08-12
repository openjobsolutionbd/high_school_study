#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
book_tools.py — জেনেরিক বই-আর্কাইভ টুল (যেকোনো সাবজেক্টে ব্যবহারযোগ্য)

এই স্ক্রিপ্টে কোনো সাবজেক্ট-নির্দিষ্ট তথ্য (চ্যাপ্টার নাম, পেজ রেঞ্জ, ফাইলনেম প্যাটার্ন)
হার্ডকোড করা নেই। সবকিছু পাশে থাকা book-config.json থেকে পড়া হয়। তাই একই স্ক্রিপ্ট
ICT, Math, Science, Social, English — যেকোনো সাবজেক্টে কাজ করবে, শুধু config.json
বদলালেই হবে।

ব্যবহার (images/ ফোল্ডারের ভেতর থেকে চালান, যেখানে book-config.json আছে):

    python3 book_tools.py list
    python3 book_tools.py page 25
    python3 book_tools.py page 37 52
    python3 book_tools.py chapter 3
    python3 book_tools.py search "শব্দ/বাক্যাংশ"
    python3 book_tools.py search "শব্দ/বাক্যাংশ" --fuzzy

কনফিগ ফাইলের path আলাদা হলে:
    python3 book_tools.py --config /path/to/book-config.json chapter 3

আউটপুট ডিফল্টভাবে ./extracted/ ফোল্ডারে জমা হয়।
"""

import argparse
import difflib
import json
import re
import sys
import zipfile
from pathlib import Path


# ---------------------------------------------------------------------------
# কনফিগ লোড ও হেল্পার
# ---------------------------------------------------------------------------

def load_config(path: Path) -> dict:
    if not path.exists():
        print(f"Error: কনফিগ ফাইল পাওয়া যায়নি: {path}")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def chapter_by_num(config: dict, num: int):
    for ch in config["chapters"]:
        if ch["num"] == num:
            return ch
    return None


def image_filename(config: dict, book_page: int) -> str:
    image_page = book_page + config["image_offset"]
    return f'{config["image_prefix"]}{image_page:04d}.jpg'


# ---------------------------------------------------------------------------
# পেজ এক্সট্র্যাকশন
# ---------------------------------------------------------------------------

def extract_page(config: dict, base_dir: Path, book_page: int, out_dir: Path) -> bool:
    zip_path = base_dir / config["zip_file"]
    if not zip_path.exists():
        print(f"Error: zip ফাইল পাওয়া যায়নি: {zip_path}")
        sys.exit(1)

    fname = image_filename(config, book_page)
    out_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path) as zf:
        name_map = {Path(n).name: n for n in zf.namelist()}
        if fname not in name_map:
            print(f"বই পৃষ্ঠা {book_page:>3}  →  {fname}  [পাওয়া যায়নি]")
            return False
        data = zf.read(name_map[fname])
        (out_dir / fname).write_bytes(data)
        print(f"বই পৃষ্ঠা {book_page:>3}  →  {fname}  (extracted)")
        return True


def extract_range(config: dict, base_dir: Path, start: int, end: int, out_dir: Path):
    for p in range(start, end + 1):
        extract_page(config, base_dir, p, out_dir)


def cmd_chapter(config: dict, base_dir: Path, num: int, out_dir: Path):
    ch = chapter_by_num(config, num)
    if not ch:
        valid = ", ".join(str(c["num"]) for c in config["chapters"])
        print(f"Error: অধ্যায় {num} কনফিগে নেই। সঠিক নম্বর: {valid}")
        sys.exit(1)
    print(f'অধ্যায় {num} ({ch["title"]}) → বই পৃষ্ঠা {ch["start"]}–{ch["end"]} বের করা হচ্ছে...')
    extract_range(config, base_dir, ch["start"], ch["end"], out_dir)


def cmd_list(config: dict):
    print(f'{config.get("subject_name", "(নাম নেই)")}')
    for ch in sorted(config["chapters"], key=lambda c: c["num"]):
        pages = ch["end"] - ch["start"] + 1
        print(f'  অধ্যায় {ch["num"]}: {ch["title"]}  '
              f'(বই পৃষ্ঠা {ch["start"]}–{ch["end"]}, {pages} পৃষ্ঠা)')


# ---------------------------------------------------------------------------
# সার্চ (নির্ভুল ম্যাচ + ঐচ্ছিক ফাজি ম্যাচ)
# ---------------------------------------------------------------------------

def normalize_bengali(text: str) -> str:
    """তুলনার আগে zero-width joiner/non-joiner ও অতিরিক্ত স্পেস বাদ দেয়,
    যাতে ইউনিকোড রেন্ডারিং ভ্যারিয়েশনের কারণে মিল miss না হয়।"""
    text = re.sub(r"[\u200c\u200d]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def find_chapter_markdown(config: dict, md_dir: Path, chapter_num: int) -> Path | None:
    pattern = config["chapter_file_pattern"].format(chapter_num)
    matches = sorted(md_dir.glob(pattern))
    return matches[0] if matches else None


def cmd_search(config: dict, base_dir: Path, term: str, out_dir: Path, fuzzy: bool):
    md_dir = base_dir / config["markdown_dir"]
    if not md_dir.exists():
        print(f"Error: markdown ফোল্ডার পাওয়া যায়নি: {md_dir}")
        sys.exit(1)

    norm_term = normalize_bengali(term)
    found_any = False

    for ch in sorted(config["chapters"], key=lambda c: c["num"]):
        file = find_chapter_markdown(config, md_dir, ch["num"])
        if file is None:
            continue

        lines = file.read_text(encoding="utf-8").splitlines()
        total = len(lines)
        if total == 0:
            continue

        hit_line = None
        match_pct = None

        # ধাপ ১: নির্ভুল (normalized substring) ম্যাচ
        for i, line in enumerate(lines, start=1):
            if norm_term in normalize_bengali(line):
                hit_line = i
                match_pct = 100.0
                break

        # ধাপ ২: --fuzzy দিলে, নির্ভুল মিল না পেলে সবচেয়ে কাছের লাইন খোঁজে
        if hit_line is None and fuzzy:
            best_ratio = 0.0
            for i, line in enumerate(lines, start=1):
                norm_line = normalize_bengali(line)
                if not norm_line:
                    continue
                ratio = difflib.SequenceMatcher(None, norm_term, norm_line).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    hit_line = i
            if best_ratio < 0.35:      # খুব দুর্বল মিল হলে বাদ দেওয়া হয়
                hit_line = None
            else:
                match_pct = best_ratio * 100

        if hit_line is None:
            continue

        found_any = True
        position_ratio = hit_line / total
        span = ch["end"] - ch["start"]
        est_page = ch["start"] + round(position_ratio * span)
        est_page = max(ch["start"], min(ch["end"], est_page))

        tag = f", মিল ~{match_pct:.0f}%" if fuzzy else ""
        print(f'খুঁজে পাওয়া গেছে: {file.name}  '
              f'(লাইন {hit_line}/{total}, ~{position_ratio*100:.0f}% জায়গায়{tag})')
        print(f'আনুমানিক বই পৃষ্ঠা: {est_page}  '
              f'(অধ্যায় {ch["num"]} — {ch["title"]}, রেঞ্জ {ch["start"]}–{ch["end"]})')

        win_start = max(ch["start"], est_page - 1)
        win_end = min(ch["end"], est_page + 1)
        print(f'সম্ভাব্য পৃষ্ঠা বের করা হচ্ছে ({win_start}–{win_end})... '
              f'[আনুমানিক হিসেব, নিশ্চিত করতে পাশের পৃষ্ঠাও দেখুন]')
        extract_range(config, base_dir, win_start, win_end, out_dir)
        print("---")

    if not found_any:
        hint = "  (--fuzzy যোগ করে আবার চেষ্টা করুন, বানান ভিন্ন হতে পারে)" if not fuzzy else ""
        print(f'কোনো চ্যাপ্টারে "{term}" খুঁজে পাওয়া যায়নি।{hint}')


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="যেকোনো সাবজেক্টের বই-আর্কাইভ থেকে নির্দিষ্ট পৃষ্ঠা বের করার জেনেরিক টুল"
    )
    parser.add_argument("--config", default="book-config.json", help="কনফিগ ফাইলের পাথ")
    parser.add_argument("--out", default="extracted", help="আউটপুট ফোল্ডারের নাম")
    sub = parser.add_subparsers(dest="command", required=True)

    p_page = sub.add_parser("page", help="একটা পৃষ্ঠা বা রেঞ্জ বের করে")
    p_page.add_argument("start", type=int)
    p_page.add_argument("end", type=int, nargs="?", default=None)

    p_chapter = sub.add_parser("chapter", help="পুরো একটা অধ্যায় বের করে")
    p_chapter.add_argument("num", type=int)

    p_search = sub.add_parser("search", help="markdown-এ শব্দ খুঁজে আনুমানিক পৃষ্ঠা বের করে")
    p_search.add_argument("term")
    p_search.add_argument("--fuzzy", action="store_true",
                           help="বানান/OCR ভুল সহনশীল খোঁজ (নির্ভুল মিল না পেলে ব্যবহার হয়)")

    sub.add_parser("list", help="সব অধ্যায়ের নাম ও পৃষ্ঠা রেঞ্জ দেখায়")

    args = parser.parse_args()
    config_path = Path(args.config)
    config = load_config(config_path)
    base_dir = config_path.parent if str(config_path.parent) != "" else Path(".")
    out_dir = base_dir / args.out

    if args.command == "page":
        if args.end is not None:
            extract_range(config, base_dir, args.start, args.end, out_dir)
        else:
            extract_page(config, base_dir, args.start, out_dir)
    elif args.command == "chapter":
        cmd_chapter(config, base_dir, args.num, out_dir)
    elif args.command == "search":
        cmd_search(config, base_dir, args.term, out_dir, fuzzy=args.fuzzy)
    elif args.command == "list":
        cmd_list(config)


if __name__ == "__main__":
    main()
