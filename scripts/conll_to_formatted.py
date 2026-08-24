#!/usr/bin/env python3
import sys
import os

def parse_conll(file_path):
    """
    Parses a CoNLL file and yields sentences.
    Each sentence is a list of tuples (word, tag).
    """
    sentences = []
    current_sentence = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line_str = line.strip()
            if not line_str:
                if current_sentence:
                    sentences.append(current_sentence)
                    current_sentence = []
                continue
            
            # Split by tab first, fallback to whitespace
            parts = line_str.split('\t')
            if len(parts) < 2:
                parts = line_str.split()
                
            if len(parts) >= 2:
                word = parts[0]
                tag = parts[-1]
                current_sentence.append((word, tag))
            else:
                # Handle cases where word or tag might be empty
                word = parts[0] if parts else ""
                tag = "O"
                current_sentence.append((word, tag))
                
        if current_sentence:
            sentences.append(current_sentence)
            
    return sentences

def convert_sentence_to_formatted(words_tags):
    """
    Converts a single sentence (list of (word, tag)) to the target format:
    e.g. ပန်းပွင့်ချိန်တွင်@O|အပူချိန်မြင့်လွန်းခြင်း@WEATHER|နှင့်နိမ့်လွန်းခြင်းမဖြစ်စေရပါ။@O|
    """
    segments = []
    current_tokens = []
    current_tag_type = None
    
    for word, tag in words_tags:
        # Determine the base tag type
        if tag == 'O':
            base_tag = 'O'
            is_start = False
        else:
            # tag is like 'B-WEATHER', 'I-WEATHER', 'S-WEATHER', 'E-WEATHER'
            parts = tag.split('-', 1)
            prefix = parts[0]
            base_tag = parts[1] if len(parts) > 1 else tag
            # In BIO/BIOES, 'B' (Begin) and 'S' (Single) mark the start of a new entity
            is_start = (prefix in ('B', 'S'))
            
        if not current_tokens:
            current_tokens.append(word)
            current_tag_type = base_tag
        elif base_tag != current_tag_type or is_start:
            # Emit current segment
            segments.append((current_tokens, current_tag_type))
            current_tokens = [word]
            current_tag_type = base_tag
        else:
            # Continue the current segment
            current_tokens.append(word)
            
    if current_tokens:
        segments.append((current_tokens, current_tag_type))
        
    # Format segments
    formatted_parts = []
    for tokens, tag_type in segments:
        text = "".join(tokens)
        formatted_parts.append(f"{text}@{tag_type}")
        
    return "|".join(formatted_parts) + "|"

def main():
    if len(sys.argv) < 2:
        input_path = 'data/first_sem_agri_bio_word.conll'
        output_path = 'data/first_sem_agri_bio_word_formatted.txt'
    else:
        input_path = sys.argv[1]
        if len(sys.argv) >= 3:
            output_path = sys.argv[2]
        else:
            base, ext = os.path.splitext(input_path)
            output_path = f"{base}_formatted.txt"
            
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' does not exist.", file=sys.stderr)
        sys.exit(1)
        
    print(f"Reading CoNLL data from '{input_path}'...")
    sentences = parse_conll(input_path)
    print(f"Parsed {len(sentences)} sentences.")
    
    print(f"Formatting sentences...")
    formatted_sentences = []
    for sent in sentences:
        formatted = convert_sentence_to_formatted(sent)
        formatted_sentences.append(formatted)
        
    print(f"Writing formatted data to '{output_path}'...")
    with open(output_path, 'w', encoding='utf-8') as f:
        for sent_str in formatted_sentences:
            f.write(sent_str + '\n')
            
    print("Conversion completed successfully!")
    
    # Print first few lines of the formatted output for verification
    print("\nFirst few formatted sentences:")
    for i, sent_str in enumerate(formatted_sentences[:5]):
        print(f"Sentence {i+1}: {sent_str}")

if __name__ == '__main__':
    main()
