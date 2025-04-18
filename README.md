# GeneGPT_OpenRouter

This directory contains an OpenRouter adaption of the code for GeneGPT. Please go to the GeneGPT repo for the original implementation. https://github.com/ncbi/GeneGPT

# Instructions

Clone the GeneGPT_OpenRouter repo to our computer. Change into the directory. 
```
python main.py \
  --input data/geneturing.json \
  --model openai/gpt-4o \
  --mask 111111
```

You can specify any OpenRouter model with the --model flag. If none is specified, the script defaults to openai/gpt-4o
