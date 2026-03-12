import os
import shutil
import uuid
import time
import threading

def create_session_id():
    """Generate a unique session ID for each user"""
    return str(uuid.uuid4())

def clear_data_folders(session_id):
    """Clear data folders for a specific session"""
    base_path = f"user_sessions/{session_id}"
    folders = [
        f"{base_path}/pdfs",
        f"{base_path}/texts",
        f"{base_path}/dist_texts",
        f"{base_path}/metadata",
        f"{base_path}/output"
    ]

    for folder in folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)

def cleanup_old_sessions(max_age_hours=2):
    """Delete session folders older than max_age_hours"""
    sessions_dir = "user_sessions"
    
    if not os.path.exists(sessions_dir):
        return 0
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    deleted_count = 0
    
    for session_folder in os.listdir(sessions_dir):
        session_path = os.path.join(sessions_dir, session_folder)
        
        if not os.path.isdir(session_path):
            continue
        
        folder_age = current_time - os.path.getmtime(session_path)
        
        if folder_age > max_age_seconds:
            try:
                shutil.rmtree(session_path)
                deleted_count += 1
                print(f"🗑️ Deleted old session: {session_folder}")
            except Exception as e:
                print(f"❌ Error deleting {session_folder}: {e}")
    
    return deleted_count

def start_cleanup_scheduler(interval_minutes=30, max_age_hours=2):
    """Start background thread for periodic cleanup"""
    def cleanup_loop():
        while True:
            time.sleep(interval_minutes * 60)
            deleted = cleanup_old_sessions(max_age_hours)
            if deleted > 0:
                print(f"🧹 Cleanup: {deleted} old sessions removed")
    
    cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
    cleanup_thread.start()
    print(f"✅ Cleanup scheduler started (every {interval_minutes}min, max age: {max_age_hours}h)")