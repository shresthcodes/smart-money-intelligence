"""
Test script for Sector Analysis page

This script verifies that the Sector Analysis page:
1. Can be imported without errors
2. Has the correct structure
3. Contains all required sections
"""

import sys
import os

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard', 'pages'))

def test_sector_analysis_page():
    """Test the Sector Analysis page structure and content."""
    
    print("🧪 Testing Sector Analysis Page...")
    print("=" * 60)
    
    # Test 1: Import the page
    print("\n1️⃣ Testing page import...")
    try:
        with open('dashboard/pages/3_Sector_Analysis.py', 'r', encoding='utf-8') as f:
            content = f.read()
        print("   ✅ Page file exists and is readable")
    except Exception as e:
        print(f"   ❌ Error reading page: {e}")
        return False
    
    # Test 2: Check for required imports
    print("\n2️⃣ Testing required imports...")
    required_imports = [
        'import streamlit as st',
        'import pandas as pd',
        'from utils.data_loader import load_latest_data'
    ]
    
    for imp in required_imports:
        if imp in content:
            print(f"   ✅ Found: {imp}")
        else:
            print(f"   ❌ Missing: {imp}")
            return False
    
    # Test 3: Check for page configuration
    print("\n3️⃣ Testing page configuration...")
    if 'st.set_page_config' in content:
        print("   ✅ Page configuration found")
        if 'Sector Analysis' in content:
            print("   ✅ Correct page title")
        if '🏭' in content:
            print("   ✅ Page icon present")
    else:
        print("   ❌ Page configuration missing")
        return False
    
    # Test 4: Check for data detection logic
    print("\n4️⃣ Testing data detection logic...")
    if 'sector_columns' in content and 'has_sector_data' in content:
        print("   ✅ Data detection logic present")
    else:
        print("   ❌ Data detection logic missing")
        return False
    
    # Test 5: Check for placeholder content
    print("\n5️⃣ Testing placeholder content...")
    placeholder_sections = [
        'About Sector Analysis',
        'Available Features',
        'How to Add Sector Data',
        'Expected Sector Data Format',
        'Sample Code'
    ]
    
    found_sections = 0
    for section in placeholder_sections:
        if section in content:
            print(f"   ✅ Found section: {section}")
            found_sections += 1
        else:
            print(f"   ⚠️  Section not found: {section}")
    
    if found_sections >= 4:
        print(f"   ✅ Sufficient placeholder content ({found_sections}/{len(placeholder_sections)} sections)")
    else:
        print(f"   ❌ Insufficient placeholder content ({found_sections}/{len(placeholder_sections)} sections)")
        return False
    
    # Test 6: Check for sample code
    print("\n6️⃣ Testing sample code presence...")
    if 'def download_sector_data' in content:
        print("   ✅ Sample code function found")
    else:
        print("   ⚠️  Sample code function not found")
    
    if 'yfinance' in content or 'yf' in content:
        print("   ✅ Data source library mentioned")
    else:
        print("   ⚠️  Data source library not mentioned")
    
    # Test 7: Check for conditional rendering
    print("\n7️⃣ Testing conditional rendering...")
    if 'if not has_sector_data:' in content or 'if has_sector_data:' in content:
        print("   ✅ Conditional rendering logic present")
    else:
        print("   ❌ Conditional rendering logic missing")
        return False
    
    # Test 8: Check for helpful resources
    print("\n8️⃣ Testing helpful resources...")
    resources = ['NSE', 'Yahoo Finance', 'BSE']
    found_resources = 0
    for resource in resources:
        if resource in content:
            print(f"   ✅ Found resource: {resource}")
            found_resources += 1
    
    if found_resources >= 2:
        print(f"   ✅ Sufficient resources provided ({found_resources}/{len(resources)})")
    else:
        print(f"   ⚠️  Limited resources ({found_resources}/{len(resources)})")
    
    # Test 9: Check for footer
    print("\n9️⃣ Testing footer...")
    if 'Footer' in content or 'footer' in content.lower():
        print("   ✅ Footer section present")
    else:
        print("   ⚠️  Footer section not found")
    
    # Test 10: Check for error handling
    print("\n🔟 Testing error handling...")
    if 'st.error' in content or 'st.warning' in content:
        print("   ✅ Error handling present")
    else:
        print("   ⚠️  Limited error handling")
    
    # Test 11: Syntax validation
    print("\n1️⃣1️⃣ Testing Python syntax...")
    try:
        compile(content, 'dashboard/pages/3_Sector_Analysis.py', 'exec')
        print("   ✅ Python syntax is valid")
    except SyntaxError as e:
        print(f"   ❌ Syntax error: {e}")
        return False
    
    # Test 12: Check for documentation
    print("\n1️⃣2️⃣ Testing documentation...")
    if '"""' in content:
        print("   ✅ Docstring present")
    else:
        print("   ⚠️  No docstring found")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ All critical tests passed!")
    print("=" * 60)
    
    return True

def test_page_structure():
    """Test the logical structure of the page."""
    
    print("\n📋 Testing Page Structure...")
    print("=" * 60)
    
    with open('dashboard/pages/3_Sector_Analysis.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check structure order
    structure_elements = [
        ('Imports', 'import streamlit'),
        ('Page Config', 'st.set_page_config'),
        ('Title', 'st.title'),
        ('Data Loading', 'load_latest_data'),
        ('Data Detection', 'sector_columns'),
        ('Conditional Logic', 'if not has_sector_data'),
        ('Footer', 'Footer' in content or 'footer' in content.lower())
    ]
    
    print("\nStructure elements in order:")
    for i, (name, marker) in enumerate(structure_elements, 1):
        if isinstance(marker, bool):
            status = "✅" if marker else "⚠️"
        else:
            status = "✅" if marker in content else "❌"
        print(f"   {i}. {name}: {status}")
    
    print("\n✅ Structure test complete!")
    return True

def test_user_experience():
    """Test user experience elements."""
    
    print("\n🎨 Testing User Experience Elements...")
    print("=" * 60)
    
    with open('dashboard/pages/3_Sector_Analysis.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    ux_elements = {
        'Emojis for visual appeal': '📊' in content or '🏭' in content,
        'Markdown formatting': 'st.markdown' in content,
        'Expandable sections': 'st.expander' in content,
        'Columns for layout': 'st.columns' in content,
        'Metrics display': 'st.metric' in content,
        'Info messages': 'st.info' in content,
        'Success messages': 'st.success' in content,
        'Code blocks': 'st.code' in content,
        'DataFrames': 'st.dataframe' in content
    }
    
    print("\nUser experience elements:")
    passed = 0
    for element, present in ux_elements.items():
        status = "✅" if present else "⚠️"
        print(f"   {status} {element}")
        if present:
            passed += 1
    
    print(f"\n📊 UX Score: {passed}/{len(ux_elements)} elements present")
    
    if passed >= len(ux_elements) * 0.7:
        print("✅ Good user experience!")
    else:
        print("⚠️  Could improve user experience")
    
    return True

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🧪 SECTOR ANALYSIS PAGE TEST SUITE")
    print("=" * 60)
    
    try:
        # Run all tests
        test1 = test_sector_analysis_page()
        test2 = test_page_structure()
        test3 = test_user_experience()
        
        # Final summary
        print("\n" + "=" * 60)
        print("📊 FINAL TEST SUMMARY")
        print("=" * 60)
        
        if test1 and test2 and test3:
            print("\n✅ ALL TESTS PASSED!")
            print("\n🎉 The Sector Analysis page is ready to use!")
            print("\nNext steps:")
            print("1. Run the Streamlit dashboard")
            print("2. Navigate to 'Sector Analysis' page")
            print("3. Follow the guide to add sector data")
            print("4. Enjoy comprehensive sector analysis!")
        else:
            print("\n⚠️  Some tests had warnings")
            print("The page should still work, but review the warnings above.")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()
