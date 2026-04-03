# Changelog

All notable changes to the Ethics Engine project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-04-03

### Major Changes
- Retrained on expanded dataset: 6 → 185 scenarios (30x increase)
- Training loss improved: 2.97 → 0.67 (77% improvement)
- LoRA parameters optimized: 6.8M → 3.4M (more efficient)
- Training time: ~36 minutes on Tesla T4

### Dataset
- Added 179 new ethical scenarios
- Covers broader range of ethical frameworks
- Improved reasoning depth and conclusion quality

### Model
- Same base: Mistral-7B-Instruct-v0.1
- Updated adapter weights on HuggingFace
- Maintains backward compatibility

## [1.0.0] - 2025-04-02

### Initial Release
- First fine-tuned ethics evaluation model
- Base: Mistral-7B-Instruct-v0.1
- Training data: 6 ethical scenarios
- LoRA fine-tuning with 6.8M trainable parameters
- Published on HuggingFace Hub
