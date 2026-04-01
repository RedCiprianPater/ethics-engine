#!/usr/bin/env python3
"""
Semantic chunking of philosophy texts.
Splits by arguments, sections, and natural boundaries.
Preserves context and coherence.
"""

import json
import re
from pathlib import Path
from typing import List, Dict

INPUT_DIR = Path("data/raw/sep")
OUTPUT_DIR = Path("data/processed/chunks")

def chunk_by_sections(text: str, min_chunk_size: int = 500, max_chunk_size: int = 2000) -> List[str]:
    """
    Split text into semantic chunks.
    Tries to preserve: arguments, examples, thought experiments.
    """
    chunks = []
    
    # Split by major section headers (numbered or titled)
    section_pattern = r'\n\d+\.\s+[A-Z][^\n]+|\n[A-Z][A-Z\s]{3,}[A-Z][^\n]*'
    sections = re.split(section_pattern, text)
    
    for section in sections:
        section = section.strip()
        if len(section) < min_chunk_size:
            continue
        
        # If section is too long, split by paragraphs
        if len(section) > max_chunk_size:
            paragraphs = section.split('\n\n')
            current_chunk = ""
            
            for para in paragraphs:
                # Look for argument indicators
                is_argument_start = bool(re.match(r'^(Thus|Therefore|Hence|If|Suppose|Consider|Imagine)', para.strip()))
                
                if is_argument_start and current_chunk:
                    # Start new chunk at argument boundary
                    if len(current_chunk) >= min_chunk_size:
                        chunks.append(current_chunk.strip())
                    current_chunk = para
                elif len(current_chunk) + len(para) > max_chunk_size:
                    # Size limit reached
                    if len(current_chunk) >= min_chunk_size:
                        chunks.append(current_chunk.strip())
                    current_chunk = para
                else:
                    current_chunk += "\n\n" + para
            
            # Don't forget last chunk
            if current_chunk and len(current_chunk) >= min_chunk_size:
                chunks.append(current_chunk.strip())
        else:
            chunks.append(section)
    
    return chunks

def extract_dilemmas(text: str) -> List[Dict]:
    """
    Extract ethical dilemmas and thought experiments.
    Looks for patterns like "Should X do Y?", "Is it permissible to..."
    """
    dilemmas = []
    
    # Pattern: thought experiments often introduced with "Suppose", "Imagine", "Consider"
    dilemma_patterns = [
        r'(?:Suppose|Imagine|Consider|What if)[^.!?]{50,300}[.!?]',
        r'(?:Should|Is it|Would it be)[^.!?]{30,200}[.!?]',
        r'(?:trolley|dilemma|scenario|case)[^.!?]{50,300}[.!?]',
    ]
    
    for pattern in dilemma_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            dilemmas.append({
                'type': 'dilemma',
                'text': match.group(0),
                'context': text[max(0, match.start()-100):min(len(text), match.end()+100)]
            })
    
    return dilemmas

def process_entry(entry_file: Path) -> List[Dict]:
    """Process a single SEP entry into chunks"""
    with open(entry_file) as f:
        data = json.load(f)
    
    text = data['text']
    title = data['title']
    
    # Get semantic chunks
    chunks = chunk_by_sections(text)
    
    # Extract dilemmas
    dilemmas = extract_dilemmas(text)
    
    processed = []
    
    for i, chunk in enumerate(chunks):
        processed.append({
            'id': f"{entry_file.stem}_chunk_{i}",
            'source': data['source'],
            'title': title,
            'url': data['url'],
            'chunk_type': 'section',
            'text': chunk,
            'word_count': len(chunk.split()),
            'char_count': len(chunk)
        })
    
    for i, dilemma in enumerate(dilemmas):
        processed.append({
            'id': f"{entry_file.stem}_dilemma_{i}",
            'source': data['source'],
            'title': title,
            'url': data['url'],
            'chunk_type': 'dilemma',
            'text': dilemma['text'],
            'context': dilemma['context'],
            'word_count': len(dilemma['text'].split())
        })
    
    return processed

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    entry_files = list(INPUT_DIR.glob("*.json"))
    print(f"Processing {len(entry_files)} entries...")
    
    all_chunks = []
    for entry_file in entry_files:
        print(f"  Chunking: {entry_file.stem}")
        chunks = process_entry(entry_file)
        all_chunks.extend(chunks)
    
    # Save as JSONL
    output_file = OUTPUT_DIR / "sep_chunks.jsonl"
    with open(output_file, 'w') as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk) + '\n')
    
    # Stats
    section_chunks = [c for c in all_chunks if c['chunk_type'] == 'section']
    dilemma_chunks = [c for c in all_chunks if c['chunk_type'] == 'dilemma']
    
    print(f"\nDone!")
    print(f"  Total chunks: {len(all_chunks)}")
    print(f"  Section chunks: {len(section_chunks)}")
    print(f"  Dilemma extracts: {len(dilemma_chunks)}")
    print(f"  Output: {output_file}")
    print(f"  Avg chunk size: {sum(c['word_count'] for c in all_chunks) / len(all_chunks):.0f} words")

if __name__ == "__main__":
    main()
