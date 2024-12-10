Here’s a Python implementation for memory profiling that can be toggled on or off in an Azure HTTP Function. The code uses psutil to monitor memory usage and provides a decorator to enable or disable profiling dynamically.

Step 1: Install Required Library

Ensure psutil is installed in your environment:

pip install psutil

Step 2: Implement Memory Profiling in Azure HTTP Function

import psutil
import functools
from datetime import datetime
import azure.functions as func

# Memory profiler toggle
ENABLE_MEMORY_PROFILING = True

def memory_profiler(func):
    """
    Decorator to profile memory usage before and after the function call.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if ENABLE_MEMORY_PROFILING:
            process = psutil.Process()
            memory_before = process.memory_info().rss / (1024 * 1024)  # in MB
            print(f"[{datetime.now()}] Memory before {func._name_}: {memory_before:.2f} MB")
            
            result = func(*args, **kwargs)
            
            memory_after = process.memory_info().rss / (1024 * 1024)  # in MB
            print(f"[{datetime.now()}] Memory after {func._name_}: {memory_after:.2f} MB")
            print(f"[{datetime.now()}] Memory difference: {memory_after - memory_before:.2f} MB")
            
            return result
        else:
            return func(*args, **kwargs)
    return wrapper

# Azure Function Example
@memory_profiler
def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Example Azure HTTP Trigger function with memory profiling.
    """
    try:
        # Simulate processing
        data = [x*2 for x in range(10*6)]  # Simulate a large computation
        
        return func.HttpResponse(
            "Memory profiling demo completed successfully!",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            f"An error occurred: {str(e)}",
            status_code=500
        )

How It Works:

1. ENABLE_MEMORY_PROFILING: Controls whether memory profiling is active. Set it to False to disable profiling.


2. memory_profiler decorator: Measures memory usage before and after the wrapped function execution.


3. Azure HTTP Function: The main function demonstrates a typical Azure Function with memory profiling applied.



Usage:

Enable Profiling: Set ENABLE_MEMORY_PROFILING = True.

Disable Profiling: Set ENABLE_MEMORY_PROFILING = False.


Deploy to Azure:

1. Package this code into an Azure Function app.


2. Set ENABLE_MEMORY_PROFILING as an application setting or use environment variables for dynamic toggling.



This approach provides flexibility for memory profiling in Azure Functions with minimal overhead when disabled.



import tracemalloc
import functools
from datetime import datetime
import azure.functions as func

# Memory profiler toggle
ENABLE_MEMORY_PROFILING = True

def memory_profiler(func):
    """
    Decorator to profile memory usage before and after the function call using tracemalloc.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if ENABLE_MEMORY_PROFILING:
            tracemalloc.start()  # Start tracking memory
            print(f"[{datetime.now()}] Memory profiling started for {func._name_}.")
            
            result = func(*args, **kwargs)  # Execute the function
            
            current, peak = tracemalloc.get_traced_memory()  # Get current and peak memory usage
            print(f"[{datetime.now()}] Current memory usage: {current / (1024 * 1024):.2f} MB")
            print(f"[{datetime.now()}] Peak memory usage: {peak / (1024 * 1024):.2f} MB")
            
            tracemalloc.stop()  # Stop tracking memory
            return result
        else:
            return func(*args, **kwargs)
    return wrapper

# Azure Function Example
@memory_profiler
def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Example Azure HTTP Trigger function with memory profiling.
    """
    try:
        # Simulate processing
        data = [x*2 for x in range(10*6)]  # Simulate a large computation
        
        return func.HttpResponse(
            "Memory profiling demo completed successfully!",
            status_code=200
        )
    except Exception as e:
        return func.HttpResponse(
            f"An error occurred: {str(e)}",
            status_code=500
        )








import tracemalloc
import functools
from datetime import datetime

# Toggle for enabling/disabling memory profiling
ENABLE_MEMORY_PROFILING = True

def memory_profiler(func):
    """
    Decorator to profile memory usage before and after the function call using tracemalloc.
    Works for both simple Python functions and Azure Functions.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if ENABLE_MEMORY_PROFILING:
            # Start memory tracking
            tracemalloc.start()
            print(f"[{datetime.now()}] Memory profiling started for {func._name_}.")
            
            # Execute the function
            result = func(*args, **kwargs)
            
            # Get memory usage stats
            current, peak = tracemalloc.get_traced_memory()
            print(f"[{datetime.now()}] Current memory usage: {current / (1024 * 1024):.2f} MB")
            print(f"[{datetime.now()}] Peak memory usage: {peak / (1024 * 1024):.2f} MB")
            
            # Stop memory tracking
            tracemalloc.stop()
            return result
        else:
            # Execute the function without profiling if disabled
            return func(*args, **kwargs)
    return wrapper
