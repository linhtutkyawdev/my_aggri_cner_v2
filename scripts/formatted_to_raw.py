#!/usr/bin/env python3
import sys
import os

def formatted_to_raw(line):
    """
    Converts a formatted line with tags like text@TAG| to raw text without tags and spaces.
    """
    segments = line.strip().split('|')
    raw_parts = []
    for seg in segments:
        if not seg:
            continue
        if '@' in seg:
            # Split from the right in case word itself contains '@'
            text = seg.rsplit('@', 1)[0]
            raw_parts.append(text)
        else:
            raw_parts.append(seg)
            
    raw_text = "".join(raw_parts)
    # Remove all spaces of various types (normal, non-breaking, zero-width)
    raw_text = raw_text.replace(" ", "").replace("\t", "").replace("\xa0", "").replace("\u200b", "")
    return raw_text

def conll_to_raw(conll_path):
    """
    Reads a CoNLL file and yields raw sentences (no tags, no spaces).
    """
    sentences = []
    current_sentence = []
    
    with open(conll_path, 'r', encoding='utf-8') as f:
        for line in f:
            line_str = line.strip()
            if not line_str:
                if current_sentence:
                    # Join tokens, remove all spaces of various types
                    raw_sent = "".join(current_sentence).replace(" ", "").replace("\t", "").replace("\xa0", "").replace("\u200b", "")
                    sentences.append(raw_sent)
                    current_sentence = []
                continue
            
            parts = line_str.split('\t')
            if len(parts) < 2:
                parts = line_str.split()
            if parts:
                current_sentence.append(parts[0])
                
        if current_sentence:
            raw_sent = "".join(current_sentence).replace(" ", "").replace("\t", "").replace("\xa0", "").replace("\u200b", "")
            sentences.append(raw_sent)
            
    return sentences

def main():
    if len(sys.argv) < 2:
        input_path = 'data_first_seminar/first_sem_agri_bio_word_formatted.txt'
        output_path = 'data_first_seminar/first_sem_agri_bio_word_raw.txt'
    else:
        input_path = sys.argv[1]
        if len(sys.argv) >= 3:
            output_path = sys.argv[2]
        else:
            base, ext = os.path.splitext(input_path)
            if ext == '.conll':
                output_path = f"{base}_raw.txt"
            else:
                # If it's a formatted file like _formatted.txt, we name it _raw.txt
                if base.endswith('_formatted'):
                    output_path = f"{base[:-10]}_raw.txt"
                else:
                    output_path = f"{base}_raw.txt"
                    
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' does not exist.", file=sys.stderr)
        sys.exit(1)
        
    print(f"Reading input from '{input_path}'...")
    
    # Check if input is conll
    is_conll = input_path.endswith('.conll')
    
    if is_conll:
        print("Detected CoNLL format.")
        raw_sentences = conll_to_raw(input_path)
    else:
        print("Detected Formatted Text format.")
        raw_sentences = []
        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    raw_sentences.append(formatted_to_raw(line))
                    
    print(f"Processed {len(raw_sentences)} sentences.")
    print(f"Writing raw text to '{output_path}'...")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for sent in raw_sentences:
            f.write(sent + '\n')
            
    print("Conversion completed successfully!")
    
    # Print first few lines of raw output for verification
    print("\nFirst few raw sentences:")
    for i, sent in enumerate(raw_sentences[:5]):
        print(f"Sentence {i+1}: {sent}")

if __name__ == '__main__':
    main()
