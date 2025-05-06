from typing import Dict, Optional, TypedDict, List

class EvaluationState(TypedDict):
    # Input data
    student_code: str
    file_path: str
    student_name: str
    requirements: Dict
    
    # Processing states
    execution_result: Dict
    
    # Metadata
    has_visualizations: Optional[bool]
    viz_imports: Optional[List[str]]
    import_count: Optional[int]
    function_count: Optional[int]
    class_count: Optional[int]
    code_size_kb: Optional[float]
    
    # Evaluation results
    syntax_score: int
    style_score: int
    requirements_score: int
    visualization_score: Optional[int]
    
    # Feedback fields 
    syntax_feedback: Optional[Dict]
    style_feedback: Optional[Dict]
    requirements_feedback: Optional[Dict]
    visualization_feedback: Optional[Dict]
    
    # Final outputs
    final_score: int
    feedback: str
    error_analysis: Optional[str]
