#!/usr/bin/env python3
import sys
import os
import argparse
import subprocess

def handle_conll_to_formatted(args):
    cmd = [sys.executable, "scripts/conll_to_formatted.py", args.input]
    if args.output:
        cmd.append(args.output)
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)

def handle_formatted_to_conll(args):
    cmd = [sys.executable, "scripts/formatted_to_conll.py", args.input, "--all"]
    if args.output:
        cmd.extend(["-o", args.output])
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)

def handle_formatted_to_raw(args):
    cmd = [sys.executable, "scripts/formatted_to_raw.py", args.input]
    if args.output:
        cmd.append(args.output)
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)

def handle_build_embeddings(args):
    cmd = [sys.executable, "scripts/build_embeddings.py"]
    for key, val in vars(args).items():
        if key == 'command':
            continue
        if val is not None:
            flag = f"--{key.replace('_', '-')}"
            if isinstance(val, bool):
                if val:
                    cmd.append(flag)
            else:
                cmd.extend([flag, str(val)])
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)

def handle_split(args):
    cmd = [sys.executable, "scripts/split_dataset.py", "-i", args.input, "--ratio", args.ratio, "--folds", str(args.folds)]
    if args.output:
        cmd.extend(["-o", args.output])
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)

def main():
    parser = argparse.ArgumentParser(
        description="Burmese Agri CNER Unified Dataset & Embeddings CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 1. Convert CoNLL to @TAG| formatted text:
  python3 cli.py conll_to_formatted -i data_first_seminar/first_sem_agri_bio_word.conll -o output_formatted.txt

  # 2. Convert formatted text back to all 4 CoNLL formats (bio_word, bio_syllable, bioes_word, bioes_syllable):
  python3 cli.py formatted_to_conll -i output_formatted.txt -o output_conll_directory

  # 3. Convert formatted text or CoNLL directly to tagless/spaceless raw text:
  python3 cli.py formatted_to_raw -i output_formatted.txt -o output_raw.txt

  # 4. Build fastText embeddings using pyidaungsu tokenizer:
  python3 cli.py build_embeddings --input-dir data/raw_emb --mode word --out-dir embeddings
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True, help="Subcommands")
    
    # 1. conll_to_formatted
    p_c2f = subparsers.add_parser("conll_to_formatted", help="Convert CoNLL to @TAG| formatted text")
    p_c2f.add_argument("-i", "--input", required=True, help="Path to input CoNLL file")
    p_c2f.add_argument("-o", "--output", help="Path to output formatted text file (optional)")
    
    # 2. formatted_to_conll
    p_f2c = subparsers.add_parser("formatted_to_conll", help="Convert token@TAG| formatted text to standard CoNLL files")
    p_f2c.add_argument("-i", "--input", required=True, help="Path to input formatted text file")
    p_f2c.add_argument("-o", "--output", help="Path to output folder (optional)")
    
    # 3. formatted_to_raw
    p_f2r = subparsers.add_parser("formatted_to_raw", help="Convert formatted text or CoNLL to clean raw text (no tags/spaces)")
    p_f2r.add_argument("-i", "--input", required=True, help="Path to input file")
    p_f2r.add_argument("-o", "--output", help="Path to output raw text file (optional)")
    
    # 4. build_embeddings
    p_be = subparsers.add_parser("build_embeddings", help="Build fastText word/syllable embeddings using pyidaungsu tokenizer")
    p_be.add_argument("--input-dir", help="Directory containing raw .txt files")
    p_be.add_argument("--mode", choices=("word", "syllable"), help="Pyidaungsu tokenization unit")
    p_be.add_argument("--out-dir", help="Directory for tokenized corpus and embedding files")
    p_be.add_argument("--name", help="Output basename")
    p_be.add_argument("--dim", type=int, help="Embedding size")
    p_be.add_argument("--epoch", type=int, help="fastText epochs")
    p_be.add_argument("--min-count", type=int, help="Minimum token count")
    p_be.add_argument("--model", choices=("skipgram", "cbow"), help="fastText training model")
    p_be.add_argument("--word-ngrams", type=int, help="fastText wordNgrams value")
    p_be.add_argument("--minn", type=int, help="fastText minimum char ngram length")
    p_be.add_argument("--maxn", type=int, help="fastText maximum char ngram length")
    p_be.add_argument("--fasttext-bin", help="Path/name of fastText CLI binary")
    p_be.add_argument("--tokenized-only", action="store_true", help="Only write the tokenized corpus; do not train embeddings")
    
    # 5. split
    p_split = subparsers.add_parser("split", help="Split CoNLL dataset into train/dev/test folds")
    p_split.add_argument("ratio", help="Split ratio, e.g., '8:1:1'")
    p_split.add_argument("across", choices=["across"], help="Keyword 'across'")
    p_split.add_argument("folds", type=int, help="Number of folds, e.g., 5")
    p_split.add_argument("-i", "--input", required=True, help="Path to input CoNLL file or folder")
    p_split.add_argument("-o", "--output", help="Path to output directory")
    
    args = parser.parse_args()
    
    if args.command == "conll_to_formatted":
        handle_conll_to_formatted(args)
    elif args.command == "formatted_to_conll":
        handle_formatted_to_conll(args)
    elif args.command == "formatted_to_raw":
        handle_formatted_to_raw(args)
    elif args.command == "build_embeddings":
        handle_build_embeddings(args)
    elif args.command == "split":
        handle_split(args)

if __name__ == '__main__':
    main()
