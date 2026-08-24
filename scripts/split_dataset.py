#!/usr/bin/env python3
import sys
import os
import argparse
from pathlib import Path

def load_conll_sentences(file_path):
    """
    Parses a CoNLL file and returns a list of raw sentence blocks.
    Each sentence block includes its trailing empty line.
    """
    sentences = []
    current_sentence = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            current_sentence.append(line)
            if not line.strip():  # blank line separates sentences
                if current_sentence:
                    sentences.append("".join(current_sentence))
                    current_sentence = []
        if current_sentence:
            # Handle files that don't have a trailing empty line
            content = "".join(current_sentence)
            if not content.endswith('\n'):
                content += '\n'
            if not content.endswith('\n\n') and not content.endswith('\r\n\r\n'):
                content += '\n'
            sentences.append(content)
            
    return sentences

def split_sentences_by_ratio(sentences, ratio, folds):
    """
    Splits the sentences into folds using a rotating block cross-validation strategy.
    ratio: list of 3 integers [X, Y, Z] (e.g. [8, 1, 1])
    folds: number of folds (e.g. 5)
    """
    B = sum(ratio)
    N = len(sentences)
    X, Y, Z = ratio
    
    folds_data = []
    for i in range(folds):
        # Starting block shift for Fold i
        S_i = int(i * B / folds)
        
        # Rotating block indices
        train_blocks = [(S_i + b) % B for b in range(X)]
        dev_blocks = [(S_i + X + b) % B for b in range(Y)]
        test_blocks = [(S_i + X + Y + b) % B for b in range(Z)]
        
        def get_sentences_for_blocks(blocks):
            selected = []
            for b in sorted(blocks):  # Sort blocks to preserve continuous sequence if possible
                start_idx = int(b * N / B)
                end_idx = int((b + 1) * N / B)
                selected.extend(sentences[start_idx:end_idx])
            return selected
            
        train_sents = get_sentences_for_blocks(train_blocks)
        dev_sents = get_sentences_for_blocks(dev_blocks)
        test_sents = get_sentences_for_blocks(test_blocks)
        
        folds_data.append((train_sents, dev_sents, test_sents))
        
    return folds_data

def process_file(file_path, output_dir, ratio, folds):
    print(f"Processing CoNLL file: '{file_path}'")
    sentences = load_conll_sentences(file_path)
    print(f"Loaded {len(sentences)} sentences.")
    
    if len(sentences) < sum(ratio):
        print(f"Warning: Too few sentences ({len(sentences)}) to split into ratio {ratio}.", file=sys.stderr)
        
    folds_data = split_sentences_by_ratio(sentences, ratio, folds)
    
    base_name = Path(file_path).stem
    
    # Group by setup/conll name on the upper level
    setup_dir = output_dir / base_name
    setup_dir.mkdir(parents=True, exist_ok=True)
    
    for i, (train, dev, test) in enumerate(folds_data):
        # Generate the folds on the lower level
        fold_dir = setup_dir / f"fold_{i}"
        fold_dir.mkdir(parents=True, exist_ok=True)
        
        # Standard filenames inside each fold
        train_file = fold_dir / "train.conll"
        dev_file = fold_dir / "dev.conll"
        test_file = fold_dir / "test.conll"
        
        # Write files
        with open(train_file, 'w', encoding='utf-8') as f:
            f.writelines(train)
        with open(dev_file, 'w', encoding='utf-8') as f:
            f.writelines(dev)
        with open(test_file, 'w', encoding='utf-8') as f:
            f.writelines(test)
            
        print(f"  Fold {i} -> Train: {len(train)} sents, Dev: {len(dev)} sents, Test: {len(test)} sents")

def main():
    parser = argparse.ArgumentParser(description="Split CoNLL dataset into train/dev/test folds")
    parser.add_argument("-i", "--input", required=True, help="Path to input CoNLL file or folder containing CoNLL files")
    parser.add_argument("-o", "--output", help="Path to output folder (optional)")
    parser.add_argument("--ratio", default="8:1:1", help="Split ratio, default: 8:1:1")
    parser.add_argument("--folds", type=int, default=5, help="Number of folds, default: 5")
    
    args = parser.parse_args()
    
    # Parse ratio
    try:
        ratio = [int(r) for r in args.ratio.split(":")]
        if len(ratio) != 3:
            raise ValueError()
    except Exception:
        print("Error: Ratio must be in the format 'X:Y:Z' where X, Y, Z are integers.", file=sys.stderr)
        sys.exit(1)
        
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input path '{input_path}' does not exist.", file=sys.stderr)
        sys.exit(1)
        
    output_dir = Path(args.output) if args.output else input_path.parent / f"{input_path.stem}_split"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Split Configuration:")
    print(f"  Input: {input_path}")
    print(f"  Output: {output_dir}")
    print(f"  Ratio: {args.ratio} (Train: {ratio[0]}x, Dev: {ratio[1]}x, Test: {ratio[2]}x)")
    print(f"  Folds: {args.folds}")
    print("-" * 50)
    
    if input_path.is_file():
        process_file(input_path, output_dir, ratio, args.folds)
    else:
        conll_files = sorted(list(input_path.glob("*.conll")))
        if not conll_files:
            print(f"Error: No .conll files found under directory '{input_path}'", file=sys.stderr)
            sys.exit(1)
        for conll_file in conll_files:
            process_file(conll_file, output_dir, ratio, args.folds)
            print()
            
    print("Dataset splitting completed successfully!")

if __name__ == "__main__":
    main()
