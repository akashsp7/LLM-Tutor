from state import EvaluationState

def code_executed_successfully(state: EvaluationState) -> str:
    """Determines next step based on whether code executed successfully."""
    if state["execution_result"]["success"]:
        print(f"Code for {state['student_name']} executed successfully. Proceeding with evaluation.")
        return "success"
    else:
        print(f"Code for {state['student_name']} failed to execute. Proceeding with error analysis.")
        return "error"

def has_visualizations(state: EvaluationState) -> bool:
    """Determines if the code contains visualizations that should be evaluated."""
    has_viz = state.get("has_visualizations", False)
    return has_viz
