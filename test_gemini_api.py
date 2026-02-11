#!/usr/bin/env python3
"""
Quick test for Gemini API integration using google.generativeai SDK
"""

import os
import google.generativeai as genai

def test_gemini_api():
    """Test basic Gemini API connectivity"""
    
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ GEMINI_API_KEY not set")
        print("Set it with: export GEMINI_API_KEY='your_key'")
        return False
    
    print("Testing Gemini API...")
    print(f"API Key: {api_key[:10]}...{api_key[-5:]}")
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = "What is the approximate on-road price of Honda Activa 5G BS4 109cc in Delhi in December 2017? Provide only the price in rupees."
        
        response = model.generate_content(prompt)
        
        print(f"\n✅ Gemini Response:\n{response.text}")
        return True
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("GEMINI API CONNECTIVITY TEST")
    print("=" * 60)
    print()
    
    success = test_gemini_api()
    
    print()
    print("=" * 60)
    if success:
        print("✅ TEST PASSED - Gemini API is working")
    else:
        print("❌ TEST FAILED - Check API key and configuration")
    print("=" * 60)
