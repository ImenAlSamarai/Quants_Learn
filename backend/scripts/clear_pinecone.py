"""
Clean Slate: Delete all chunks from Pinecone
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.vector_store import vector_store

print("🧹 Clean Slate: Deleting all chunks from Pinecone...")
print("   This will remove all existing content to start fresh with optimized chunking.\n")

try:
    # Delete all vectors in default namespace
    vector_store.index.delete(delete_all=True, namespace='')
    print("✅ Successfully deleted all chunks from default namespace")

    # Also delete from web_resource namespace if it exists
    try:
        vector_store.index.delete(delete_all=True, namespace='web_resource')
        print("✅ Successfully deleted all chunks from web_resource namespace")
    except:
        pass

    print("\n🎉 Pinecone is now clean and ready for fresh indexing!")

except Exception as e:
    print(f"❌ Error clearing Pinecone: {e}")
