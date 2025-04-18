# Import the os module to access environment variables
import os

# Retrieve the OpenRouter API key from the system's environment variables.
# The environment variable 'OPENROUTER_API_KEY' must be set before running the application.
# This key is required to authenticate requests to the OpenRouter API.
# 
# Instructions for setting the environment variable:
# - On Windows (Command Prompt): set OPENROUTER_API_KEY=your_api_key
# - On Windows (PowerShell): $env:OPENROUTER_API_KEY="your_api_key"
# - On Linux/Mac (Terminal): export OPENROUTER_API_KEY=your_api_key
# 
# Replace 'your_api_key' above with the actual API key provided by OpenRouter.
# Note: check your ~/.bashrc file or ~/.bash_profile to ensure the variable is set for all sessions.
# Ensure the environment variable is set in the same session where the script will run.
API_KEY = os.getenv('OPENROUTER_API_KEY')
