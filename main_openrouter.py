"""
Script:     main.py
Author:     Van Q. Truong
Created:     2025-04-18
Purpose:    Adapted from GeneGPT to use OpenRouter API to teach LLMs to use NCBI API.

Description:
This script queries the OpenRouter API to generate genomic prompts and responses.
It uses a masking system to dynamically control the content of the prompts and supports
querying multiple tasks from an input JSON file. Results are saved in structured output
directories for further analysism with informative logging in metadata files.
"""

import os
import re
import json
import time
import argparse
import requests
import urllib.request
from pathlib import Path
from datetime import datetime
from config import OPENROUTER_API_KEY

# Constants
API_RATE_LIMIT_DELAY = 0.5  # Default delay between OpenRouter API calls (in seconds)
# NOTE: Adjust based on OpenRouter rate limits:
# Free model: ~20 req/min, Paid: 1 req/sec per credit (e.g. 10 credits = 10 req/sec)
# See: https://openrouter.ai/docs#rate-limits
OPENROUTER_URL = "https://openrouter.ai/api/v1/completions"
CUTOFF_LENGTH = 18000  # Maximum character length for prompts

def fetch_url(url, delay=1):
    """
    Fetch data from a given URL with an optional delay.

    Args:
        url (str): The URL to fetch data from.
        delay (int): Time to wait before making the request (default: 1 second).

    Returns:
        str: The response content from the URL.
    """
    time.sleep(delay)  # Delay added before NCBI sample API calls
    req = urllib.request.Request(url.replace(" ", "+"))
    with urllib.request.urlopen(req) as response:
        return response.read()

def query_openrouter(prompt, model="openai/gpt-4o", max_tokens=512, temperature=0):
    """
    Query the OpenRouter API with a given prompt and model.

    Args:
        prompt (str): The input prompt for the model.
        model (str): The OpenRouter model to use (default: "openai/gpt-4o").
        max_tokens (int): Maximum number of tokens to generate (default: 512).
        temperature (float): Sampling temperature for randomness (default: 0).

    Returns:
        dict: The JSON response from the OpenRouter API.
        dict: The payload sent to the API.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stop": ['->', '\n\nQuestion'],
        "n": 1
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json(), payload
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] OpenRouter API call failed: {e}")
        return None, payload

def get_prompt_header(mask):
    """
    Generate the prompt header based on the provided mask.

    Args:
        mask (list): A list of booleans indicating which components to include in the prompt.

    Returns:
        str: The generated prompt header.
    """
    # Example API calls to fetch data
    url_1 = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gene&retmax=5&retmode=json&sort=relevance&term=LMP10'
    call_1 = fetch_url(url_1)

    url_2 = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=gene&retmax=5&retmode=json&id=19171,5699,8138'
    call_2 = fetch_url(url_2)

    url_3 = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=snp&retmax=10&retmode=json&id=1217074595'
    call_3 = fetch_url(url_3)

    url_4 = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=omim&retmax=20&retmode=json&sort=relevance&term=Meesmann+corneal+dystrophy'
    call_4 = fetch_url(url_4)

    url_5 = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=omim&retmax=20&retmode=json&id=618767,601687,300778,148043,122100'
    call_5 = fetch_url(url_5)

    url_6 = 'https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi?CMD=Put&PROGRAM=blastn&MEGABLAST=on&DATABASE=nt&FORMAT_TYPE=XML&QUERY=ATTCTGCCTTTAGTAATTTGATGACAGAGACTTCTTGGGAACCACAGCCAGGGAGCCACCCTTTACTCCACCAACAGGTGGCTTATATCCAATCTGAGAAAGAAAGAAAAAAAAAAAAGTATTTCTCT&HITLIST_SIZE=5'
    call_6 = fetch_url(url_6)
    rid = re.search('RID = (.*)\n', call_6.decode('utf-8')).group(1)

    url_7 = f'https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi?CMD=Get&FORMAT_TYPE=Text&RID={rid}'
    time.sleep(30)  # Delay to ensure BLAST results are available from NCBI
    call_7 = fetch_url(url_7)

    prompt = 'Your task is to use NCBI Web APIs (e.g., Eutils, BLAST) to answer genomic questions.\n'

    if mask[0]:
        prompt += 'You can call Eutils by: "[https://eutils.ncbi.nlm.nih.gov/entrez/eutils/{esearch|efetch|esummary}.fcgi?db={gene|snp|omim}&retmax={}&{term|id}={term|id}]".\n'
        prompt += 'esearch: input is a search term and output is database id(s).\n'
        prompt += 'efetch/esummary: input is database id(s) and output is full records or summaries.\n'
        prompt += 'Database: gene is for genes, snp is for SNPs, and omim is for genetic diseases.\n\n'

    if mask[1]:
        prompt += 'For DNA sequences, use BLAST: "[https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi?CMD={Put|Get}&PROGRAM=blastn&MEGABLAST=on&DATABASE=nt&FORMAT_TYPE={XML|Text}&QUERY={sequence}&HITLIST_SIZE={n}]".\n'
        prompt += 'BLAST maps DNA sequences to chromosome locations.\n\n'

    if any(mask[2:]):
        prompt += 'Here are some examples:\n\n'

    if mask[2]:
        prompt += f'Question: What is the official gene symbol of LMP10?\n[{url_1}]->[{call_1}]\n[{url_2}]->[{call_2}]\nAnswer: PSMB10\n\n'

    if mask[3]:
        prompt += f'Question: Which gene is SNP rs1217074595 associated with?\n[{url_3}]->[{call_3}]\nAnswer: LINC01270\n\n'

    if mask[4]:
        prompt += f'Question: What are genes related to Meesmann corneal dystrophy?\n[{url_4}]->[{call_4}]\n[{url_5}]->[{call_5}]\nAnswer: KRT12, KRT3\n\n'

    if mask[5]:
        prompt += f'Question: Align the DNA sequence to the human genome:ATTCTGC...\n[{url_6}]->[{rid}]\n[{url_7}]->[{call_7}]\nAnswer: chr15:91950805-91950932\n\n'

    return prompt

def get_output_path(model, input_file, mask_str):
    """
    Generate the output directory path based on the model, input file, and mask.

    Args:
        model (str): The model name.
        input_file (str): The input file path.
        mask_str (str): The mask string.

    Returns:
        Path: The output directory path.
    """
    name = Path(input_file).stem
    return Path("outputs") / f"model={model.replace('/', '_')}" / f"file={name}" / f"mask={mask_str}"

def run_tasks(input_file, model, output_dir, prompt):
    skipped_log = output_dir / "skipped_urls.json"
    skipped_entries = []
    """
    Run tasks from the input file and save results to the output directory.

    Args:
        input_file (str): Path to the input JSON file containing tasks.
        model (str): The model to use for querying.
        output_dir (Path): The output directory to save results.
        prompt (str): The base prompt to use for tasks.
    """
    with open(input_file) as f:
        tasks = json.load(f)

    # Optional mapping from internal keys to human-readable file names
    task_name_map = {
        "gene_alias": "Gene alias",
        "gene_name_conversion": "Gene name conversion",
        "gene_location": "Gene location",
        "snp_location": "SNP location",
        "gene_disease_association": "Gene disease association",
        "protein_coding_genes": "Protein-coding genes",
        "gene_snp_association": "Gene SNP association",
        "human_genome_dna_alignment": "Human genome DNA alignment",
        "multi_species_dna_alignment": "Multi-species DNA alignment"
    }

    for task, qas in tasks.items():
        pretty_name = task_name_map.get(task, task.replace('_', ' ').title())
        task_file = output_dir / f"{pretty_name}.json"
        if task_file.exists():
            existing = json.load(open(task_file))
            if len(existing) == 50:
                continue

        print(f"\n[RUNNING] Task: {task}")
        results = []
        for question, answer in qas.items():
            print(f"\n--- Question ---\n{question}")
            result = process_question(question, answer, prompt, output_dir, task, skipped_entries)
            results.append(result)

            with open(task_file, 'w') as f:
                 json.dump(results, f, indent=4)

    # Save skipped URL logs if any
    if skipped_entries:
        with open(skipped_log, 'w') as f:
            json.dump(skipped_entries, f, indent=2)

def process_question(question, answer, base_prompt, output_dir, task_name, skipped_entries):
    """
    Process a single question by querying the OpenRouter API.

    Args:
        question (str): The question to process.
        answer (str): The expected answer.
        base_prompt (str): The base prompt to use.
        output_dir (Path): The output directory to save raw input/output.
        task_name (str): The name of the task.

    Returns:
        list: The result of the processing.
    """
    full_prompt = f"{base_prompt}Question: {question}\n"
    prompts = []
    call_count = 0

    while call_count < 10:
        if len(full_prompt) > CUTOFF_LENGTH:
            full_prompt = full_prompt[-CUTOFF_LENGTH:]

        response, payload = query_openrouter(full_prompt)
        time.sleep(0.5)  # Prevent hitting OpenRouter rate limits
        if not response:
            return [question, answer, 'apiError', prompts]

        output_text = response['choices'][0]['text']
        print(output_text)
        prompts.append([full_prompt, output_text])
        call_count += 1

        # Save raw input/output to a file
        pretty_task_name = task_name.replace('_', ' ').title()
        io_log_dir = output_dir / "raw_io" / pretty_task_name
        io_log_dir.mkdir(parents=True, exist_ok=True)
        call_time = datetime.utcnow().isoformat()
        with open(io_log_dir / f"q{call_count:02d}.json", "w") as f:
            json.dump({"input": payload, "output": output_text, "time_utc": call_time, "usage": response.get('usage', {})}, f, indent=2)

        urls = re.findall(r'\[(https?://[^\[\]]+)\]', output_text)
        if not urls:
            skipped_entries.append({
                "question": question,
                "url": None,
                "reason": "no valid URL in model output"
            })
            return [question, answer, output_text, prompts]

        url = urls[0]
        if 'blast' in url and 'Get' in url:
            time.sleep(30)

                # Skip malformed or incomplete URLs with placeholders
        if '{' in url or '}' in url:
            print(f"[SKIP] URL contains unresolved placeholder: {url}")
            skipped_entries.append({
                "question": question,
                "url": url,
                "reason": "placeholder in URL"
            })
            return [question, answer, output_text, prompts]

        result = fetch_url(url)
        if 'blast' in url and 'Put' in url:
            rid = re.search('RID = (.*)\n', result.decode('utf-8'))
            result = rid.group(1) if rid else 'No RID'

        if len(result) > 10000:
            result = result[:10000]

        full_prompt += f"{output_text}->[{result}]\n"

    return [question, answer, 'numError', prompts]

def main():
    """
    Main entry point for the script. Parses arguments and runs tasks.
    """
    parser = argparse.ArgumentParser(description="Query OpenRouter with NCBI-style genomic prompts")
    parser.add_argument("--input", type=str, required=True, help="Path to input JSON file")
    parser.add_argument("--model", type=str, default="openai/gpt-4o", help="OpenRouter model name")
    parser.add_argument("--mask", type=str, required=True, help="6-digit binary mask for prompt content (e.g., 110011)")

    args = parser.parse_args()

    if not re.fullmatch(r"[01]{6}", args.mask):
        raise ValueError("Mask must be a 6-digit binary string (e.g., 110011)")

    mask = [bit == "1" for bit in args.mask]
    prompt = get_prompt_header(mask)

    output_dir = get_output_path(args.model, args.input, args.mask)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save global metadata
    metadata = {
        "input_file": args.input,
        "model": args.model,
        "mask": args.mask,
        "started_at": datetime.utcnow().isoformat(),
        "mask_legend": {
            "0": "Eutils instructions",
            "1": "BLAST instructions",
            "2": "Gene alias example",
            "3": "SNP-gene example",
            "4": "Gene-disease example",
            "5": "BLAST alignment example"
        },
        "mask_translation": {
            "Eutils instructions": mask[0],
            "BLAST instructions": mask[1],
            "Gene alias example": mask[2],
            "SNP-gene example": mask[3],
            "Gene-disease example": mask[4],
            "BLAST alignment example": mask[5]
        }
    }
    with open(output_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    run_tasks(args.input, args.model, output_dir, prompt)

if __name__ == "__main__":
    main()
