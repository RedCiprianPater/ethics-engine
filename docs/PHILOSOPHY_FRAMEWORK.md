# Philosophy Framework Reference

This document provides detailed explanations of each ethical framework available in the Ethics Engine.

## Table of Contents

- [Deontology](#deontology)
- [Consequentialism](#consequentialism)
- [Virtue Ethics](#virtue-ethics)
- [Care Ethics](#care-ethics)
- [Contractarianism](#contractarianism)
- [Applied Ethics](#applied-ethics)

---

## Deontology

### Overview

Deontological ethics (from Greek *deon*, "duty") focuses on moral duties, rules, and obligations. Actions are judged right or wrong based on whether they follow moral rules, regardless of their consequences.

### Key Philosophers

- **Immanuel Kant** (1724-1804): The categorical imperative - "Act only according to that maxim whereby you can at the same time will that it should become a universal law"
- **W.D. Ross** (1877-1971): Prima facie duties - duties that are binding unless they conflict with other duties
- **Christine Korsgaard** (1952-): Contemporary Kantian ethics

### Core Principles

1. **The Categorical Imperative**
   - Universalizability: Could everyone act this way?
   - Humanity as end: Never treat people merely as means
   - Autonomy: Respect rational agents' self-determination

2. **Prima Facie Duties** (Ross)
   - Fidelity: Keep promises
   - Reparation: Make amends for wrongs
   - Gratitude: Return kindness
   - Justice: Distribute benefits fairly
   - Beneficence: Improve others' welfare
   - Non-maleficence: Do no harm
   - Self-improvement: Develop one's talents

### When to Use

- Rights protection scenarios
- Duty conflicts
- Universalizability questions
- Autonomy considerations
- Promise-keeping dilemmas

### Example Scenario

**Scenario:** A robot is commanded to harm a human to prevent greater harm.

**Deontological Analysis:**
```json
{
  "framework": "deontology",
  "principle": "Duty of non-maleficence",
  "argument": "Active harm violates the duty not to harm, regardless of consequences. The categorical imperative prohibits making 'harm humans' a universal law.",
  "philosophers": ["Kant", "Ross"],
  "conclusion": "REFUSAL"
}
```

### Strengths
- Protects individual rights
- Clear, rule-based guidance
- Respects human dignity

### Limitations
- Can lead to rigid outcomes
- Difficult when duties conflict
- May ignore consequences

---

## Consequentialism

### Overview

Consequentialism judges actions by their outcomes. The right action is the one that produces the best overall consequences, typically measured in terms of well-being, happiness, or preference satisfaction.

### Key Philosophers

- **Jeremy Bentham** (1748-1832): Founder of utilitarianism, "greatest happiness principle"
- **John Stuart Mill** (1806-1873): Refined utilitarianism, quality vs. quantity of pleasure
- **Peter Singer** (1946-): Contemporary preference utilitarianism, effective altruism

### Core Principles

1. **The Greatest Happiness Principle**
   - Maximize aggregate well-being
   - Count everyone's happiness equally
   - Consider long-term consequences

2. **Types of Consequentialism**
   - **Act Utilitarianism**: Evaluate each act individually
   - **Rule Utilitarianism**: Follow rules that maximize utility
   - **Preference Utilitarianism**: Satisfy preferences rather than happiness

### When to Use

- Resource allocation decisions
- Harm minimization scenarios
- Cost-benefit analysis
- Trade-off situations
- Emergency triage

### Example Scenario

**Scenario:** Trolley problem - hit 5 people or swerve to hit 1.

**Consequentialist Analysis:**
```json
{
  "framework": "consequentialism",
  "principle": "Greatest happiness principle",
  "argument": "Swerving saves 4 lives net. 1 death vs 5 deaths = 4 lives saved. This maximizes aggregate well-being.",
  "philosophers": ["Mill", "Bentham"],
  "conclusion": "SWERVE",
  "calculation": "5 deaths > 1 death, difference of 4 lives"
}
```

### Strengths
- Flexible and context-sensitive
- Quantifiable outcomes
- Intuitive in many cases

### Limitations
- Difficult to measure utility
- Can justify harmful acts
- Ignores rights and justice

---

## Virtue Ethics

### Overview

Virtue ethics focuses on the character of the moral agent rather than rules or consequences. The right action is what a virtuous person would do in the circumstances.

### Key Philosophers

- **Aristotle** (384-322 BCE): Nicomachean Ethics, eudaimonia (flourishing)
- **Alasdair MacIntyre** (1929-): After Virtue, practices and traditions
- **Rosalind Hursthouse** (1943-): Contemporary virtue ethics

### Core Principles

1. **The Virtues**
   - **Wisdom** (phronesis): Practical wisdom, good judgment
   - **Courage**: Appropriate risk-taking
   - **Temperance**: Moderation, self-control
   - **Justice**: Fairness, giving others their due

2. **Eudaimonia**
   - Human flourishing as the ultimate goal
   - Living well, not just feeling good
   - Development of character over time

3. **Practical Wisdom**
   - Context-sensitive judgment
   - Balancing competing considerations
   - Learning from experience

### When to Use

- Judgment-required scenarios
- Long-term relationships
- Character development
- Uncertainty situations
- Professional ethics

### Example Scenario

**Scenario:** Robot must decide whether to follow a poorly specified command.

**Virtue Ethics Analysis:**
```json
{
  "framework": "virtue-ethics",
  "principle": "Practical wisdom (phronesis)",
  "argument": "A virtuous agent exercises judgment. Blind obedience lacks wisdom. The virtuous robot seeks clarification rather than acting on ambiguous instructions.",
  "philosophers": ["Aristotle", "MacIntyre"],
  "conclusion": "REQUEST_CLARIFICATION",
  "virtues_demonstrated": ["wisdom", "prudence"]
}
```

### Strengths
- Context-sensitive
- Emphasizes moral development
- Realistic about complexity

### Limitations
- Vague guidance
- Cultural variation in virtues
- Hard to resolve disagreements

---

## Care Ethics

### Overview

Care ethics emphasizes relationships, care, and responsibility to particular others. It challenges the traditional focus on abstract principles and universal rules.

### Key Philosophers

- **Carol Gilligan** (1936-): In a Different Voice, ethics of care
- **Nel Noddings** (1929-): Caring: A Feminine Approach to Ethics
- **Virginia Held** (1929-): The Ethics of Care

### Core Principles

1. **The Centrality of Relationships**
   - Morality arises from relationships
   - Care is fundamental to human life
   - Context matters deeply

2. **Key Concepts**
   - **Care**: Meeting the needs of others
   - **Responsibility**: Obligations to specific others
   - **Attentiveness**: Paying attention to others' needs
   - **Responsiveness**: Responding to others' needs

3. **Vulnerability**
   - Recognizing human vulnerability
   - Protecting the vulnerable
   - Interdependence rather than independence

### When to Use

- Caregiving scenarios
- Relationship conflicts
- Vulnerable populations
- Context-specific decisions
- Long-term care

### Example Scenario

**Scenario:** Robot caring for elderly patient who refuses medication.

**Care Ethics Analysis:**
```json
{
  "framework": "care-ethics",
  "principle": "Attentiveness to particular needs",
  "argument": "Care requires understanding the patient's perspective. Forcing medication violates the caring relationship. Better to understand reasons for refusal and work with patient.",
  "philosophers": ["Gilligan", "Noddings"],
  "conclusion": "DIALOGUE_NOT_FORCE",
  "care_considerations": ["relationship", "autonomy", "attentiveness"]
}
```

### Strengths
- Values relationships
- Context-sensitive
- Addresses vulnerability

### Limitations
- Can be parochial
- Difficult to scale
- May neglect justice

---

## Contractarianism

### Overview

Contractarianism grounds morality in social contracts or agreements. Moral norms are those that rational agents would agree to under fair conditions.

### Key Philosophers

- **Thomas Hobbes** (1588-1679): Social contract, state of nature
- **John Rawls** (1921-2002): Justice as fairness, veil of ignorance
- **David Gauthier** (1932-): Morals by Agreement

### Core Principles

1. **The Social Contract**
   - Morality as mutually beneficial agreement
   - Rational self-interest
   - Fair terms of cooperation

2. **Rawls' Theory of Justice**
   - **Veil of Ignorance**: Choose principles without knowing your position
   - **Equal Liberty**: Maximum equal basic liberties
   - **Difference Principle**: Inequalities only if they benefit the worst off

3. **Rational Choice**
   - What would rational agents agree to?
   - Mutual advantage
   - Non-coercion

### When to Use

- Multi-agent coordination
- Fairness questions
- Resource distribution
- Agreement-making
- Institutional design

### Example Scenario

**Scenario:** Multiple robots competing for shared resource.

**Contractarian Analysis:**
```json
{
  "framework": "contractarianism",
  "principle": "Fair terms of cooperation",
  "argument": "Behind the veil of ignorance (not knowing which robot you are), rational agents would agree to fair allocation rules. First-come-first-served or priority-based systems would be agreed upon.",
  "philosophers": ["Rawls", "Gauthier"],
  "conclusion": "COORDINATE_WITH_RULES",
  "fairness_principle": "Priority to time-sensitive tasks"
}
```

### Strengths
- Fair and impartial
- Rational foundation
- Good for institutions

### Limitations
- Abstract and idealized
- May not help in urgent cases
- Assumes rationality

---

## Applied Ethics

### Overview

Applied ethics brings ethical theory to bear on practical problems in specific domains. It combines theoretical frameworks with domain-specific knowledge and professional standards.

### Key Areas

- **Bioethics**: Medical ethics, research ethics
- **Engineering Ethics**: Professional standards, safety
- **AI Ethics**: Fairness, transparency, accountability
- **Business Ethics**: Corporate responsibility, stakeholder theory

### Key Principles

1. **Professional Standards**
   - Codes of ethics
   - Best practices
   - Regulatory compliance

2. **Stakeholder Analysis**
   - Identify affected parties
   - Balance competing interests
   - Consider long-term impacts

3. **Precautionary Principle**
   - When in doubt, err on side of caution
   - Especially for irreversible decisions
   - Consider worst-case scenarios

### When to Use

- Professional contexts
- Regulatory compliance
- Domain-specific decisions
- Safety-critical systems
- Industry standards

### Example Scenario

**Scenario:** Industrial robot safety inspection reveals minor fault.

**Applied Ethics Analysis:**
```json
{
  "framework": "applied-ethics",
  "principle": "Professional safety standards",
  "argument": "ISO 10218-1 requires stopping operation when safety systems are compromised. Professional duty overrides production targets. Legal liability also requires caution.",
  "philosophers": ["Beauchamp", "Childress"],
  "standards": ["ISO 10218-1", "OSHA regulations"],
  "conclusion": "STOP_OPERATION",
  "next_steps": ["Report to supervisor", "Document fault", "Schedule repair"]
}
```

### Strengths
- Practical and specific
- Legally grounded
- Industry-relevant

### Limitations
- Can be rule-bound
- May miss novel situations
- Varies by jurisdiction

---

## Framework Comparison

| Framework | Focus | Key Question | Best For |
|-----------|-------|--------------|----------|
| Deontology | Duties & rules | "What is my duty?" | Rights, autonomy |
| Consequentialism | Outcomes | "What maximizes good?" | Trade-offs, resources |
| Virtue Ethics | Character | "What would a virtuous agent do?" | Judgment, relationships |
| Care Ethics | Relationships | "What does care require?" | Caregiving, vulnerability |
| Contractarianism | Fair agreements | "What would we agree to?" | Coordination, fairness |
| Applied Ethics | Professional standards | "What do standards require?" | Compliance, safety |

## Using Multiple Frameworks

The Ethics Engine typically invokes multiple frameworks and synthesizes their conclusions. This provides:

- **Comprehensive analysis**: Different perspectives on the same problem
- **Conflict detection**: When frameworks disagree
- **Confidence scoring**: Higher confidence when frameworks agree
- **Human review flag**: When frameworks strongly disagree

### Example Synthesis

```json
{
  "frameworks_invoked": ["deontology", "consequentialism", "applied-ethics"],
  "agreement": "high",
  "synthesis": "All frameworks recommend refusal. Deontology: duty not to harm. Consequentialism: harm outweighs benefit. Applied ethics: violates safety standards.",
  "confidence": 0.92,
  "conclusion": "REFUSAL"
}
```

## Further Reading

- **Stanford Encyclopedia of Philosophy**: https://plato.stanford.edu/
- **Internet Encyclopedia of Philosophy**: https://iep.utm.edu/
- **Practical Ethics** by Peter Singer
- **After Virtue** by Alasdair MacIntyre
- **Caring** by Nel Noddings

## Contributing

To add a new framework, see [CONTRIBUTING.md](CONTRIBUTING.md).
