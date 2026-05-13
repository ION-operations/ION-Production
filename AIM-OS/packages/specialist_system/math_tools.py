"""
Math Tools for AI

Provides computational math tools for AI agents including:
- Matplotlib for visualization
- NumPy for numerical computation
- SciPy for scientific computing
- SymPy for symbolic mathematics
- Pandas for data analysis

NL_TAG: MATH-TOOLS-001 | Execute math computation | executeMathComputation | []
NL_TAG_CONNECT: MATH-MCP-001 | Math tools via MCP | executeMathComputation → MCP | [MATH-TOOLS-001]
NL_TAG_INTENT: MATH-DESIGN-001 | Enable AI math capabilities | computational tools for AI | [ADR-MATH]
"""

import sys
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
import io
import base64


class MathTools:
    """
    Math tools for AI agents.
    
    Provides access to mathematical computation, visualization, and analysis tools.
    
    NL_TAG: MATH-TOOLS-002 | Create math visualization | createVisualization | [MATH-TOOLS-001]
    """
    
    def __init__(self):
        """Initialize math tools with available libraries."""
        self.available_libraries = self._check_available_libraries()
    
    def _check_available_libraries(self) -> Dict[str, bool]:
        """Check which math libraries are available."""
        libraries = {
            'numpy': False,
            'scipy': False,
            'matplotlib': False,
            'sympy': False,
            'pandas': False,
            'jupyter': False
        }
        
        for lib in libraries.keys():
            try:
                __import__(lib)
                libraries[lib] = True
            except ImportError:
                pass
        
        return libraries
    
    def execute_python_code(
        self,
        code: str,
        libraries: Optional[List[str]] = None,
        return_output: bool = True,
        return_plot: bool = False
    ) -> Dict[str, Any]:
        """
        Execute Python code with math libraries.
        
        Args:
            code: Python code to execute
            libraries: List of libraries to import (auto-detected if None)
            return_output: Whether to return stdout/stderr
            return_plot: Whether to return matplotlib plots as base64 images
            
        Returns:
            Execution result with output, errors, and optional plot
        """
        if libraries is None:
            libraries = ['numpy', 'scipy', 'matplotlib', 'sympy', 'pandas']
        
        # Check library availability
        missing = [lib for lib in libraries if not self.available_libraries.get(lib, False)]
        if missing:
            return {
                'success': False,
                'error': f'Missing libraries: {", ".join(missing)}',
                'available': self.available_libraries
            }
        
        # Prepare code with imports
        imports = '\n'.join([f'import {lib}' for lib in libraries if self.available_libraries.get(lib, False)])
        full_code = f'{imports}\n{code}'
        
        # Capture stdout/stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            # Redirect stdout/stderr
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture
            
            # Execute code
            exec_globals = {}
            exec(full_code, exec_globals)
            
            # Capture matplotlib plots if requested
            plot_data = None
            if return_plot and self.available_libraries.get('matplotlib', False):
                import matplotlib.pyplot as plt
                if plt.get_fignums():
                    # Save plot to bytes
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', bbox_inches='tight')
                    buf.seek(0)
                    plot_data = base64.b64encode(buf.read()).decode('utf-8')
                    plt.close('all')
            
            # Restore stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
            return {
                'success': True,
                'output': stdout_capture.getvalue() if return_output else None,
                'error': stderr_capture.getvalue() if stderr_capture.getvalue() else None,
                'plot': plot_data,
                'variables': {k: str(v) for k, v in exec_globals.items() if not k.startswith('_') and k not in libraries}
            }
            
        except Exception as e:
            # Restore stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
            return {
                'success': False,
                'error': str(e),
                'output': stdout_capture.getvalue() if return_output else None,
                'stderr': stderr_capture.getvalue()
            }
    
    def create_plot(
        self,
        plot_type: str,
        data: Any,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a plot using matplotlib.
        
        Args:
            plot_type: Type of plot ('line', 'scatter', 'bar', 'hist', '3d', etc.)
            data: Data to plot (dict with x, y, or array)
            options: Plot options (title, labels, etc.)
            
        Returns:
            Plot as base64 image
        """
        if not self.available_libraries.get('matplotlib', False):
            return {
                'success': False,
                'error': 'Matplotlib not available'
            }
        
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            
            options = options or {}
            
            # Create figure
            fig, ax = plt.subplots()
            
            # Plot based on type
            if plot_type == 'line':
                x = data.get('x', np.arange(len(data.get('y', []))))
                y = data.get('y', [])
                ax.plot(x, y, **{k: v for k, v in options.items() if k not in ['title', 'xlabel', 'ylabel']})
            elif plot_type == 'scatter':
                x = data.get('x', [])
                y = data.get('y', [])
                ax.scatter(x, y, **{k: v for k, v in options.items() if k not in ['title', 'xlabel', 'ylabel']})
            elif plot_type == 'bar':
                x = data.get('x', np.arange(len(data.get('y', []))))
                y = data.get('y', [])
                ax.bar(x, y, **{k: v for k, v in options.items() if k not in ['title', 'xlabel', 'ylabel']})
            elif plot_type == 'hist':
                values = data.get('values', [])
                ax.hist(values, **{k: v for k, v in options.items() if k not in ['title', 'xlabel', 'ylabel']})
            else:
                return {
                    'success': False,
                    'error': f'Unknown plot type: {plot_type}'
                }
            
            # Set labels and title
            if 'title' in options:
                ax.set_title(options['title'])
            if 'xlabel' in options:
                ax.set_xlabel(options['xlabel'])
            if 'ylabel' in options:
                ax.set_ylabel(options['ylabel'])
            
            # Save to base64
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            plot_data = base64.b64encode(buf.read()).decode('utf-8')
            plt.close('all')
            
            return {
                'success': True,
                'plot': plot_data,
                'format': 'png'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def solve_equation(
        self,
        equation: str,
        variable: str = 'x'
    ) -> Dict[str, Any]:
        """
        Solve a mathematical equation symbolically.
        
        Args:
            equation: Equation string (e.g., 'x**2 + 2*x + 1 = 0')
            variable: Variable to solve for
            
        Returns:
            Solution(s) to the equation
        """
        if not self.available_libraries.get('sympy', False):
            return {
                'success': False,
                'error': 'SymPy not available'
            }
        
        try:
            from sympy import symbols, solve, sympify, Eq
            
            # Parse equation
            var = symbols(variable)
            expr = sympify(equation.replace('=', '-'))
            
            # Solve
            solutions = solve(expr, var)
            
            return {
                'success': True,
                'solutions': [str(sol) for sol in solutions],
                'count': len(solutions)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def compute_statistics(
        self,
        data: List[float],
        statistics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compute statistical measures.
        
        Args:
            data: List of numerical values
            statistics: List of statistics to compute (default: all)
            
        Returns:
            Dictionary of computed statistics
        """
        if not self.available_libraries.get('numpy', False):
            return {
                'success': False,
                'error': 'NumPy not available'
            }
        
        try:
            import numpy as np
            
            arr = np.array(data)
            stats = {}
            
            if statistics is None:
                statistics = ['mean', 'median', 'std', 'min', 'max', 'sum', 'count']
            
            if 'mean' in statistics:
                stats['mean'] = float(np.mean(arr))
            if 'median' in statistics:
                stats['median'] = float(np.median(arr))
            if 'std' in statistics:
                stats['std'] = float(np.std(arr))
            if 'min' in statistics:
                stats['min'] = float(np.min(arr))
            if 'max' in statistics:
                stats['max'] = float(np.max(arr))
            if 'sum' in statistics:
                stats['sum'] = float(np.sum(arr))
            if 'count' in statistics:
                stats['count'] = int(len(arr))
            
            return {
                'success': True,
                'statistics': stats
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_available_tools(self) -> Dict[str, Any]:
        """
        Get list of available math tools.
        
        Returns:
            Dictionary of available tools and libraries
        """
        return {
            'libraries': self.available_libraries,
            'tools': [
                'execute_python_code',
                'create_plot',
                'solve_equation',
                'compute_statistics'
            ]
        }

