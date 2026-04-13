# V8 — Meta-Labeling — Hook & Intro

**Video Title:** 9 Classifiers to Judge Your Predictions: When to Trust Your Model
**Date:** 10 April 2026

---

## Hook Question

What if your model is right 60 percent of the time — but you have no idea which 60 percent? Would you still bet real money on every single prediction?

## Credibility

I built a meta-labelling layer that sits on top of the forecasting models and answers exactly that question: should I trust this particular prediction or not? Nine different classifiers vote on whether each trade is worth taking. The result: same gross accuracy, but the trades that pass the meta-label filter have a hit rate 11 percent higher than the ones that do not.

## Why Now (R.A.I.N.Y — N)

As ML models get better, the marginal gains from switching architectures are shrinking. Meta-labeling is one of the few techniques that can still deliver a measurable edge improvement on top of any existing model. If you are hitting a performance ceiling right now, this is the lever most people have not tried.

## Video Structure

In this video I walk you through the meta-labelling concept from Marcos López de Prado's work, show you how I implemented it with 9 classifiers, and demonstrate the filtering effect on trade quality. By the end you will have a system that tells you not just what to trade but when to trust the signal and when to sit out.

## Open Loop

But first let me show you what happens when you trade every signal your model generates versus only the ones the meta-label approves — because the equity curve comparison is the most convincing argument I can make.
