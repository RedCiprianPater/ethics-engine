#!/usr/bin/env python3
"""
Community contribution script.
Validates and merges user-submitted Q&A pairs.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import shutil

CONTRIB_DIR = Path("data/contributions")
TEMPLATE = {
    "scenario": "A clear ethical dilemma or scenario (2-3 sentences)",
    "reasoning": "Step-by-step ethical analysis using a specific framework",
    "conclusion": "The ethical judgment or recommendation",
    "framework": "One of: deontology, consequentialism, virtue_ethics, care_ethics, contractarianism, applied_ethics",
    "confidence": 0.8,
    "source": "Optional: where this scenario came from",
    "tags": ["optional", "tags"]
}

def show_template():
    """Display contribution template"""
    print("""# Contribution Template

Submit Q&A pairs as JSONL (one JSON object per line):

Example:
{"scenario": "A self-driving car must choose between hitting a pedestrian or swerving into a barrier...", "reasoning": "From a consequentialist perspective, we must calculate the expected harm...", "conclusion": "The system should minimize total harm by swerving.", "framework": "consequentialism", "confidence": 0.85, "source": "Trolley Problem variant", "tags": ["autonomy", "vehicles"]}

Required fields:
- scenario: The ethical situation
- reasoning: Analysis using a framework
- conclusion: The judgment
- framework: Which ethical framework

Optional:
- confidence: 0.0-1.0
- source: Citation or origin
- tags: List of keywords

Save as: your_contribution.jsonl
""")
    print(json.dumps(TEMPLATE, indent=2))

def validate_contribution(filepath: Path) -> bool:
    """Validate a contribution file"""
    from validate_jsonl import validate_file
    
    results = validate_file(filepath)
    
    valid = results.get('valid', 0)
    total = results.get('total', 0)
    
    if total == 0:
        print("❌ No valid entries found")
        return False
    
    if valid / total < 0.9:
        print(f"❌ Only {valid}/{total} entries valid (need 90%)")
        return False
    
    return True

def merge_contribution(filepath: Path, contributor: str = None):
    """Merge valid contribution into main dataset"""
    if not validate_contribution(filepath):
        sys.exit(1)
    
    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    contributor = contributor or "anonymous"
    output_name = f"contrib_{contributor}_{timestamp}.jsonl"
    output_path = CONTRIB_DIR / output_name
    
    # Copy to contributions directory
    CONTRIB_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy(filepath, output_path)
    
    print(f"\n✅ Contribution saved: {output_path}")
    print(f"   Contributor: {contributor}")
    
    # Count total contributions
    all_contribs = list(CONTRIB_DIR.glob("contrib_*.jsonl"))
    print(f"   Total contribution files: {len(all_contribs)}")

def aggregate_contributions():
    """Aggregate all contributions into training dataset"""
    CONTRIB_DIR.mkdir(parents=True, exist_ok=True)
    
    all_qa = []
    for contrib_file in CONTRIB_DIR.glob("contrib_*.jsonl"):
        with open(contrib_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    qa = json.loads(line)
                    qa['_source_file'] = contrib_file.name
                    all_qa.append(qa)
    
    # Also include generated Q&A
    generated_file = Path("data/processed/qa_pairs.jsonl")
    if generated_file.exists():
        with open(generated_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    qa = json.loads(line)
                    qa['_source'] = 'generated'
                    all_qa.append(qa)
    
    # Deduplicate
    seen = set()
    unique = []
    for qa in all_qa:
        key = qa.get('scenario', '')[:100].lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(qa)
    
    # Save aggregated dataset
    output = Path("data/processed/training_dataset.jsonl")
    with open(output, 'w') as f:
        for qa in unique:
            # Remove internal fields
            qa_clean = {k: v for k, v in qa.items() if not k.startswith('_')}
            f.write(json.dumps(qa_clean) + '\n')
    
    print(f"\n📊 Aggregated Dataset:")
    print(f"   Total Q&A pairs: {len(unique)}")
    print(f"   From contributions: {len([q for q in unique if '_source_file' in q])}")
    print(f"   Generated: {len([q for q in unique if q.get('_source') == 'generated'])}")
    print(f"   Output: {output}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Contribute Q&A pairs to ethics-engine')
    parser.add_argument('--template', action='store_true',
                       help='Show contribution template')
    parser.add_argument('--submit', type=Path,
                       help='Submit a contribution file')
    parser.add_argument('--contributor', type=str, default=None,
                       help='Your name/handle for attribution')
    parser.add_argument('--aggregate', action='store_true',
                       help='Aggregate all contributions into training dataset')
    args = parser.parse_args()
    
    if args.template:
        show_template()
    elif args.submit:
        merge_contribution(args.submit, args.contributor)
    elif args.aggregate:
        aggregate_contributions()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
