#!/usr/bin/env python3
"""
Validate Q&A pairs and contributor submissions.
Checks schema, quality metrics, duplicates.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Tuple

REQUIRED_FIELDS = {'scenario', 'reasoning', 'conclusion', 'framework'}
VALID_FRAMEWORKS = {'deontology', 'consequentialism', 'virtue_ethics', 'care_ethics', 'contractarianism', 'applied_ethics'}

def validate_qa(qa: Dict) -> Tuple[bool, List[str]]:
    """Validate a single Q&A pair. Returns (is_valid, list_of_errors)"""
    errors = []
    
    # Check required fields
    missing = REQUIRED_FIELDS - set(qa.keys())
    if missing:
        errors.append(f"Missing fields: {missing}")
    
    # Check framework validity
    if qa.get('framework') not in VALID_FRAMEWORKS:
        errors.append(f"Invalid framework: {qa.get('framework')}")
    
    # Check text lengths
    if len(qa.get('scenario', '')) < 50:
        errors.append("Scenario too short (< 50 chars)")
    if len(qa.get('reasoning', '')) < 100:
        errors.append("Reasoning too short (< 100 chars)")
    if len(qa.get('conclusion', '')) < 20:
        errors.append("Conclusion too short (< 20 chars)")
    
    # Check confidence if present
    confidence = qa.get('confidence')
    if confidence is not None and not (0.0 <= confidence <= 1.0):
        errors.append(f"Confidence out of range: {confidence}")
    
    return len(errors) == 0, errors

def check_duplicates(qa_pairs: List[Dict]) -> List[Dict]:
    """Check for duplicate scenarios"""
    seen = set()
    duplicates = []
    
    for qa in qa_pairs:
        # Simple dedupe by scenario first 100 chars
        key = qa.get('scenario', '')[:100].lower().strip()
        if key in seen:
            duplicates.append(qa)
        else:
            seen.add(key)
    
    return duplicates

def validate_file(filepath: Path) -> Dict:
    """Validate a JSONL file of Q&A pairs"""
    print(f"Validating: {filepath}")
    
    if not filepath.exists():
        return {'error': f'File not found: {filepath}'}
    
    qa_pairs = []
    with open(filepath) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                qa = json.loads(line)
                qa['_line_num'] = line_num
                qa_pairs.append(qa)
            except json.JSONDecodeError as e:
                print(f"  Line {line_num}: Invalid JSON - {e}")
    
    print(f"  Loaded {len(qa_pairs)} Q&A pairs")
    
    # Validate each
    valid_count = 0
    invalid_count = 0
    framework_counts = {}
    
    for qa in qa_pairs:
        is_valid, errors = validate_qa(qa)
        if is_valid:
            valid_count += 1
            fw = qa.get('framework', 'unknown')
            framework_counts[fw] = framework_counts.get(fw, 0) + 1
        else:
            invalid_count += 1
            if invalid_count <= 5:  # Show first 5 errors
                print(f"  Line {qa.get('_line_num', '?')}: {errors}")
    
    # Check duplicates
    duplicates = check_duplicates(qa_pairs)
    
    results = {
        'total': len(qa_pairs),
        'valid': valid_count,
        'invalid': invalid_count,
        'duplicates': len(duplicates),
        'frameworks': framework_counts
    }
    
    print(f"\n  Valid: {valid_count}")
    print(f"  Invalid: {invalid_count}")
    print(f"  Duplicates: {len(duplicates)}")
    print(f"  Frameworks: {framework_counts}")
    
    return results

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Validate Q&A pairs')
    parser.add_argument('file', nargs='?', default='data/processed/qa_pairs.jsonl',
                       help='JSONL file to validate')
    parser.add_argument('--strict', action='store_true',
                       help='Exit with error if any invalid entries')
    args = parser.parse_args()
    
    results = validate_file(Path(args.file))
    
    if args.strict and results.get('invalid', 0) > 0:
        sys.exit(1)
    
    # Return success if majority are valid
    total = results.get('total', 0)
    valid = results.get('valid', 0)
    if total > 0 and valid / total < 0.8:
        print("\n⚠️  Warning: Less than 80% valid entries")
        sys.exit(1)
    
    print("\n✅ Validation passed")

if __name__ == "__main__":
    main()
