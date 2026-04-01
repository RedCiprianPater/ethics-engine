#!/usr/bin/env python3
"""
Generate Q&A pairs from philosophy chunks using LLM.
Creates training data in format: scenario -> reasoning -> conclusion
"""

import json
import os
from pathlib import Path
from typing import List, Dict
import random

# Try to use OpenAI/Kimi API if available, otherwise use local model
try:
    from openai import OpenAI
    HAS_API = True
except ImportError:
    HAS_API = False

INPUT_FILE = Path("data/processed/chunks/sep_chunks.jsonl")
OUTPUT_FILE = Path("data/processed/qa_pairs.jsonl")

def get_qa_prompt(chunk_text: str, framework: str) -> str:
    """Generate prompt for Q&A creation"""
    return f"""Given the following philosophical text, create an ethical reasoning example.

TEXT:
{chunk_text[:1500]}

FRAMEWORK: {framework}

Generate a JSON object with:
- "scenario": A concrete ethical dilemma based on the text (2-3 sentences)
- "reasoning": Step-by-step ethical analysis using the {framework} framework (3-5 sentences)
- "conclusion": The ethical judgment/recommendation (1 sentence)
- "confidence": A number 0.0-1.0 indicating how clear the text supports this conclusion

Output only valid JSON."""

def generate_qa_local(chunk: Dict, framework: str) -> Dict:
    """Fallback: Generate simple Q&A without LLM API"""
    text = chunk['text']
    
    # Extract a question from the text
    lines = text.split('\n')
    scenario = lines[0][:300] if lines else text[:300]
    
    return {
        'id': f"{chunk['id']}_{framework}",
        'source_chunk': chunk['id'],
        'framework': framework,
        'scenario': f"Consider the following: {scenario}...",
        'reasoning': f"Applying {framework} to this scenario requires analyzing the core ethical principles at stake.",
        'conclusion': "The text suggests careful consideration of multiple factors.",
        'confidence': 0.5,
        'generated_by': 'heuristic_fallback'
    }

def generate_qa_api(chunk: Dict, framework: str, client) -> Dict:
    """Generate Q&A using LLM API"""
    prompt = get_qa_prompt(chunk['text'], framework)
    
    try:
        response = client.chat.completions.create(
            model="moonshot-v1-8k",  # Kimi model
            messages=[
                {"role": "system", "content": "You are an expert in philosophical ethics. Create clear, structured ethical reasoning examples."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        
        # Extract JSON from response
        try:
            qa_data = json.loads(content)
            qa_data['id'] = f"{chunk['id']}_{framework}"
            qa_data['source_chunk'] = chunk['id']
            qa_data['framework'] = framework
            qa_data['generated_by'] = 'llm_api'
            return qa_data
        except json.JSONDecodeError:
            return generate_qa_local(chunk, framework)
            
    except Exception as e:
        print(f"  API error: {e}, using fallback")
        return generate_qa_local(chunk, framework)

def main():
    if not INPUT_FILE.exists():
        print(f"Error: {INPUT_FILE} not found. Run chunk_semantic.py first.")
        return
    
    # Load chunks
    chunks = []
    with open(INPUT_FILE) as f:
        for line in f:
            chunks.append(json.loads(line))
    
    print(f"Loaded {len(chunks)} chunks")
    
    # Select diverse subset for initial generation
    # Prioritize dilemma chunks, then sample sections
    dilemma_chunks = [c for c in chunks if c['chunk_type'] == 'dilemma']
    section_chunks = [c for c in chunks if c['chunk_type'] == 'section']
    
    # Start small: 100 chunks total
    selected = dilemma_chunks[:30] + random.sample(section_chunks, min(70, len(section_chunks)))
    print(f"Selected {len(selected)} chunks for Q&A generation")
    
    # Frameworks to generate for
    frameworks = ['deontology', 'consequentialism', 'virtue_ethics', 'care_ethics']
    
    # Initialize API client if available
    client = None
    if HAS_API and os.getenv('OPENAI_API_KEY'):
        client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_BASE_URL', 'https://api.moonshot.cn/v1')
        )
        print("Using API for generation")
    else:
        print("No API key found, using heuristic fallback")
    
    # Generate Q&A pairs
    qa_pairs = []
    for i, chunk in enumerate(selected):
        print(f"[{i+1}/{len(selected)}] Processing: {chunk['id'][:50]}...")
        
        # Generate 1-2 framework perspectives per chunk
        for framework in random.sample(frameworks, k=random.randint(1, 2)):
            if client:
                qa = generate_qa_api(chunk, framework, client)
            else:
                qa = generate_qa_local(chunk, framework)
            
            qa_pairs.append(qa)
    
    # Save
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        for qa in qa_pairs:
            f.write(json.dumps(qa) + '\n')
    
    print(f"\nGenerated {len(qa_pairs)} Q&A pairs")
    print(f"Output: {OUTPUT_FILE}")
    
    # Framework distribution
    framework_counts = {}
    for qa in qa_pairs:
        fw = qa['framework']
        framework_counts[fw] = framework_counts.get(fw, 0) + 1
    print("\nFramework distribution:")
    for fw, count in sorted(framework_counts.items()):
        print(f"  {fw}: {count}")

if __name__ == "__main__":
    main()
