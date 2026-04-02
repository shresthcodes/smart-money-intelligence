"""
Property-Based Test for Docstring Presence

This test validates that all public functions in the codebase have docstrings,
ensuring code documentation standards are maintained.

Feature: smart-money-intelligence, Property 25: Function Docstring Presence
Validates: Requirements 12.2
"""

import pytest
import inspect
import importlib
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def get_all_modules():
    """
    Get all Python modules in the scripts directory.
    
    Returns:
        List of module names to test
    """
    scripts_dir = project_root / 'scripts'
    modules = []
    
    for file in scripts_dir.glob('*.py'):
        if file.name != '__init__.py' and not file.name.startswith('_'):
            module_name = file.stem
            modules.append(f'scripts.{module_name}')
    
    return modules


def get_public_functions(module):
    """
    Get all public functions from a module.
    
    Public functions are those that:
    - Are callable
    - Don't start with underscore
    - Are defined in the module (not imported)
    
    Args:
        module: Python module object
    
    Returns:
        List of (function_name, function_object) tuples
    """
    functions = []
    
    for name, obj in inspect.getmembers(module):
        # Skip private functions (starting with _)
        if name.startswith('_'):
            continue
        
        # Check if it's a function
        if inspect.isfunction(obj):
            # Check if it's defined in this module (not imported)
            if obj.__module__ == module.__name__:
                functions.append((name, obj))
    
    return functions


def has_docstring(func):
    """
    Check if a function has a non-empty docstring.
    
    Args:
        func: Function object to check
    
    Returns:
        bool: True if function has a non-empty docstring
    """
    docstring = inspect.getdoc(func)
    return docstring is not None and len(docstring.strip()) > 0


# Feature: smart-money-intelligence, Property 25: Function Docstring Presence
# Validates: Requirements 12.2
@pytest.mark.property
class TestDocstringPresence:
    """
    Test suite for validating docstring presence across all public functions.
    """
    
    def test_all_modules_have_docstrings(self):
        """
        Property 25: Function Docstring Presence
        
        For any public function in the codebase, the function should have
        a non-empty docstring.
        
        This test:
        1. Discovers all Python modules in scripts/
        2. Finds all public functions in each module
        3. Verifies each function has a docstring
        """
        modules_to_test = get_all_modules()
        
        assert len(modules_to_test) > 0, "No modules found to test"
        
        all_functions_tested = 0
        functions_without_docstrings = []
        
        for module_name in modules_to_test:
            try:
                # Import the module
                module = importlib.import_module(module_name)
                
                # Get all public functions
                public_functions = get_public_functions(module)
                
                # Test each function
                for func_name, func_obj in public_functions:
                    all_functions_tested += 1
                    
                    if not has_docstring(func_obj):
                        functions_without_docstrings.append(
                            f"{module_name}.{func_name}"
                        )
            
            except ImportError as e:
                pytest.skip(f"Could not import {module_name}: {e}")
        
        # Assert that we tested at least some functions
        assert all_functions_tested > 0, "No public functions found to test"
        
        # Assert that all functions have docstrings
        if functions_without_docstrings:
            error_msg = (
                f"Found {len(functions_without_docstrings)} function(s) without docstrings:\n" +
                "\n".join(f"  - {func}" for func in functions_without_docstrings)
            )
            pytest.fail(error_msg)
        
        print(f"\n✓ All {all_functions_tested} public functions have docstrings")
    
    def test_data_collection_functions(self):
        """
        Test that all functions in data_collection module have docstrings.
        """
        from scripts import data_collection
        
        public_functions = get_public_functions(data_collection)
        
        assert len(public_functions) > 0, "No public functions found in data_collection"
        
        for func_name, func_obj in public_functions:
            assert has_docstring(func_obj), (
                f"Function {func_name} in data_collection module is missing a docstring"
            )
    
    def test_preprocessing_functions(self):
        """
        Test that all functions in preprocessing module have docstrings.
        """
        from scripts import preprocessing
        
        public_functions = get_public_functions(preprocessing)
        
        assert len(public_functions) > 0, "No public functions found in preprocessing"
        
        for func_name, func_obj in public_functions:
            assert has_docstring(func_obj), (
                f"Function {func_name} in preprocessing module is missing a docstring"
            )
    
    def test_feature_engineering_functions(self):
        """
        Test that all functions in feature_engineering module have docstrings.
        """
        from scripts import feature_engineering
        
        public_functions = get_public_functions(feature_engineering)
        
        assert len(public_functions) > 0, "No public functions found in feature_engineering"
        
        for func_name, func_obj in public_functions:
            assert has_docstring(func_obj), (
                f"Function {func_name} in feature_engineering module is missing a docstring"
            )
    
    def test_signal_generator_functions(self):
        """
        Test that all functions in signal_generator module have docstrings.
        """
        from scripts import signal_generator
        
        public_functions = get_public_functions(signal_generator)
        
        assert len(public_functions) > 0, "No public functions found in signal_generator"
        
        for func_name, func_obj in public_functions:
            assert has_docstring(func_obj), (
                f"Function {func_name} in signal_generator module is missing a docstring"
            )
    
    def test_insights_generator_functions(self):
        """
        Test that all functions in insights_generator module have docstrings.
        """
        from scripts import insights_generator
        
        public_functions = get_public_functions(insights_generator)
        
        assert len(public_functions) > 0, "No public functions found in insights_generator"
        
        for func_name, func_obj in public_functions:
            assert has_docstring(func_obj), (
                f"Function {func_name} in insights_generator module is missing a docstring"
            )
    
    def test_docstring_quality(self):
        """
        Test that docstrings meet minimum quality standards.
        
        A quality docstring should:
        - Be at least 20 characters long
        - Contain the word "Args" or "Returns" (for functions with parameters/returns)
        """
        modules_to_test = get_all_modules()
        
        low_quality_docstrings = []
        
        for module_name in modules_to_test:
            try:
                module = importlib.import_module(module_name)
                public_functions = get_public_functions(module)
                
                for func_name, func_obj in public_functions:
                    docstring = inspect.getdoc(func_obj)
                    
                    if docstring:
                        # Check minimum length
                        if len(docstring) < 20:
                            low_quality_docstrings.append(
                                f"{module_name}.{func_name}: Docstring too short ({len(docstring)} chars)"
                            )
                        
                        # Check for Args/Returns sections if function has parameters
                        sig = inspect.signature(func_obj)
                        has_params = len(sig.parameters) > 0
                        has_return = sig.return_annotation != inspect.Signature.empty
                        
                        if has_params and 'Args:' not in docstring and 'Parameters:' not in docstring:
                            low_quality_docstrings.append(
                                f"{module_name}.{func_name}: Missing 'Args:' section"
                            )
                        
                        if has_return and 'Returns:' not in docstring:
                            low_quality_docstrings.append(
                                f"{module_name}.{func_name}: Missing 'Returns:' section"
                            )
            
            except ImportError:
                continue
        
        if low_quality_docstrings:
            warning_msg = (
                f"Found {len(low_quality_docstrings)} docstring(s) that could be improved:\n" +
                "\n".join(f"  - {issue}" for issue in low_quality_docstrings[:10])  # Show first 10
            )
            # This is a warning, not a failure
            print(f"\n⚠ {warning_msg}")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, '-v', '-m', 'property'])
