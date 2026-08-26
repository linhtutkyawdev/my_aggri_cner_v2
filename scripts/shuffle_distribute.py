#!/usr/bin/env python3
import os
import sys
import argparse
import random

def read_units(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line.rstrip('\r\n') for line in f]
    
    # Detect if the file is block-based (like CoNLL, with blank separator lines)
    middle_blanks = False
    first_non_blank = -1
    last_non_blank = -1
    for i, line in enumerate(lines):
        if line.strip():
            if first_non_blank == -1:
                first_non_blank = i
            last_non_blank = i
            
    if first_non_blank != -1:
        for i in range(first_non_blank, last_non_blank):
            if not lines[i].strip():
                middle_blanks = True
                break
                
    if middle_blanks:
        units = []
        current_unit = []
        for line in lines:
            if not line.strip():
                if current_unit:
                    units.append(current_unit)
                    current_unit = []
            else:
                current_unit.append(line)
        if current_unit:
            units.append(current_unit)
        return units, True
    else:
        # flat line-by-line
        units = [[line] for line in lines if line.strip()]
        return units, False

def write_units(units, is_block, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        if is_block:
            f.write('\n\n'.join('\n'.join(u) for u in units) + '\n\n')
        else:
            f.write('\n'.join(u[0] for u in units) + '\n')

def distribute_uniformly(list_a, list_b):
    A = len(list_a)
    B = len(list_b)
    T = A + B
    if A == 0:
        return list_b
    if B == 0:
        return list_a
        
    # Calculate deterministic, beautifully symmetric indices for list_a
    a_indices = [int((i + 0.5) * T / A) for i in range(A)]
    
    output = []
    a_idx = 0
    b_idx = 0
    for j in range(T):
        if a_idx < A and j == a_indices[a_idx]:
            output.append(list_a[a_idx])
            a_idx += 1
        else:
            output.append(list_b[b_idx])
            b_idx += 1
    return output

def main():
    parser = argparse.ArgumentParser(description="Shuffle the first 1/3 of a text file and distribute them uniformly among the remaining 2/3.")
    parser.add_argument("-i", "--input", required=True, help="Path to input text or CoNLL file")
    parser.add_argument("-o", "--output", help="Path to output text or CoNLL file (defaults to overwriting input)")
    parser.add_argument("--seed", type=int, help="Optional random seed for reproducible shuffling")
    parser.add_argument("--global-shuffle", action="store_true", help="Perform a global shuffle on the entire file instead of 1/3-2/3 uniform distribution")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file not found at: {args.input}")
        sys.exit(1)
        
    units, is_block = read_units(args.input)
    N = len(units)
    print(f"ℹ️ Total units detected: {N} (Format: {'Block/CoNLL' if is_block else 'Flat Text/Line-by-line'})")
    
    if args.global_shuffle:
        print(f"➡️ Performing a GLOBAL shuffle on all {N} units...")
        if args.seed is not None:
            random.seed(args.seed)
        final_units = list(units)
        random.shuffle(final_units)
        output_path = args.output if args.output else args.input
        write_units(final_units, is_block, output_path)
        print(f"✅ Successfully shuffled the entire file globally!")
        print(f"💾 Result saved to: {output_path}")
        return

    if N < 3:
        print(f"⚠️ Warning: File has only {N} units. Shuffling the entire file instead of splitting.")
        if args.seed is not None:
            random.seed(args.seed)
        shuffled = list(units)
        random.shuffle(shuffled)
        output_path = args.output if args.output else args.input
        write_units(shuffled, is_block, output_path)
        print(f"✅ Saved shuffled result to: {output_path}")
        return

    # Split into 1/3 (A) and 2/3 (B)
    A = N // 3
    list_a = units[:A]
    list_b = units[A:]
    
    print(f"➡️ Splitting: First 1/3 = {len(list_a)} units, Remaining 2/3 = {len(list_b)} units.")
    
    # Initialize random seed
    if args.seed is not None:
        random.seed(args.seed)
        
    # Shuffle the first 1/3 separately
    random.shuffle(list_a)
    print(f"🎲 Shuffled the first 1/3 subset separately (seed={args.seed}).")
    
    # Shuffle the remaining 2/3 separately
    random.shuffle(list_b)
    print(f"🎲 Shuffled the remaining 2/3 subset separately (seed={args.seed}).")
    
    # Merge uniformly
    final_units = distribute_uniformly(list_a, list_b)
    
    output_path = args.output if args.output else args.input
    write_units(final_units, is_block, output_path)
    print(f"✅ Successfully distributed the separately shuffled 1/3 uniformly into the separately shuffled 2/3!")
    print(f"💾 Result saved to: {output_path}")

if __name__ == '__main__':
    main()
