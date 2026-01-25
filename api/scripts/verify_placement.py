
import requests
import time
import json

BASE_URL = "http://localhost:8001/api"

def reset_data():
    print("Setting LLM provider to simple_mock...")
    requests.post(f"{BASE_URL}/settings", json={"llm_provider": "simple_mock", "llm_model": "mock-1"})

    print("WARNING: Resetting all data...")
    resp = requests.delete(f"{BASE_URL}/admin/reset")
    resp.raise_for_status()
    print("Data reset complete.")

def get_dashboard():
    resp = requests.get(f"{BASE_URL}/dashboard/summary")
    resp.raise_for_status()
    return resp.json()

def create_session(topic="daily_life"):
    resp = requests.post(f"{BASE_URL}/sessions", json={"topic_code": topic})
    resp.raise_for_status()
    return resp.json()

def send_message(session_id, text):
    resp = requests.post(f"{BASE_URL}/chat/{session_id}/message", json={"text": text})
    resp.raise_for_status()
    return resp.json()['reply']

def finish_session(session_id):
    print(f"Finishing session {session_id}...")
    resp = requests.post(f"{BASE_URL}/sessions/{session_id}/finish", timeout=120)
    resp.raise_for_status()
    return resp.json()

def main():
    try:
        # 1. Reset
        reset_data()
        
        # 2. Check empty dashboard
        dash = get_dashboard()
        print(f"Initial Fluency: {dash['fluency_level']} (Score: {dash['fluency_score']})")
        assert dash['fluency_level'] == "A1", "Should be A1 initially"
        
        # 3. Run Placement Test
        print("\n--- Starting Placement Test ---")
        sess = create_session("placement_test")
        sid = sess['session_id']
        print(f"System Prompt Snippet: {sess['system_prompt'][:50]}...")
        
        # Simulate conversation
        replies = [
            "I am fine, thank you. My name is John.",
            "I come from Brazil. It is very hot there.",
            "I work as a software engineer. I like coding.",
            "In my free time I play soccer and read books.",
        ]
        
        for text in replies:
            print(f"User: {text}")
            ai = send_message(sid, text)
            print(f"AI: {ai[:60]}...")
            time.sleep(0.5)
            
        # Finish (triggers evaluation)
        finish_session(sid)
        print("Placement test finished.")
        
        # 4. Check Dashboard (Placement Score)
        dash = get_dashboard()
        p_level = dash['fluency_level']
        p_score = dash['fluency_score']
        print(f"Post-Placement Fluency: {p_level} (Score: {p_score})")
        
        # 5. Run Normal Session
        print("\n--- Starting Normal Session ---")
        sess = create_session("daily_life")
        sid = sess['session_id']
        
        # Brief chat
        send_message(sid, "Hello again.")
        send_message(sid, "I want to buy some bread.")
        
        # Finish (triggers normal quiz gen + potentially new metric snapshot if quizzes done?)
        # NOTE: Normal sessions only generate metrics AFTER quizzes are done.
        # We need to answer quizzes to get a score.
        res = finish_session(sid)
        quizzes = res.get('quizzes', [])
        print(f"Quizzes to answer: {len(quizzes)}")
        
        params = {"choice": "placeholder", "latency_ms": 1000}
        for q in quizzes:
            # We need the correct answer to get a good score? 
            # Actually, let's just guess the first choice to simulate interaction
            choices = json.loads(q['choices_json'])['choices']
            # Cheat: find the answer if possible, or just pick first
            # The API doesn't expose 'answer' in the list... wait, it does in 'finish_session' response for debugging?
            # Yes: "answer": q.answer in the router return.
            ans = q['answer']
            requests.post(f"{BASE_URL}/quiz/{q['id']}/answer", json={"choice": ans, "latency_ms": 1000})
            
        print("Quizzes answered.")
        
        # 6. Check Dashboard (Average Score)
        dash = get_dashboard()
        final_level = dash['fluency_level']
        final_score = dash['fluency_score']
        print(f"Final Fluency: {final_level} (Score: {final_score})")
        
        print("\nVerification Successful.")
        
    except Exception as e:
        print(f"\nFAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
