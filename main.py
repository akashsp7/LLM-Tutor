import os
import json
import sys
import argparse
from typing import Dict
from state import EvaluationState
from workflow import build_evaluation_workflow
from dotenv import load_dotenv

load_dotenv()

def evaluate_assignment(file_path: str, requirements_file: str) -> Dict:
    """Main function to evaluate a student assignment."""
    with open(file_path, 'r') as f:
        code = f.read()
    
    student_name = os.path.basename(file_path).split('_')[0]
    
    with open(requirements_file, 'r') as f:
        requirements = json.load(f)
    
    initial_state = EvaluationState(
        student_code=code,
        file_path=file_path,
        student_name=student_name,
        requirements=requirements,
        execution_result={},
        syntax_score=0,
        style_score=0,
        requirements_score=0,
        visualization_score=None,
        final_score=0,
        feedback="",
        error_analysis=None
    )
    
    workflow = build_evaluation_workflow()
    graph = workflow.compile()
    final_state = graph.invoke(initial_state)
    
    return {
        "student_name": final_state["student_name"],
        "final_score": final_state["final_score"],
        "feedback": final_state["feedback"],
        "error_analysis": final_state["error_analysis"]
    }
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Evaluate a Python assignment.')
    parser.add_argument('file_path', help='Path to the Python file to evaluate')
    parser.add_argument('--requirements', '-r', default='requirements.json',
                        help='Path to the requirements JSON file (default: requirements.json)')
    parser.add_argument('--output', '-o', help='Path to save the evaluation results (optional)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.file_path):
        print(f"Error: File {args.file_path} does not exist.")
        sys.exit(1)
    
    if not os.path.exists(args.requirements):
        print(f"Error: Requirements file {args.requirements} does not exist.")
        sys.exit(1)
    
    try:
        result = evaluate_assignment(args.file_path, args.requirements)
        

        print(f"\n{'='*50}")
        print(f"EVALUATION RESULTS FOR: {os.path.basename(args.file_path)}")
        print(f"{'='*50}")
        print(f"Student: {result['student_name']}")
        print(f"Score: {result['final_score']}/100")
        print(f"\nFEEDBACK:\n")
        print(result['feedback'])
        
        if result.get('error_analysis'):
            print(f"\nERROR ANALYSIS:\n")
            print(result['error_analysis'])
        

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\nResults saved to {args.output}")
            
    except Exception as e:
        print(f"Error during evaluation: {str(e)}")
        sys.exit(1)