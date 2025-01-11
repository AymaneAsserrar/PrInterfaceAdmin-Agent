"""CPU monitoring routes module with proper data handling."""
from typing import List, Dict, Union
from fastapi import APIRouter, Request, HTTPException, status
from domain.schemas import (
    ExceptionResponseSchema,
    GetCpuResponseSchema,
    GetCpuCoreResponseSchema,
)
from statistics import mean

cpu_router = APIRouter()

@cpu_router.get(
    "/usage",
    response_model=Dict[str, Union[List[GetCpuResponseSchema], float]],
    responses={
        200: {"description": "Successfully retrieved CPU usage data"}
    }
)
async def get_cpu(request: Request) -> Dict[str, Union[List[GetCpuResponseSchema], float]]:
    """Get CPU usage data for all cores and system average."""
    try:
        monitor_task = request.app.state.monitortask
        
        # Get the CPU percentages
        cpu_percentages = monitor_task.cpu_percent
        
        if not cpu_percentages or not isinstance(cpu_percentages, list):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No CPU data available"
            )
        
        # Create the CPU usage data
        cpu_data = []
        for i, usage in enumerate(cpu_percentages):
            # Ensure the usage is a float and not None or zero when it shouldn't be
            if usage is None:
                usage = 0.0
            try:
                usage_float = float(usage)
                cpu_data.append(GetCpuResponseSchema(
                    core=i,
                    usage=round(usage_float, 2)
                ))
            except (TypeError, ValueError) as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Invalid CPU usage value for core {i}: {str(e)}"
                )
        
        # Calculate average only from valid, non-zero values
        valid_usages = [core.usage for core in cpu_data if core.usage is not None and core.usage > 0]
        average_usage = round(mean(valid_usages), 2) if valid_usages else 0.0
        
        # Add some debug information if average is 0
        if average_usage == 0:
            print(f"Debug - CPU percentages: {cpu_percentages}")
            print(f"Debug - Valid usages: {valid_usages}")
        
        return {
            "cpu_usage": cpu_data,
            "average": average_usage
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve CPU data: {str(e)}"
        )