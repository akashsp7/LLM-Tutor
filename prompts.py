from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic_objects import SyntaxStyleEvaluation, RequirementsEvaluation, VisualizationEvaluation

syntax_style_parser = PydanticOutputParser(pydantic_object=SyntaxStyleEvaluation)
requirements_parser = PydanticOutputParser(pydantic_object=RequirementsEvaluation)
visualization_parser = PydanticOutputParser(pydantic_object=VisualizationEvaluation)


SYNTAX_STYLE_TEMPLATE = PromptTemplate.from_template(
"""
You are a Python code evaluator focusing on syntax correctness and style best practices.

Please evaluate the following Python code on two dimensions:

1. Syntax correctness (60 points):
    - Is the code syntactically valid?
    - Does it use proper indentation?
    - Are there any obvious syntax errors?

2. Readability and style (40 points):
    - Does the code follow PEP 8 conventions?
    - Are variable and function names descriptive and consistent?
    - Is the code properly commented?
    - Is the overall structure logical and easy to follow?

{format_instructions}

Here is the code to evaluate:

```python
{code}
```
""",
partial_variables={"format_instructions": syntax_style_parser.get_format_instructions()}
)
    
REQUIREMENTS_TEMPlATE = PromptTemplate.from_template(
"""
You are a Python assignment evaluator focusing on how well the code fulfills the specified requirements.

Assignment Requirements:
{requirements_text}

Please evaluate the following Python code based on how well it meets these requirements.
Consider the following aspects:

1. Functionality (Does the code implement all required features?)
2. Completeness (Are all requirements addressed?)
3. Correctness (Are the implementations accurate?)
4. Approach (Is the solution approach appropriate and efficient?)

Give a score out of 100 points.

Note: The code execution status is: {execution_status}

{format_instructions}

Here is the code to evaluate:

```python
{code}
```
""",
partial_variables={"format_instructions": requirements_parser.get_format_instructions()}
)
    
VISUALIZATION_TEMPLATE = PromptTemplate.from_template(
"""
You are a data visualization expert evaluating Python code that creates visualizations.

Please evaluate the following Python code on these visualization aspects:

1. Visual clarity (30 points):
    - Are the visualizations clear and easy to interpret?
    - Do they have proper labels, titles, and legends?
    - Is the choice of visualization type appropriate for the data?

2. Insight generation (40 points):
    - Do the visualizations reveal meaningful patterns or insights?
    - Is there a clear purpose for each visualization?
    - Do the visualizations help answer important questions about the data?

3. Technical implementation (30 points):
    - Is the visualization code well-structured and efficient?
    - Are appropriate visualization libraries and functions used?
    - Is there customization beyond default settings?

Libraries detected: {libraries}

Note: The code execution status is: {execution_status}

{format_instructions}

Here is the code to evaluate:

```python
{code}
```
""",
partial_variables={"format_instructions": visualization_parser.get_format_instructions()}
)