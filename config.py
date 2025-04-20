"""
Script:     config.py
Author:     Van Q. Truong
Created:    2025-04-18
Purpose:    Retrieve API keys from system environment variables for OpenRouter and OpenAI.

Description:
This script safely loads API keys for OpenAI and OpenRouter from your system environment variables.

Instructions:
Set environment variables before running:
  - Windows (CMD): set OPENROUTER_API_KEY=your_api_key
  - Windows (PowerShell): $env:OPENROUTER_API_KEY="your_api_key"
  - Linux/Mac: export OPENROUTER_API_KEY=your_api_key
"""

import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
