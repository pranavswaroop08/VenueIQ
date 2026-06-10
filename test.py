from elasticsearch import Elasticsearch
import json

# Your Elasticsearch credentials
ES_HOST = "https://localhost:9200"
ES_USER = "elastic"
ES_PASSWORD = "qUKn3=DHhkyrcYtr=sxj"

try:
    # Connect to Elasticsearch
    es = Elasticsearch(
        ES_HOST,
        basic_auth=(ES_USER, ES_PASSWORD),
        verify_certs=False  # For self-signed certs
    )
    
    # Get cluster info
    info = es.info()
    
    print("✅ LOGIN SUCCESSFUL!")
    print(f"\nCluster Name: {info['cluster_name']}")
    print(f"Elasticsearch Version: {info['version']['number']}")
    print(f"Tagline: {info['tagline']}")
    
    # List all indices
    indices = es.indices.get_alias(index="*")
    print(f"\n📊 Available Indices:")
    for index_name in indices.keys():
        print(f"  - {index_name}")
    
except Exception as e:
    print(f"❌ LOGIN FAILED: {e}")
    print(f"\nCheck:")
    print(f"  1. Is Elasticsearch running? (check docker: docker ps)")
    print(f"  2. Is URL correct? {ES_HOST}")
    print(f"  3. Are credentials correct? {ES_USER}:{ES_PASSWORD}")