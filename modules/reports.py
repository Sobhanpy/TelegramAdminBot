from modules.utils import load_json, save_json

REPORT_FILE = "reports.json"

def log_activity(user_id, action):
    data = load_json(REPORT_FILE)
    if str(user_id) not in data:
        data[str(user_id)] = []
    data[str(user_id)].append(action)
    save_json(REPORT_FILE, data)

def get_user_report(user_id):
    data = load_json(REPORT_FILE)
    return data.get(str(user_id), [])
