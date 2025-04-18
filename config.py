"""
Script:     config.py
Author:     Van Q. Truong
Created:    2025-04-18
Purpose:    Retrieve API keys from system environment variables for OpenRouter and OpenAI.

Description:
This scrpipt retrieves the API keys for OpenRouter and OpenAI from the system's environment variables.

Generally, it's not good practice to hard code your API key in the code to prevent leaking it online.
Anyone with your special API key can access your account and rack up charges. 

The environment variable 'OPENROUTER_API_KEY' must be set before running the application.
This key is required to authenticate requests to the OpenAI or OpenRouter API.

General instructions for setting the environment variable:
- On Windows (Command Prompt): set OPENROUTER_API_KEY=your_api_key
- On Windows (PowerShell): $env:OPENROUTER_API_KEY="your_api_key"
- On Linux/Mac (Terminal): export OPENROUTER_API_KEY=your_api_key

Replace 'your_api_key' above with the actual API key provided by OpenRouter.
Follow the same pattern for setting the 'OPENAI_API_KEY' environment variable.
Note: check your ~/.bashrc file or ~/.bash_profile to ensure the variable is set for all sessions.
"""
# Import the os module to access environment variables
import os

# Retrieve API keys from the system's environment variables.
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
API_KEY = os.getenv('OPENROUTER_API_KEY')
