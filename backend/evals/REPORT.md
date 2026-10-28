# Model comparison

Labeled cases: 42 PageClassification, 13 CandidateJudgement. Every case is a prompt Linkmortem sent while scanning real repositories.

Costly errors are the mistakes that hurt users most: calling a living page dead, or accepting a different page as the new home.

Unanswered cases timed out or were refused by the provider. Accuracy counts only answered cases.

| Model | Cases | Accuracy | Costly errors | Invalid answers | Unanswered | Median latency | p95 latency | Input tokens | Output tokens |
|---|---|---|---|---|---|---|---|---|---|
| backboard:openrouter:google/gemma-4-31b-it | 55 | 98% | 0 | 0 | 0 | 2.98 s | 5.43 s | 463 | 29 |
| backboard:openrouter:google/gemma-4-26b-a4b-it | 55 | 95% | 0 | 0 | 0 | 1.22 s | 2.11 s | 503 | 27 |
| backboard:openrouter:meta-llama/llama-4-scout (JSON by prompt) | 55 | 93% | 4 | 0 | 0 | 5.06 s | 7.52 s | 690 | 32 |
| backboard:openrouter:deepseek/deepseek-v3.2 | 55 | 91% | 3 | 0 | 0 | 4.29 s | 9.47 s | 423 | 44 |
| backboard:openrouter:qwen/qwen3-30b-a3b-instruct-2507 | 55 | 91% | 3 | 0 | 1 | 2.57 s | 9.43 s | 447 | 30 |
| ollama:gemma4:e4b | 55 | 87% | 1 | 0 | 0 | 0.72 s | 1.11 s | 585 | 30 |
| backboard:openrouter:google/gemma-3-27b-it | 55 | 87% | 5 | 0 | 0 | 2.48 s | 4.17 s | 353 | 30 |
| backboard:openrouter:mistralai/ministral-14b-2512 | 55 | 79% | 10 | 1 | 2 | 1.86 s | 2.90 s | 647 | 37 |
| backboard:openrouter:google/gemma-3-4b-it | 55 | 67% | 10 | 0 | 0 | 1.29 s | 2.55 s | 699 | 36 |
