# Cost and Runtime Evidence

The final production configuration is the Jev v2 hybrid pipeline. Its real 100-review cold/warm calculator, editable rates, usage ledger, saved records/calls, projections, and offline replay command are in [`jev-pilot-v2/`](jev-pilot-v2/). Run this no-call command for the final calculator:

```bash
python3 run_pipeline.py jev-report --cost-dir cost/jev-pilot-v2 --budget-usd 5.00
```

The files at the root of this directory preserve the earlier local-Ollama calculator. They are historical comparison evidence, not the final production estimate.

## Historical local-Ollama calculator

The default command is offline and makes no model or network calls:

```bash
python3 run_pipeline.py replay --cost-dir cost
```

The real pilot is an explicit separate command. It requires Ollama running locally with the pinned model installed.

Cold run with an empty result cache and one worker:

```bash
python3 run_pipeline.py pilot \
  --input "Final Assignment - Spotify Reviews Dataset/cost_100.csv" \
  --cost-dir cost --run-kind cold --reset-cache --batch-size 10 --verification-size 10
```

Warm run with unchanged settings and saved results:

```bash
python3 run_pipeline.py pilot \
  --input "Final Assignment - Spotify Reviews Dataset/cost_100.csv" \
  --cost-dir cost --run-kind warm --batch-size 10 --verification-size 10
```

After both runs, regenerate `cost/report.md`, `cost/usage.csv`, and `cost/rates.csv`:

```bash
python3 run_pipeline.py replay --cost-dir cost
```

The local model is `qwen3.5:4b-q4_K_M` with pinned Ollama digest `d8b0f5e9760c`. API spend is zero. Local electricity and hardware depreciation are reported as unknown rather than silently treated as zero.

