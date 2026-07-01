import os
import sys

# Ensure workspace is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Reconfigure stdout and stderr to use UTF-8 encoding to prevent UnicodeEncodeError on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from src.tools.rag_tools import get_rag_context

def main():
    print("🧪 Running automated test for RAG Search...")
    topic = "What is AgentVista and what are its capabilities and limitations?"
    
    try:
        context, citations = get_rag_context(topic)
        
        print("\n--- Test Results ---")
        print(f"Citations: {citations}")
        print(f"Context Length: {len(context)} characters")
        
        # Validation checks
        assert len(citations) > 0, "Test failed: citations list is empty!"
        assert "agentvista_testvista.md" in citations or "fpt_research.md" in citations, \
            "Test failed: expected source file is missing from citations!"
        assert len(context) > 100, "Test failed: retrieved context is too short!"
        
        print("\n✅ RAG Automated Test PASSED successfully!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ RAG Automated Test FAILED with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
