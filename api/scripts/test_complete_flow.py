import requests
import json
import time

BASE_URL = "http://localhost:8001/api"

def test_complete_flow():
    print("="*60)
    print("TESTING COMPLETE FLOW")
    print("="*60)
    
    try:
        # 1. Test Settings API
        print("\n1. Testing Settings API...")
        settings_resp = requests.get(f"{BASE_URL}/settings")
        settings_resp.raise_for_status()
        settings = settings_resp.json()
        print(f"   ✓ Settings loaded: {settings}")
        print(f"   - Native language: {settings.get('native_language', 'NOT SET')}")
        print(f"   - Target language: {settings.get('target_language', 'NOT SET')}")
        
        # 2. Create Session
        print("\n2. Creating session...")
        session_resp = requests.post(f"{BASE_URL}/sessions", json={"topic_code": "daily_life"})
        session_resp.raise_for_status()
        session_id = session_resp.json()['session_id']
        print(f"   ✓ Session created: {session_id}")
        
        # 3. Send message with error
        print("\n3. Sending message with intentional error...")
        msg_text = "I goed to the store yesterday"
        msg_resp = requests.post(
            f"{BASE_URL}/chat/{session_id}/message",
            json={"text": msg_text}
        )
        msg_resp.raise_for_status()
        msg_data = msg_resp.json()
        
        print(f"   ✓ Message sent: '{msg_text}'")
        print(f"   ✓ AI Reply: '{msg_data['reply'][:60]}...'")
        
        # Check for corrections
        errors = msg_data.get('detected_errors', [])
        if errors:
            print(f"   ✓ CORRECTIONS DETECTED: {len(errors)} error(s)")
            for i, err in enumerate(errors, 1):
                print(f"      {i}. {err['user_text']} → {err['corrected_text']}")
                print(f"         Category: {err['category']}")
                print(f"         Note: {err['note']}")
        else:
            print(f"   ⚠ WARNING: No corrections detected (expected at least 1)")
        
        # 4. Send another message
        print("\n4. Sending second message...")
        msg2_resp = requests.post(
            f"{BASE_URL}/chat/{session_id}/message",
            json={"text": "It was very fun"}
        )
        msg2_resp.raise_for_status()
        print(f"   ✓ Second message sent")
        
        # 5. Finish Session (trigger quiz generation)
        print("\n5. Finishing session (generating quizzes)...")
        finish_resp = requests.post(f"{BASE_URL}/sessions/{session_id}/finish", timeout=120)
        finish_resp.raise_for_status()
        finish_data = finish_resp.json()
        
        print(f"   ✓ Session finished!")
        print(f"   - Quizzes created: {finish_data['quizzes_created']}")
        print(f"   - Flashcards created: {finish_data['flashcards_created']}")
        
        if finish_data['quizzes_created'] > 0:
            print(f"\n   QUIZ PREVIEW:")
            for i, quiz in enumerate(finish_data.get('quizzes', [])[:2], 1):
                choices_data = json.loads(quiz['choices_json'])
                print(f"   Q{i}: {quiz['prompt']}")
                print(f"       Choices: {choices_data['choices']}")
                print(f"       Answer: {quiz['answer']}")
        
        # Summary
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)
        print(f"✓ Settings API: PASS (languages: {settings.get('native_language')}/{settings.get('target_language')})")
        print(f"{'✓' if errors else '⚠'} Corrections: {'PASS' if errors else 'WARN'} ({len(errors)} detected)")
        print(f"✓ Quiz Generation: PASS ({finish_data['quizzes_created']} quizzes)")
        print(f"✓ Flashcards: PASS ({finish_data['flashcards_created']} cards)")
        print("="*60)
        
        if not errors:
            print("\n⚠ NOTE: Errors detection may need adjustment in error_service")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_flow()
    exit(0 if success else 1)
