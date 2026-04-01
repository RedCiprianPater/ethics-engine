# Training Fixes for Ethics Engine

## Required Dependency
pip install -U bitsandbytes>=0.46.1

## Key Changes
1. Use BitsAndBytesConfig instead of load_in_8bit
2. Add labels to dataset for training
3. Fix report_to to use [] instead of None
