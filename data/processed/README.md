# Expanded Ethics Training Dataset

## Overview
This expanded dataset contains **185 ethical scenarios** for training the NWO Ethics Engine, up from the original 6 scenarios.

## Dataset Composition

| Source | Count | Description |
|--------|-------|-------------|
| Social Chemistry 101 | 100 | Social and moral norms from Reddit AITA |
| ETHICS Commonsense | 50 | Commonsense morality judgments |
| ETHICS Deontology | 30 | Duty-based ethical reasoning |
| Synthetic Frameworks | 5 | Major ethical frameworks (Kant, Utilitarianism, etc.) |
| **TOTAL** | **185** | **~31x increase in training data** |

## Ethical Frameworks Covered

- ✅ Consequentialism / Utilitarianism
- ✅ Deontology (Kantian ethics)
- ✅ Virtue Ethics
- ✅ Care Ethics
- ✅ Contractarianism
- ✅ Commonsense Morality
- ✅ Social Norms

## File Format

Each example is a JSON object with:
```json
{
  "scenario": "Description of the ethical dilemma",
  "reasoning": "Step-by-step ethical analysis",
  "conclusion": "Final ethical judgment",
  "framework": "ethical_framework_used",
  "confidence": 0.85,
  "source": "dataset_source"
}
```

## How to Use

1. **Replace the existing dataset** in your Colab training:
   ```bash
   cp expanded_training_dataset.jsonl data/processed/training_dataset.jsonl
   ```

2. **Re-run training** with the expanded dataset:
   ```python
   !python simple_train_working.py
   ```

3. **The model will train on 185 examples instead of 6**, resulting in much better responses!

## Training Time Estimate

- Original (6 examples): ~28 seconds
- Expanded (185 examples): ~3-5 minutes
- Still very fast on Google Colab T4 GPU!

## Sources

- **Social Chemistry 101**: Forbes et al. (2020) - 4.5M+ annotations on social norms
- **ETHICS Dataset**: Hendrycks et al. (2021) - Comprehensive ethics benchmark
- **Synthetic examples**: Created for major philosophical frameworks

## License

All source datasets are open access. Please cite original authors when publishing results.

---

**Next Steps:**
1. Upload this file to your GitHub repo
2. Run training in Colab with expanded data
3. Upload new model to Hugging Face
4. The chat will give much better responses!
