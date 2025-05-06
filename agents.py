from state import EvaluationState
from prompts import SYNTAX_STYLE_TEMPLATE, REQUIREMENTS_TEMPlATE, VISUALIZATION_TEMPLATE
from pydantic_objects import SyntaxStyleEvaluation, RequirementsEvaluation, VisualizationEvaluation
import re
import tempfile
import subprocess
import sys
import os
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
import re
import json

syntax_style_parser = PydanticOutputParser(pydantic_object=SyntaxStyleEvaluation)
requirements_parser = PydanticOutputParser(pydantic_object=RequirementsEvaluation)
visualization_parser = PydanticOutputParser(pydantic_object=VisualizationEvaluation)

def extract_json_from_backticks(text):
    # Extracts content between ```json and ```
    match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if match:
        return match.group(1)
    else:
        return text  # fallback: return original if not wrapped

def input_node(state: EvaluationState) -> EvaluationState:
    """Processes the initial student code submission and extracts metadata."""
    print(f"Processing submission for student: {state['student_name']}")
    
    code = state["student_code"]
    
    # File size
    code_size_kb = len(code) / 1024
    print(f"Code size: {code_size_kb:.2f} KB")
    
    # Extract imports
    import_pattern = r'^import\s+(\w+)|^from\s+(\w+).*import'
    imports = set()
    for line in code.split('\n'):
        match = re.search(import_pattern, line)
        if match:
            # Get whichever group matched (import X or from X import)
            module = match.group(1) if match.group(1) else match.group(2)
            imports.add(module)
    
    # Detect visualization libraries
    viz_libraries = {'matplotlib', 'seaborn', 'plotly', 'bokeh', 'altair', 'pygal'}
    has_viz = bool(imports.intersection(viz_libraries))
    
    # Extract visualization imports specifically
    viz_imports = list(imports.intersection(viz_libraries))
    
    # Count functions defined in the code
    function_pattern = r'^def\s+(\w+)'
    functions = []
    for line in code.split('\n'):
        match = re.search(function_pattern, line)
        if match:
            functions.append(match.group(1))
    
    # Count classes defined in the code
    class_pattern = r'^class\s+(\w+)'
    classes = []
    for line in code.split('\n'):
        match = re.search(class_pattern, line)
        if match:
            classes.append(match.group(1))
    
    print(f"Found {len(imports)} imports, {len(functions)} functions, and {len(classes)} classes")
    if has_viz:
        print("Visualization libraries detected")
    
    # Create a new state with all important data as top-level keys
    return {
        **state,
        "has_visualizations": has_viz,
        "viz_imports": viz_imports,
        "import_count": len(imports),
        "function_count": len(functions),
        "class_count": len(classes),
        "code_size_kb": code_size_kb
    }

def code_execution_node(state: EvaluationState) -> EvaluationState:
    """Executes the student code to check for runtime errors."""
    print(f"Executing code for {state['student_name']}...")
    
    # Create a temporary file to execute the code
    with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as temp_file:
        temp_file_path = temp_file.name
        temp_file.write(state['student_code'])
    
    try:
        # Execute the code with a timeout
        result = subprocess.run(
            [sys.executable, temp_file_path],
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        # Check if execution was successful
        if result.returncode == 0:
            state['execution_result'] = {
                'success': True,
                'output': result.stdout,
                'error': None
            }
        else:
            state['execution_result'] = {
                'success': False,
                'output': result.stdout,
                'error': result.stderr
            }
    except subprocess.TimeoutExpired:
        state['execution_result'] = {
            'success': False,
            'output': '',
            'error': 'Code execution timed out after 30 seconds'
        }
    except Exception as e:
        state['execution_result'] = {
            'success': False,
            'output': '',
            'error': str(e)
        }
    
    # Clean up the temporary file
    os.unlink(temp_file_path)
    
    return state

def analyze_errors(state: EvaluationState) -> EvaluationState:
    """Analyzes code that failed to execute and provides detailed error feedback."""
    print(f"Analyzing errors in {state['student_name']}'s code...")
    
    error_message = state["execution_result"]["error"]
    
    # Basic error categorization
    if "SyntaxError" in error_message:
        analysis = "Your code contains syntax errors. Check for missing colons, parentheses, or incorrect indentation."
    elif "NameError" in error_message:
        analysis = "Your code references variables or functions that are not defined."
    elif "ImportError" in error_message or "ModuleNotFoundError" in error_message:
        analysis = "Your code attempts to import modules that are not available."
    elif "TypeError" in error_message:
        analysis = "Your code has type mismatches. Check your function arguments and operations."
    elif "IndexError" in error_message or "KeyError" in error_message:
        analysis = "Your code attempts to access list indices or dictionary keys that don't exist."
    elif "ZeroDivisionError" in error_message:
        analysis = "Your code attempts to divide by zero."
    elif "timeout" in error_message.lower():
        analysis = "Your code took too long to execute (>30 seconds). Check for infinite loops."
    else:
        analysis = f"Your code failed with the following error: {error_message}"
    
    state["error_analysis"] = analysis
    
    # Assign a base score for failing code
    state["final_score"] = 0
    state["feedback"] = f"Your code failed to execute. {analysis} Fix these errors first before addressing other requirements."
    
    return state

def syntax_style_agent(state: EvaluationState) -> EvaluationState:
    """Evaluates code syntax and style according to best practices."""
    print(f"Evaluating syntax and style for {state['student_name']}...")
    
    code = state["student_code"]
    
    # Initialize the LLM
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.1
    )
    
    execution_success = state["execution_result"]["success"]
    
    # Shouldn't be used now since if code fails, it goes directly to feedback
    max_syntax_score = 40 if not execution_success else 60
    
    try:

        prompt = SYNTAX_STYLE_TEMPLATE.format(code=code)

        response = llm.invoke(prompt)
        
        raw_content = response.content  
        clean_json_str = extract_json_from_backticks(raw_content)

        # Now parse the clean JSON
        evaluation = syntax_style_parser.parse(clean_json_str)
        
        # print("\n--- RAW LLM evaluation for syntax_style_agent (Try block) ---")
        # print(evaluation)
        # evaluation = syntax_style_parser.parse(response.content)
        
        # Cap
        syntax_score = min(evaluation.syntax_score, max_syntax_score)
        style_score = evaluation.style_score
        
        print(f"Syntax score: {syntax_score}/60, Style score: {style_score}/40")
        
        return {
            **state,
            "syntax_score": syntax_score,
            "style_score": style_score,
            "syntax_feedback": {
                "score": syntax_score,
                "explanation": evaluation.syntax_feedback,
                "improvements": evaluation.syntax_improvements
            },
            "style_feedback": {
                "score": style_score,
                "explanation": evaluation.style_feedback,
                "improvements": evaluation.style_improvements
            }
        }
    
    except Exception as e:

        print(f"Error in syntax_style_agent: {str(e)}")
        
        fallback_syntax_score = 30 if execution_success else 20
        fallback_style_score = 20
        
        return {
            **state,
            "syntax_score": fallback_syntax_score,
            "style_score": fallback_style_score,
            "syntax_feedback": {
                "score": fallback_syntax_score,
                "explanation": "An error occurred during evaluation.",
                "improvements": ["Review your code for syntax errors."]
            },
            "style_feedback": {
                "score": fallback_style_score,
                "explanation": "An error occurred during evaluation.",
                "improvements": ["Review your code for style issues."]
            }
        }

def requirements_agent(state: EvaluationState) -> EvaluationState:
    """Evaluates how well the code meets the assignment requirements."""
    print(f"Evaluating requirements fulfillment for {state['student_name']}...")
    
    code = state["student_code"]
    requirements = state["requirements"]
    execution_success = state["execution_result"]["success"]
    
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.1
    )
    
    requirements_text = ""
    for i, req in enumerate(requirements.get("criteria", []), 1):
        requirements_text += f"{i}. {req}\n"
    
    if not requirements_text:
        requirements_text = "Read the data files and extract metrics and visualizations to provide significant insights from it."
    
    try:
        prompt = REQUIREMENTS_TEMPlATE.format(
            requirements_text=requirements_text,
            code=code,
            execution_status="Successful" if execution_success else "Failed"
        )
        
        response = llm.invoke(prompt)
        
        raw_content = response.content  
        clean_json_str = extract_json_from_backticks(raw_content)

        evaluation = requirements_parser.parse(clean_json_str)
        # print("\n--- RAW LLM evaluation for requirements_agent (Try block) ---")
        # print(evaluation)
        # evaluation = requirements_parser.parse(response.content)
        
        # Apply a penalty if code execution failed
        requirements_score = evaluation.requirements_score
        if not execution_success:
            requirements_score = min(requirements_score, 60)
            
        print(f"Requirements score: {requirements_score}/100")
        
        return {
            **state,
            "requirements_score": requirements_score,
            "requirements_feedback": {
                "score": requirements_score,
                "overall_assessment": evaluation.overall_assessment,
                "strengths": evaluation.strengths,
                "weaknesses": evaluation.weaknesses,
                "improvement_suggestions": evaluation.improvement_suggestions
            }
        }
    
    except Exception as e:
        print(f"Error in requirements_agent: {str(e)}")
        default_score = 50 if execution_success else 30
        
        return {
            **state,
            "requirements_score": default_score,
            "requirements_feedback": {
                "score": default_score,
                "overall_assessment": "An error occurred during evaluation.",
                "strengths": ["N/A"],
                "weaknesses": ["N/A"],
                "improvement_suggestions": ["Review assignment requirements and ensure your code addresses them."]
            }
        }

def visualization_agent(state: EvaluationState) -> EvaluationState:

    """Evaluates the quality and effectiveness of data visualizations."""
    print(f"Evaluating visualizations for {state['student_name']}...")
    
    code = state["student_code"]
    execution_success = state["execution_result"]["success"]
    
    # Check if visualizations were detected
    has_viz = state.get("has_visualizations", False)
    if not has_viz:
        print("No visualizations detected, skipping visualization evaluation")

        return {
            **state,
            "visualization_score": None
        }
    
    viz_libraries = state.get("viz_imports", [])
    
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.1
    )
    
    try:
        prompt = VISUALIZATION_TEMPLATE.format(
            libraries=", ".join(viz_libraries),
            execution_status="Successful" if execution_success else "Failed",
            code=code
        )
        
        response = llm.invoke(prompt)
        raw_content = response.content  
        clean_json_str = extract_json_from_backticks(raw_content)

        evaluation = visualization_parser.parse(clean_json_str)
        # print("\n--- RAW LLM evaluation for visualization_agent (Try block) ---")
        # print(evaluation)
        # evaluation = visualization_parser.parse(response.content)
        
        visualization_score = evaluation.visualization_score
        if not execution_success:
            visualization_score = min(visualization_score, 50)
            
        print(f"Visualization score: {visualization_score}/100")
        
        # Return new state with updated values
        return {
            **state,
            "visualization_score": visualization_score,
            "visualization_feedback": {
                "score": visualization_score,
                "clarity_assessment": evaluation.clarity_assessment,
                "insight_assessment": evaluation.insight_assessment,
                "technical_assessment": evaluation.technical_assessment,
                "strengths": evaluation.strengths,
                "improvement_suggestions": evaluation.improvement_suggestions
            }
        }
    
    except Exception as e:
        print(f"Error in visualization_agent: {str(e)}")
        default_score = 50 if execution_success else 30
        
        return {
            **state,
            "visualization_score": default_score,
            "visualization_feedback": {
                "score": default_score,
                "clarity_assessment": "An error occurred during evaluation.",
                "insight_assessment": "An error occurred during evaluation.",
                "technical_assessment": "An error occurred during evaluation.",
                "strengths": ["Visualization libraries were imported correctly."],
                "improvement_suggestions": ["Review visualization best practices."]
            }
        }

def feedback_agent(state: EvaluationState) -> EvaluationState:
    """Synthesizes all evaluations into coherent feedback and a final score."""
    print(f"Generating final feedback for {state['student_name']}...")

    if state.get("error_analysis"):
        return state

    syntax_weight = 0.2
    style_weight = 0.1
    requirements_weight = 0.5
    visualization_weight = 0.2
    
    has_viz = state.get("visualization_score") is not None

    if has_viz:
        final_score = int(
            (state["syntax_score"] / 60) * 100 * syntax_weight +
            (state["style_score"] / 40) * 100 * style_weight +
            (state["requirements_score"] / 100) * 100 * requirements_weight +
            (state["visualization_score"] / 100) * 100 * visualization_weight
        )
    else:
        adjusted_syntax_weight = syntax_weight / (1 - visualization_weight)
        adjusted_style_weight = style_weight / (1 - visualization_weight)
        adjusted_requirements_weight = requirements_weight / (1 - visualization_weight)

        final_score = int(
            (state["syntax_score"] / 60) * 100 * adjusted_syntax_weight +
            (state["style_score"] / 40) * 100 * adjusted_style_weight +
            (state["requirements_score"] / 100) * 100 * adjusted_requirements_weight
        )

    final_score = max(0, min(100, final_score))
    state["final_score"] = final_score

    feedback = []
    feedback.append(f"# Evaluation for {state['student_name']}")
    feedback.append(f"## Overall Score: {final_score}/100")
    grade = "A" if final_score >= 90 else "B" if final_score >= 80 else "C" if final_score >= 70 else "D" if final_score >= 60 else "F"
    feedback.append(f"## Grade: {grade}")
    feedback.append("## Summary")

    if state["execution_result"]["success"]:
        feedback.append("✅ Your code executed successfully.")
    else:
        feedback.append("❌ Your code failed to execute. Fix errors first.")

    strengths = []
    improvements = []

    def unpack_feedback(feedback_entry, score_title):
        section = []
        if isinstance(feedback_entry, dict):
            score = feedback_entry.get("score")
            explanation = feedback_entry.get("explanation") or feedback_entry.get("overall_assessment", "")
            if score is not None:
                section.append(f"\n## {score_title}: {score}")
            if explanation:
                section.append(explanation)

            if "improvements" in feedback_entry:
                for imp in feedback_entry.get("improvements", []):
                    improvements.append(f"{score_title}: {imp}")
            if "strengths" in feedback_entry:
                for strength in feedback_entry.get("strengths", []):
                    strengths.append(strength)
            if "weaknesses" in feedback_entry:
                for weakness in feedback_entry.get("weaknesses", []):
                    improvements.append(f"{score_title}: {weakness}")
            if "improvement_suggestions" in feedback_entry:
                for suggestion in feedback_entry.get("improvement_suggestions", []):
                    improvements.append(f"{score_title}: {suggestion}")

            if "clarity_assessment" in feedback_entry:
                section.append("### Visual Clarity\n" + feedback_entry["clarity_assessment"])
            if "insight_assessment" in feedback_entry:
                section.append("### Insight Generation\n" + feedback_entry["insight_assessment"])
            if "technical_assessment" in feedback_entry:
                section.append("### Technical Implementation\n" + feedback_entry["technical_assessment"])
        elif isinstance(feedback_entry, str):
            section.append(f"\n## {score_title}")
            section.append(feedback_entry)
        else:
            section.append(f"\n## {score_title}")
            section.append("No feedback available.")
        return section

    feedback += unpack_feedback(state.get("syntax_feedback"), "Syntax Evaluation")
    feedback += unpack_feedback(state.get("style_feedback"), "Style Evaluation")
    feedback += unpack_feedback(state.get("requirements_feedback"), "Requirements Evaluation")
    
    if has_viz:
        feedback += unpack_feedback(state.get("visualization_feedback"), "Visualization Evaluation")

    if strengths:
        feedback.append("\n## Strengths")
        for s in strengths[:3]:
            feedback.append(f"- {s}")

    if improvements:
        feedback.append("\n## Areas for Improvement")
        for imp in improvements[:5]:
            feedback.append(f"- {imp}")

    state["feedback"] = "\n".join(feedback)
    return state


# def feedback_agent(state: EvaluationState) -> EvaluationState:
#     """Synthesizes all evaluations into coherent feedback and a final score."""
#     print(f"Generating final feedback for {state['student_name']}...")
    
#     # Debugging: Print what's in the state that we'll use for feedback
#     print("DEBUG feedback_agent state keys:", list(state.keys()))
#     print("DEBUG syntax_feedback:", state.get("syntax_feedback"))
#     print("DEBUG style_feedback:", state.get("style_feedback"))
#     print("DEBUG requirements_feedback:", state.get("requirements_feedback"))
#     print("DEBUG visualization_feedback:", state.get("visualization_feedback"))