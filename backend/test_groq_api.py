#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from groq import Groq

def test_groq_api():
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv("GROQ_API_KEY")
    print(f"🔑 API Key: {api_key[:20]}..." if api_key else "❌ No API key found")
    
    if not api_key:
        print("❌ GROQ_API_KEY not found in environment")
        return False
    
    try:
        # Test the API key
        client = Groq(api_key=api_key)
        
        # Simple test request
        response = client.chat.completions.create(
            messages=[
                {"role": "user", "content": "Hello, test"}
            ],
            model="llama-3.1-8b-instant",
            max_tokens=50
        )
        
        print("✅ API Key is valid!")
        print(f"📝 Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ API Key test failed: {e}")
        return False

if __name__ == "__main__":
    test_groq_api()
