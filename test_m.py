from profiler_framework.profiler import Profiler

profiler = Profiler()

@profiler.track_memory
def heavy_computation():
    """A function with high memory and CPU usage"""
    return sum([i**2 for i in range(10**4)])

heavy_computation()


from profiler_framework.profiler.core import Profiler
import asyncio

profiler = Profiler()

@profiler.track_memory_async
async def async_heavy_task():
    """An async function that waits and consumes CPU"""
    sum([i**2 for i in range(10**3)])
    await asyncio.sleep(2)
    
@profiler.track_memory
def heavy_task():
    """An async function that waits and consumes CPU"""
    sum([i**2 for i in range(10**2)])
    

asyncio.run(async_heavy_task())
heavy_task()

from profiler_framework.profiler import Visualizer

viz = Visualizer(debug=True)
viz.visualize_usage()     # Creates bar charts
viz.visualize_over_time() # Creates time-series plots


