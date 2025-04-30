import numpy as np
from typing import List, Dict, Any, Tuple

def calculate_zscore(values: List[float]) -> List[float]:
    """
    Calculate Z-scores for a list of values.
    
    Args:
        values: List of numerical values
        
    Returns:
        List of Z-scores
    """
    mean = np.mean(values)
    std = np.std(values)
    if std == 0:  # Handle case where all values are the same
        return [0.0] * len(values)
    return [(x - mean) / std for x in values]

def detect_outliers(data: List[Dict[str, Any]], 
                   value_key: str, 
                   z_threshold: float = 1.0) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Detect outliers in the data using Z-score analysis.
    
    Args:
        data: List of data points
        value_key: Key in the data dictionary containing the value to analyze
        z_threshold: Z-score threshold for outlier detection (default: 1.0)
        
    Returns:
        Tuple of (normal_points, outlier_points)
    """
    if not data:
        return [], []
        
    # Extract values for analysis
    values = [float(point["payload"][value_key]) for point in data]
    
    # Calculate Z-scores
    z_scores = calculate_zscore(values)
    
    # Separate normal and outlier points
    normal_points = []
    outlier_points = []
    
    for point, z_score in zip(data, z_scores):
        point_with_z = point.copy()
        point_with_z["z_score"] = z_score
        
        # Outliers are now included if the absolute Z-score is greater than or equal to the threshold
        if abs(z_score) >= z_threshold:  
            outlier_points.append(point_with_z)
        else:
            normal_points.append(point_with_z)
            
    return normal_points, outlier_points
