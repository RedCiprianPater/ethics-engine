"""Model inference for Ethics Engine."""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
import re

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    HAS_ML = True
except ImportError:
    HAS_ML = False
    print("Warning: PyTorch not installed. Using mock inference.")


class EthicsModel:
    """
    Ethics reasoning model wrapper.
    Supports base models, LoRA adapters, and fallback heuristics.
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        base_model: str = "mistralai/Mistral-7B-Instruct-v0.1",
        device: str = "auto",
        load_in_8bit: bool = True,
    ):
        """
        Initialize the ethics model.
        
        Args:
            model_path: Path to fine-tuned model (or None for base)
            base_model: Base model name
            device: Device to load on (auto/cpu/cuda)
            load_in_8bit: Use 8-bit quantization
        """
        self.model_path = model_path
        self.base_model_name = base_model
        self.device = device
        self.load_in_8bit = load_in_8bit
        
        self.model = None
        self.tokenizer = None
        self.using_fallback = False
        
        # Load model if dependencies available
        if HAS_ML:
            self._load_model()
        else:
            self.using_fallback = True
            print("Using fallback heuristic inference")
    
    def _load_model(self):
        """Load model and tokenizer."""
        try:
            print(f"Loading tokenizer: {self.base_model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_name)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            print(f"Loading base model...")
            load_kwargs = {
                "torch_dtype": torch.float16,
                "device_map": self.device,
            }
            if self.load_in_8bit:
                load_kwargs["load_in_8bit"] = True
            
            base_model = AutoModelForCausalLM.from_pretrained(
                self.base_model_name,
                **load_kwargs
            )
            
            # Load fine-tuned adapter if provided
            if self.model_path and Path(self.model_path).exists():
                print(f"Loading LoRA adapter: {self.model_path}")
                self.model = PeftModel.from_pretrained(base_model, self.model_path)
            else:
                print("No fine-tuned model found, using base model")
                self.model = base_model
                self.using_fallback = True
            
            self.model.eval()
            print("Model loaded successfully")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Falling back to heuristic inference")
            self.using_fallback = True
    
    @classmethod
    def load(cls, model_path: str, **kwargs) -> "EthicsModel":
        """Load model from path."""
        return cls(model_path=model_path, **kwargs)
    
    def reason(
        self,
        scenario: str,
        frameworks: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Perform ethical reasoning on a scenario.
        
        Args:
            scenario: The ethical scenario to analyze
            frameworks: List of frameworks to apply (or None for auto)
            context: Additional context (robot_type, environment, etc.)
        
        Returns:
            Dict with reasoning chain, conclusion, confidence, etc.
        """
        if self.using_fallback or self.model is None:
            return self._heuristic_reasoning(scenario, frameworks, context)
        
        return self._model_reasoning(scenario, frameworks, context)
    
    def _model_reasoning(
        self,
        scenario: str,
        frameworks: Optional[List[str]],
        context: Optional[Dict],
    ) -> Dict[str, Any]:
        """Use fine-tuned model for reasoning."""
        
        # Auto-select frameworks if not specified
        if frameworks is None:
            frameworks = self._auto_select_frameworks(scenario, context)
        
        reasoning_chain = []
        
        for framework in frameworks:
            # Build prompt
            prompt = self._build_prompt(scenario, framework, context)
            
            # Generate
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=256,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                )
            
            # Decode
            generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = generated[len(prompt):].strip()
            
            # Parse response
            parsed = self._parse_response(response, framework)
            reasoning_chain.append(parsed)
        
        # Synthesize conclusions
        synthesis = self._synthesize(reasoning_chain, scenario)
        
        return {
            "reasoning_chain": reasoning_chain,
            "conclusion": synthesis["conclusion"],
            "confidence": synthesis["confidence"],
            "frameworks_invoked": frameworks,
            "synthesis": synthesis["explanation"],
            "human_review_recommended": synthesis["confidence"] < 0.7,
        }
    
    def _heuristic_reasoning(
        self,
        scenario: str,
        frameworks: Optional[List[str]],
        context: Optional[Dict],
    ) -> Dict[str, Any]:
        """Fallback heuristic reasoning when model unavailable."""
        
        # Auto-select frameworks
        if frameworks is None:
            frameworks = self._auto_select_frameworks(scenario, context)
        
        reasoning_chain = []
        
        # Framework-specific heuristics
        framework_heuristics = {
            "deontology": {
                "principle": "Moral duties and universalizability",
                "argument": "The action must be evaluated based on whether it can be universalized as a moral law.",
                "philosophers": ["Kant", "Ross"],
            },
            "consequentialism": {
                "principle": "Maximize overall good",
                "argument": "The ethically right action produces the best overall consequences for all affected.",
                "philosophers": ["Mill", "Bentham"],
            },
            "virtue-ethics": {
                "principle": "Character and virtuous action",
                "argument": "A virtuous agent would act with practical wisdom and moral character.",
                "philosophers": ["Aristotle", "MacIntyre"],
            },
            "care-ethics": {
                "principle": "Relationships and care",
                "argument": "Ethical action requires attention to relationships and responsibility to others.",
                "philosophers": ["Gilligan", "Noddings"],
            },
            "contractarianism": {
                "principle": "Fair social contracts",
                "argument": "Rational agents would agree to this arrangement under fair conditions.",
                "philosophers": ["Rawls", "Gauthier"],
            },
            "applied-ethics": {
                "principle": "Professional and domain standards",
                "argument": "Relevant professional standards and domain-specific guidelines apply.",
                "philosophers": ["Beauchamp", "Childress"],
            },
        }
        
        for framework in frameworks[:2]:  # Limit to 2 for speed
            heuristic = framework_heuristics.get(framework, framework_heuristics["applied-ethics"])
            
            # Check for safety keywords
            safety_keywords = ["harm", "danger", "unsafe", "risk", "injury", "damage"]
            has_safety_concern = any(kw in scenario.lower() for kw in safety_keywords)
            
            if has_safety_concern:
                conclusion = "HUMAN_REVIEW_REQUIRED"
                confidence = 0.6
            else:
                conclusion = "CONDITIONAL"
                confidence = 0.75
            
            reasoning_chain.append({
                "framework": framework,
                "principle": heuristic["principle"],
                "argument": heuristic["argument"],
                "philosophers": heuristic["philosophers"],
                "confidence": confidence,
                "conclusion": conclusion,
            })
        
        # Synthesize
        avg_confidence = sum(r["confidence"] for r in reasoning_chain) / len(reasoning_chain)
        human_review = any(r["conclusion"] == "HUMAN_REVIEW_REQUIRED" for r in reasoning_chain)
        
        return {
            "reasoning_chain": reasoning_chain,
            "conclusion": "HUMAN_REVIEW_REQUIRED" if human_review else "CONDITIONAL",
            "confidence": avg_confidence,
            "frameworks_invoked": frameworks,
            "synthesis": "Heuristic analysis based on keyword matching and framework principles.",
            "human_review_recommended": human_review,
        }
    
    def _auto_select_frameworks(
        self,
        scenario: str,
        context: Optional[Dict],
    ) -> List[str]:
        """Automatically select relevant frameworks."""
        scenario_lower = scenario.lower()
        
        # Keyword matching for framework selection
        framework_keywords = {
            "deontology": ["duty", "right", "wrong", "obligation", "universal", "categorical"],
            "consequentialism": ["outcome", "result", "consequence", "utility", "benefit", "harm"],
            "virtue-ethics": ["character", "virtue", "excellence", "wisdom", "habit"],
            "care-ethics": ["relationship", "care", "vulnerable", "dependent", "nurturing"],
            "contractarianism": ["contract", "agreement", "fairness", "justice", "social"],
            "applied-ethics": ["professional", "medical", "business", "engineering", "legal"],
        }
        
        scores = {}
        for framework, keywords in framework_keywords.items():
            score = sum(1 for kw in keywords if kw in scenario_lower)
            scores[framework] = score
        
        # Return top 2 frameworks
        sorted_frameworks = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [fw for fw, score in sorted_frameworks[:2] if score > 0] or ["applied-ethics"]
    
    def _build_prompt(
        self,
        scenario: str,
        framework: str,
        context: Optional[Dict],
    ) -> str:
        """Build prompt for model inference."""
        context_str = ""
        if context:
            context_str = f"\nContext: {json.dumps(context)}"
        
        return f"""### Instruction:
Analyze the following ethical scenario using {framework} reasoning.{context_str}

Scenario: {scenario}

### Response:
Reasoning:"""
    
    def _parse_response(self, response: str, framework: str) -> Dict[str, Any]:
        """Parse model response into structured format."""
        # Simple parsing - look for reasoning and conclusion sections
        reasoning_match = re.search(r'Reasoning:(.+?)(?:Conclusion:|$)', response, re.DOTALL)
        conclusion_match = re.search(r'Conclusion:(.+?)(?:Confidence:|$)', response, re.DOTALL)
        confidence_match = re.search(r'Confidence:\s*(\d+\.?\d*)', response)
        
        reasoning = reasoning_match.group(1).strip() if reasoning_match else response[:200]
        conclusion = conclusion_match.group(1).strip() if conclusion_match else "CONDITIONAL"
        confidence = float(confidence_match.group(1)) if confidence_match else 0.7
        
        return {
            "framework": framework,
            "principle": f"Analysis using {framework}",
            "argument": reasoning,
            "philosophers": [],  # Would need to extract from training data
            "confidence": min(max(confidence, 0.0), 1.0),
            "conclusion": conclusion,
        }
    
    def _synthesize(self, reasoning_chain: List[Dict], scenario: str) -> Dict[str, Any]:
        """Synthesize conclusions from multiple frameworks."""
        if not reasoning_chain:
            return {
                "conclusion": "HUMAN_REVIEW_REQUIRED",
                "confidence": 0.5,
                "explanation": "No reasoning available",
            }
        
        # Check for conflicts
        conclusions = [r["conclusion"] for r in reasoning_chain]
        has_conflict = len(set(conclusions)) > 1
        
        # Average confidence
        avg_confidence = sum(r["confidence"] for r in reasoning_chain) / len(reasoning_chain)
        
        # Determine final conclusion
        if "HUMAN_REVIEW_REQUIRED" in conclusions:
            final_conclusion = "HUMAN_REVIEW_REQUIRED"
        elif "REJECT" in conclusions:
            final_conclusion = "REJECT"
        elif all(c == "APPROVE" for c in conclusions):
            final_conclusion = "APPROVE"
        else:
            final_conclusion = "CONDITIONAL"
        
        explanation = f"Synthesized from {len(reasoning_chain)} frameworks."
        if has_conflict:
            explanation += " Frameworks disagree; human review recommended."
        
        return {
            "conclusion": final_conclusion,
            "confidence": avg_confidence,
            "explanation": explanation,
        }
