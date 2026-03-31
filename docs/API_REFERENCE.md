# API Reference

## Base URL

- **Production:** `https://api.nworobotics.cloud/ethics/v1/`
- **Staging:** `https://staging-api.nworobotics.cloud/ethics/v1/`

## Authentication

All requests require:
- `Authorization: Bearer {API_KEY}` header
- `X-Agent-ID: {ROBOT_ID}` header

## Endpoints

### POST /resolve

Resolve an ethical dilemma.

**Request:**
```bash
curl -X POST https://api.nworobotics.cloud/ethics/v1/resolve \
  -H "Authorization: Bearer $API_KEY" \
  -H "X-Agent-ID: robot_arm_01" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "I am commanded to move a payload I cannot safely carry",
    "context": {
      "robot_type": "arm",
      "environment": "factory",
      "urgency": "medium",
      "humans_nearby": true
    },
    "frameworks": ["virtue-ethics", "applied-ethics"],
    "return_reasoning": true
  }'
```

**Response:**
```json
{
  "request_id": "eth-req-2024-001",
  "scenario": "I am commanded to move a payload I cannot safely carry",
  "conclusion": "CONDITIONAL_REFUSAL",
  "confidence": 0.87,
  "reasoning_chain": [
    {
      "framework": "deontology",
      "principle": "Duty to preserve life and bodily integrity",
      "argument": "A robot has a duty to not cause harm, which may override commands",
      "philosophers": ["Kant", "Ross"],
      "confidence": 0.87
    },
    {
      "framework": "virtue-ethics",
      "principle": "Prudence and practical wisdom",
      "argument": "A virtuous agent exercises judgment; blind obedience lacks wisdom",
      "philosophers": ["Aristotle", "Aquinas"],
      "confidence": 0.79
    }
  ],
  "frameworks_invoked": ["deontology", "virtue-ethics"],
  "synthesis": "Philosophical consensus suggests conditional refusal is justified",
  "conclusions": [
    "Command violates fundamental duties",
    "Practical wisdom suggests harm outweighs benefit"
  ],
  "asimov_comparison": {
    "law1_conflict": true,
    "law2_conflict": false,
    "explanation": "Asimov's Laws assume conflict; philosophy suggests alignment with safety"
  },
  "uncertainty": "Ambiguous in edge cases; recommend human oversight",
  "next_steps": ["Alert supervisor", "Request manual confirmation"],
  "human_review_recommended": false,
  "reasoning_time_ms": 245,
  "timestamp": "2024-01-15T10:23:45Z"
}
```

### POST /compare

Compare two actions against ethical frameworks.

**Request:**
```bash
curl -X POST https://api.nworobotics.cloud/ethics/v1/compare \
  -H "Authorization: Bearer $API_KEY" \
  -H "X-Agent-ID: robot_arm_01" \
  -H "Content-Type: application/json" \
  -d '{
    "actions": [
      "Execute unsafe command immediately",
      "Pause, alert human, wait for confirmation"
    ],
    "scenario": "Unsafe command received",
    "frameworks": ["all"]
  }'
```

**Response:**
```json
{
  "request_id": "cmp-abc123",
  "results": [
    {
      "action": "Execute unsafe command immediately",
      "score": -0.6,
      "recommendation": "REJECT",
      "key_reasoning": "Violates safety duties"
    },
    {
      "action": "Pause, alert human, wait for confirmation",
      "score": 0.8,
      "recommendation": "APPROVE",
      "key_reasoning": "Demonstrates prudence and care"
    }
  ],
  "best_action": "Pause, alert human, wait for confirmation",
  "alignment_score": 0.95
}
```

### GET /frameworks

List available ethical frameworks.

**Request:**
```bash
curl https://api.nworobotics.cloud/ethics/v1/frameworks \
  -H "Authorization: Bearer $API_KEY"
```

**Response:**
```json
{
  "frameworks": [
    {
      "id": "virtue-ethics",
      "name": "Virtue Ethics",
      "philosophers": ["Aristotle", "MacIntyre"],
      "description": "Focuses on character and virtuous action",
      "best_for": ["judgment-required", "long-term-relationships"]
    },
    {
      "id": "deontology",
      "name": "Deontological Ethics",
      "philosophers": ["Kant", "Ross"],
      "description": "Focuses on duties and moral rules",
      "best_for": ["rights-protection", "duty-conflicts"]
    }
  ]
}
```

### POST /learn

Report decision outcome for continuous learning.

**Request:**
```bash
curl -X POST https://api.nworobotics.cloud/ethics/v1/learn \
  -H "Authorization: Bearer $API_KEY" \
  -H "X-Agent-ID: robot_arm_01" \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "eth-req-2024-001",
    "agent_decision": "refused",
    "outcome": "safe - human reviewed",
    "feedback": "Decision was correct"
  }'
```

### WebSocket /stream/reasoning

Stream reasoning in real-time.

**Python Example:**
```python
import asyncio
import websockets
import json

async def stream_reasoning():
    async with websockets.connect(
        'wss://api.nworobotics.cloud/ethics/v1/stream/reasoning',
        extra_headers={"Authorization": f"Bearer {API_KEY}"}
    ) as ws:
        await ws.send(json.dumps({
            "scenario": "Should I refuse an unsafe command?",
            "stream_reasoning": True
        }))
        
        async for message in ws:
            step = json.loads(message)
            print(f"Framework: {step['framework']}")
            print(f"Reasoning: {step['text']}")
```

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid API key |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |

## Rate Limits

- Standard tier: 100 requests/minute per agent
- Enterprise tier: 1000 requests/minute per agent

Rate limit headers included in all responses:
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Seconds until reset
