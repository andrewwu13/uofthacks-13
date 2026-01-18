
import sys
import os

# Set path
sys.path.append(os.getcwd())

def verify_module_vectors():
    print("\n=== Verifying Module Vectors Refactor ===")
    from backend.app.vector.module_vectors import MODULE_CATALOG, encode_module_id, get_module_by_id
    
    print(f"Catalog Size: {len(MODULE_CATALOG)}")
    
    # Test Encoding
    test_id = encode_module_id("neobrutalist", "hero") 
    # Neo(2) * 6 + Hero(1) = 13
    print(f"Encoded 'neobrutalist' + 'hero' -> {test_id}")
    assert test_id == 13, f"Expected 13, got {test_id}"
    
    # Test Lookup
    module = get_module_by_id(13)
    assert module is not None, "Failed to find module 13"
    assert module.genre == "neobrutalist", f"Expected neobrutalist, got {module.genre}"
    print("✅ Module Vectors Logic Verified")

def verify_vector_store_types():
    print("\n=== Verifying Vector Store Types ===")
    from backend.app.vector.vector_store import VectorStore
    vs = VectorStore()
    try:
        # Add integer ID
        vs.add(42, [0.1]*12, {})
        print("✅ Added integer ID 42 to store")
        assert 42 in vs.vectors
        assert isinstance(list(vs.vectors.keys())[0], int)
    except Exception as e:
        print(f"❌ Failed to add integer ID: {e}")

if __name__ == "__main__":
    verify_module_vectors()
    verify_vector_store_types()
