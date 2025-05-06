# LLM Tutor

## Overview
LLM Tutor is an automated system for evaluating student Python code submissions using Large Language Models (LLMs). It provides detailed feedback on code execution, syntax, style, requirement fulfillment, and visualization quality.

## Features
- Executes student code in a sandbox environment
- Evaluates code syntax and style according to best practices
- Assesses requirement fulfillment based on assignment criteria
- Evaluates data visualizations if present
- Generates comprehensive feedback with actionable suggestions

## Architecture
The project is built as a workflow using the langgraph library, with different agents handling specific aspects of code evaluation.

## Usage
```bash
python main.py /path/to/student_submission.py --requirements requirements.json
```

## Evaluation Criteria
- Syntax: 60 points (20% of final score)
- Style: 40 points (10% of final score)
- Requirements: 100 points (50% of final score)
- Visualization: 100 points (20% of final score, if applicable)

## Installation
1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your OpenAI API key in a `.env` file

## Dependencies
- langchain_openai
- langgraph
- pydantic
- python-dotenv
- openai
