#!/usr/bin/env python3
import os
import sys
import argparse
from collections import Counter

RESET = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
RED = "\033[31m"

COLOR_CYCLE = [CYAN, GREEN, YELLOW, BLUE, MAGENTA, RED]

def parse_formatted_file(file_path):
    tag_counts = Counter()
    tag_chars = Counter()
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line_str = line.strip()
            if not line_str:
                continue
            segments = line_str.split('|')
            for seg in segments:
                if not seg:
                    continue
                if '@' in seg:
                    text, tag = seg.rsplit('@', 1)
                    tag_counts[tag] += 1
                    tag_chars[tag] += len(text)
                else:
                    tag_counts['O'] += 1
                    tag_chars['O'] += len(seg)
    return tag_counts, tag_chars

def main():
    parser = argparse.ArgumentParser(
        description="Visualize entity tag distribution of formatted text files."
    )
    parser.add_argument("-i", "--input", required=True, help="Input formatted file or directory")
    parser.add_argument("--exclude-o", action="store_true", help="Exclude the 'O' tag")
    parser.add_argument("--width", type=int, default=40, help="Bar chart width")
    parser.add_argument("--csv", help="Path to export the tag distribution as a CSV file")
    args = parser.parse_args()

    input_path = args.input
    if not os.path.exists(input_path):
        print(f"{RED}{BOLD}Error: Input path '{input_path}' does not exist.{RESET}", file=sys.stderr)
        sys.exit(1)

    formatted_files = []
    if os.path.isdir(input_path):
        for root, _, files in os.walk(input_path):
            for file in files:
                if file.endswith('.txt') and not file.endswith('_raw.txt'):
                    formatted_files.append(os.path.join(root, file))
    else:
        formatted_files.append(input_path)

    if not formatted_files:
        print(f"{YELLOW}Warning: No formatted files found.{RESET}")
        sys.exit(0)

    total_counts = Counter()
    total_chars = Counter()
    for file_path in formatted_files:
        try:
            file_counts, file_chars = parse_formatted_file(file_path)
            total_counts.update(file_counts)
            total_chars.update(file_chars)
        except Exception as e:
            print(f"{RED}Failed to parse '{file_path}': {e}{RESET}", file=sys.stderr)

    if not total_counts:
        print(f"{RED}{BOLD}No tag instances found.{RESET}")
        sys.exit(0)

    o_count = total_counts.get('O', 0)
    display_counts = total_counts.copy()
    display_chars = total_chars.copy()

    if args.exclude_o:
        if 'O' in display_counts:
            del display_counts['O']
        if 'O' in display_chars:
            del display_chars['O']

    if not display_counts:
        print(f"{YELLOW}All segments are 'O' tags, and --exclude-o was requested.{RESET}")
        sys.exit(0)

    total_segments = sum(total_counts.values())
    total_display_segments = sum(display_counts.values())
    total_display_chars = sum(display_chars.values())

    print("\n" + "=" * 80)
    print(f" {BOLD}{UNDERLINE}CNER TAG DISTRIBUTION REPORT{RESET}")
    print("=" * 80)
    print(f"  📂 Files Scanned: {len(formatted_files)}")
    print(f"  📊 Total Segments: {total_segments:,}")
    if args.exclude_o:
        print(f"  🚫 O-Tag Filter:   {BOLD}Enabled{RESET} (Filtered out {o_count:,} segments, displaying remaining {total_display_segments:,})")
    else:
        print(f"  🚫 O-Tag Filter:   {BOLD}Disabled{RESET}")
    print("=" * 80 + "\n")

    print(f"{BOLD}{'Tag Name':20s} | {'Count (Seg)':12s} | {'% of Disp':10s} | {'Total Chars':12s} | {'Avg Char/Seg':12s}{RESET}")
    print("-" * 80)

    sorted_tags = sorted(display_counts.items(), key=lambda x: x[1], reverse=True)
    for i, (tag, count) in enumerate(sorted_tags):
        pct = (count / total_display_segments) * 100 if total_display_segments > 0 else 0
        chars = display_chars[tag]
        avg_len = chars / count if count > 0 else 0
        color = COLOR_CYCLE[i % len(COLOR_CYCLE)]
        print(f"{color}{tag:20s}{RESET} | {count:12,d} | {pct:8.2f}% | {chars:12,d} | {avg_len:12.1f}")

    print("-" * 80)
    print(f"{BOLD}{'TOTAL DISPLAYED':20s} | {total_display_segments:12,d} | 100.00%     | {total_display_chars:12,d} | {total_display_chars/total_display_segments if total_display_segments > 0 else 0:12.1f}{RESET}")
    print("=" * 80 + "\n")

    print(f"{BOLD}{UNDERLINE}VISUAL DISTRIBUTION CHART (Segment Frequencies):{RESET}\n")
    max_count = max(display_counts.values()) if display_counts else 1
    for i, (tag, count) in enumerate(sorted_tags):
        pct = (count / total_display_segments) * 100 if total_display_segments > 0 else 0
        bar_length = int((count / max_count) * args.width)
        bar = "█" * bar_length
        color = COLOR_CYCLE[i % len(COLOR_CYCLE)]
        print(f"  {color}{tag:20s}{RESET} | {color}{bar:<{args.width}}{RESET} | {count:,} ({pct:.1f}%)")
    print("\n" + "=" * 80 + "\n")

    if args.csv:
        import csv
        try:
            with open(args.csv, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Tag", "Count", "Percentage", "TotalChars", "AvgCharPerSeg"])
                for tag, count in sorted_tags:
                    pct = (count / total_display_segments) * 100 if total_display_segments > 0 else 0
                    chars = display_chars[tag]
                    avg_len = chars / count if count > 0 else 0
                    writer.writerow([tag, count, f"{pct:.2f}%", chars, f"{avg_len:.2f}"])
            print(f"{GREEN}{BOLD}Successfully exported CSV distribution report to: {args.csv}{RESET}\n")
        except Exception as e:
            print(f"{RED}Failed to write CSV: {e}{RESET}\n", file=sys.stderr)

if __name__ == '__main__':
    main()
