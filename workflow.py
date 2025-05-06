from state import EvaluationState
from router import code_executed_successfully, has_visualizations
from agents import input_node, code_execution_node, analyze_errors, syntax_style_agent
from agents import requirements_agent, visualization_agent, feedback_agent
from langgraph.graph import StateGraph, START, END

def build_evaluation_workflow() -> StateGraph:
    """Constructs the full evaluation workflow graph."""

    workflow = StateGraph(EvaluationState)
    
    # Add all nodes
    workflow.add_node("input", input_node)
    workflow.add_node("code_execution", code_execution_node)
    workflow.add_node("analyze_errors", analyze_errors)
    workflow.add_node("syntax_style", syntax_style_agent)
    workflow.add_node("requirements_agent", requirements_agent)
    workflow.add_node("visualization", visualization_agent)
    workflow.add_node("feedback_agent", feedback_agent)
    
    # Edges (flow)
    workflow.add_edge(START, "input")
    workflow.add_edge("input", "code_execution")
    
    # Conditional check 1
    workflow.add_conditional_edges(
        "code_execution",
        code_executed_successfully,
        {
            "success": "syntax_style",  # If success, continue to evaluation
            "error": "analyze_errors"    # If error, analyze it
        }
    )
    
    # After error analysis (skipping other evaluations)
    workflow.add_edge("analyze_errors", "feedback_agent")
    
    # Standard flow
    workflow.add_edge("syntax_style", "requirements_agent")
    
    # Conditional check 2
    workflow.add_conditional_edges(
        "requirements_agent",
        has_visualizations,
        {
            True: "visualization",  # If has visualizations, evaluate them
            False: "feedback_agent"       # Otherwise, skip to feedback_agent
        }
    )
    
    # Final edge 
    workflow.add_edge("visualization", "feedback_agent")
    
    # END node
    workflow.add_edge("feedback_agent", END)
    
    return workflow 
