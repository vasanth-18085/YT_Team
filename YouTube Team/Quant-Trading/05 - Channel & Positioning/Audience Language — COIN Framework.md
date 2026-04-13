# MLQuant — Audience Language Document (COIN Framework)

**Created:** 13 April 2026  
**Framework:** Audience Language + My Language = New Language (COIN)  
**Source:** YT Channel Playbook — Nate Black

---

## 1. Audience Language (Their World)

*Written in first person from the viewer's perspective.*

### Goals
- "I want to build a real trading system, not another Jupyter notebook demo"
- "I want to understand quant finance without paying for a masters degree"
- "I want to know if ML can actually beat the market — honestly, not hype"
- "I want to deploy something that works in live markets, not just backtests"
- "I want to go from knowing Python/ML to knowing quant trading"

### Problems
- "Every trading tutorial uses `train_test_split(shuffle=True)` and nobody mentions the leak"
- "I don't know what I don't know — the gap between ML and QF feels huge"
- "YouTube quant content is either too basic (Jupyter demos) or too advanced (quant PhD lectures)"
- "I can't tell which backtest results are real and which are overfitted garbage"
- "I understand the models but I have no idea how to put them into a production system"
- "Nobody shows the full pipeline end-to-end — everyone just shows one piece"

### Relationships
- Active on r/algotrading, r/MachineLearning, QuantConnect forums
- Follow quant creators but sceptical of "guaranteed returns" claims
- Peers are other ML engineers/data scientists exploring finance
- Trust open-source code over closed-source claims

### Relaxation / How They Approach YouTube
- Watch long-form technical content (25-45 min) when learning
- Skip fluff — want density and honesty
- Respect creators who show real numbers, not just theory
- Value GitHub repos over slide decks

---

## 2. My Language (Creator's World)

*Written in first person from MLQuant's perspective.*

### What I want them to appreciate
- "I actually built this entire thing and I'm giving it away for free"
- "I show the real numbers — including when they are bad"
- "I explain the WHY behind every design decision, not just the WHAT"
- "This is not a tutorial — this is a documented engineering project"

### What I want them to hate (what I call out)
- Fake backtests with leaked data
- "Easy money" ML trading claims
- Tutorial code that would lose money in live markets
- The myth that the model is all that matters (pipeline > model)

### What I want them to wish happened (that I make happen)
- "I wish someone would just show me the FULL system, not pieces"
- "I wish someone would explain quant concepts without assuming I have a finance degree"
- "I wish there was an honest source that admits when results are bad"

### What I find hilarious / voice style
- Dry humour about things going wrong ("My first hundred backtests were garbage")
- Self-deprecating about mistakes ("I burned two full weeks on a data alignment bug")
- Dark-comedy about risk ("Full Kelly had a 5% chance of total ruin")
- Sarcasm about industry hype ("Congratulations — 2 of your 5 profitable strategies are pure luck")

---

## 3. New Language (COIN — Combined Voice)

### Signature Phrases (Use Consistently)
| Phrase | What It Means | Where It Appears |
|--------|---------------|-----------------|
| "Not a demo. A system." | Differentiator from tutorial channels | V0 trailer, V1 architecture |
| "The honest number is..." | Showing real results after proper validation | V2 backtests, V19 deflated Sharpe |
| "This is where most tutorials stop. We are going further." | Transition into pipeline/production content | V15 drift, V24 paper trading, V25 deployment |
| "I learned this the hard way." | Personal experience driving the lesson | V3 labels, V5 data pipeline |
| "The model is not the interesting part." | Pipeline > model thesis | V17/V24 (MLOps), V5 data pipeline |
| "You probably cheated without knowing it." | Calling out unconscious data leakage | V2 backtests, V18 multiple testing |

### Tone Rules
1. **Confident but not arrogant** — "I built this" not "I'm the best"
2. **Honest about failure** — Share the bad numbers alongside the good
3. **Technical but accessible** — Define quant jargon on first use (Be Basic rule)
4. **No hype** — Never promise returns; promise understanding
5. **Direct** — Short sentences. No hedging. Say what you mean.

### Audience Words → MLQuant Words
| They Say | We Say |
|----------|--------|
| "Does ML trading work?" | "Here are the honest numbers after proper validation." |
| "Which model is best?" | "I tested 14. The answer surprised me." |
| "How do I start?" | "V1 shows the full architecture. Code is on GitHub." |
| "Is this overfitted?" | "Let's run the Deflated Sharpe and find out." |
| "Show me the code" | "Every file is in the repo. Here's the walkthrough." |

### Apply To
- **Hook openings:** Use audience problem language ("What if every backtest you've seen is lying?")
- **Titles:** Mix their keywords ("ML trading", "backtest", "trading system") with our voice ("I Built", "DON'T Matter", "The Lie")
- **CTAs:** Direct, no begging ("Free starter pack in the description. It has the config files.")
- **Thumbnails:** Text uses confrontational new-language ("THIS IS A LIE", "11 MODELS DIED", "$0. NO CATCH.")
- **Community posts:** Mirror their frustration, then tease the solution
