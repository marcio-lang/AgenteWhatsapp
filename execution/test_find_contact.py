#!/usr/bin/env python3
"""
Test script to check what find_contact returns for the user's LID
"""
import sys
sys.path.insert(0, '.')

from execution.evolution_api import EvolutionClient

client = EvolutionClient()

# User's LID from webhook
user_lid = "135768261533797@lid"

print(f"Testing find_contact for LID: {user_lid}")
print("=" * 60)

try:
    result = client.find_contact(user_lid)
    print(f"\nResult type: {type(result)}")
    print(f"\nFull result:")
    print(result)
    
    if isinstance(result, list) and len(result) > 0:
        print(f"\nFirst item:")
        print(result[0])
        
        if 'remoteJid' in result[0]:
            print(f"\nResolved number: {result[0]['remoteJid']}")
        else:
            print("\nNo 'remoteJid' field found!")
            print(f"Available fields: {list(result[0].keys())}")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
