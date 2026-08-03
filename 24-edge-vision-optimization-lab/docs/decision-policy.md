# Deployment decision policy

There is no universal winner. The console derives a Pareto frontier by maximizing macro F1
while minimizing p50 latency and artifact size. Conditional policies select:

- `quality_first`: highest macro F1, then latency;
- `cpu_low_latency`: lowest observed p50, then quality;
- `small_size`: smallest artifact, then quality.

Hard deployment constraints must be applied before preference ordering. NOT_RUN variants are
never recommended. Experimental variants can appear in analysis but are not accepted by the
online predictor.
