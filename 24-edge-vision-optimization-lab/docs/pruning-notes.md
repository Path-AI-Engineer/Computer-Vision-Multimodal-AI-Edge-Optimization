# Pruning notes

Magnitude pruning makes weights zero but preserves dense tensor shapes. Dense kernels may
still execute the same multiply-add schedule, so sparsity and observed speedup are reported as
separate fields. Reparameterization must be removed before export. Structured channel pruning
can alter compute shape, but requires shape propagation, compatible residual paths and
post-pruning fine-tuning. Negative speedup results are retained.
