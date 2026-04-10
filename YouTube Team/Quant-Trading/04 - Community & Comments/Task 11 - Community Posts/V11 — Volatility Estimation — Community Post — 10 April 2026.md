# V11 — Volatility Estimation — Community Post

**Date:** 10 April 2026

GARCH has been the standard for 30 years. It still works most of the time.

But during March 2020 it forecast 1.8% daily vol when realised vol was 4.9%. Off by 2.7x.

That error feeds directly into position sizing. Underestimate volatility by 2.7x and your positions are 2.7x too large. During a crash.

The fix: a three model ensemble. GARCH for normal conditions. A hybrid for transitions. An LSTM for crises.

New video covers all three and the reweighting system 👉 [INSERT PRIMARY LINK]
