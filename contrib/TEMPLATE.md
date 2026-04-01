# Contributing Q&A Pairs to Ethics Engine

Thank you for contributing to the NWO Ethics Engine training dataset!

## Quick Start

1. **Create your Q&A pairs** as a JSONL file (one JSON object per line)
2. **Validate** your submission
3. **Submit** via the contribution script

## File Format

Each line must be a valid JSON object with these fields:

```json
{
  "scenario": "A clear ethical dilemma (2-3 sentences)",
  "reasoning": "Step-by-step analysis using a specific framework",
  "conclusion": "The ethical judgment or recommendation",
  "framework": "deontology",
  "confidence": 0.85,
  "source": "Optional: citation or origin",
  "tags": ["optional", "keywords"]
}
```

## Required Fields

| Field | Description | Example |
|-------|-------------|---------|
| `scenario` | The ethical situation | "A doctor has one dose of medicine and two patients..." |
| `reasoning` | Analysis using framework | "From a deontological perspective, the doctor has a duty to..." |
| `conclusion` | Final judgment | "The doctor should treat the patient with highest survival chance." |
| `framework` | Ethical framework used | One of: `deontology`, `consequentialism`, `virtue_ethics`, `care_ethics`, `contractarianism`, `applied_ethics` |

## Optional Fields

| Field | Description |
|-------|-------------|
| `confidence` | Float 0.0-1.0 indicating certainty |
| `source` | Book, paper, or URL where scenario originated |
| `tags` | Array of keywords for categorization |

## Example Submission

Create `my_contribution.jsonl`:

```json
{"scenario": "An autonomous vehicle must choose between hitting a pedestrian who suddenly stepped into the road, or swerving into a barrier which will likely injure the passenger.", "reasoning": "From a consequentialist perspective, we must calculate expected outcomes. Hitting the pedestrian causes certain severe harm to one person. Swerving risks harm to the passenger but preserves the pedestrian's life. The expected utility favors swerving if passenger injury probability is low.", "conclusion": "The vehicle should swerve to minimize expected harm.", "framework": "consequentialism", "confidence": 0.8, "source": "Trolley Problem variant", "tags": ["autonomy", "vehicles", "harm"]}
```

## Submit Your Contribution

```bash
# Show template
python scripts/contribute.py --template

# Submit your file
python scripts/contribute.py --submit my_contribution.jsonl --contributor "YourName"

# Aggregate all contributions (maintainers only)
python scripts/contribute.py --aggregate
```

## Quality Guidelines

✅ **DO:**
- Use concrete, specific scenarios
- Show clear reasoning steps
- Cite sources when possible
- Use diverse frameworks
- Include edge cases

❌ **DON'T:**
- Submit vague or abstract scenarios
- Include personal opinions without reasoning
- Duplicate existing entries
- Use biased or loaded language

## Validation

Your submission will be checked for:
- Required fields present
- Valid framework names
- Minimum text lengths
- JSON validity
- Duplicate detection

Need 90%+ valid entries to be accepted.

## Questions?

Open an issue on GitHub: https://github.com/RedCiprianPater/ethics-engine/issues
