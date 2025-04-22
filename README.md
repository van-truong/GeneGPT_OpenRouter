# GeneGPT_OpenRouter

This directory contains an OpenRouter adaption of the code for GeneGPT. Please go to the GeneGPT repo for the original implementation. https://github.com/ncbi/GeneGPT

# Instructions

Clone the GeneGPT_OpenRouter repo to your computer. Change into the directory. Make sure your environment has all the neccessary requirements, including storing your OPENROUTER_API_KEY in your system variables. 

Then when ready, run this command from your terminal:

```
python main.py \
  --input data/geneturing.json \
  --model openai/gpt-4o \
  --mask 111111
```

You can specify any OpenRouter model with the --model flag. If none is specified, the script defaults to openai/gpt-4o. Check out the available models here: https://openrouter.ai/

How OpenRouter works:
* If the model parameter is omitted, the user or payer’s default is used. Otherwise, remember to select a value for model from the supported models or API, and include the organization prefix. OpenRouter will select the least expensive and best GPUs available to serve the request, and fall back to other providers or GPUs if it receives a 5xx response code or if you are rate-limited.
* https://openrouter.ai/docs/api-reference/overview 


# To-dos
* Update the evaluate.py script to automatially handle the new output structure
