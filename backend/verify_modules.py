import sys
import os

# Add backend directory to sys.path so we can import 'app'
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_root = os.path.dirname(current_dir)
sys.path.append(backend_root)

try:
    from app.vector.module_vectors import MODULE_CATALOG, decode_module_id, get_module_by_id
    from app.vector.profile_vectors import get_recommended_template_id
    from app.vector.vector_store import initialize_vector_store

    # 1. Initialize
    initialize_vector_store()

    print(f"\n=== VERIFICATION: 36 MODULE SYSTEM ===")
    print(f"Catalog Size: {len(MODULE_CATALOG)} (Expected: 36)")

    # 2. Check IDs
    ids = [m.module_id for m in MODULE_CATALOG]
    min_id, max_id = min(ids), max(ids)
    print(f"ID Range: {min_id} - {max_id} (Expected: 0 - 35)")

    # 3. Check specific modules
    print("\n--- Sample Modules ---")
    samples = [0, 6, 35] # Base/Standard, Minimalist/Standard, Cyber/Bold
    for sid in samples:
        m = get_module_by_id(sid)
        if m:
            print(f"ID {sid}: {m.genre.upper()} / {m.layout.upper()}")
            print(f"  Desc: {m.description[:50]}...")
            print(f"  Tags: {m.tags}")
        else:
            print(f"ID {sid}: NOT FOUND")

    # 4. Test Recommendation
    print("\n--- Recommendation Test ---")
    dummy_profile = {
        "visual_preference": "minimalist",
        "browsing_speed": "fast"
    }
    # Note: Vector search requires profile conversion which might need dependencies like numpy
    # We assume 'user_profile_to_vector' works.
    
    try:
        rec_id = get_recommended_template_id(dummy_profile)
        rec_data = decode_module_id(rec_id)
        print(f"Profile: {dummy_profile}")
        print(f"Recommended ID: {rec_id}")
        print(f"Recommended Type: {rec_data['genre']} / {rec_data['layout']}")
    except Exception as e:
        print(f"Recommendation Failed: {e}")

    print("\n=== VERIFICATION COMPLETE ===")

except ImportError as e:
    print(f"Import Error: {e}")
except Exception as e:
    print(f"Error: {e}")
