import os
import json
import requests
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
AIRLABS_API_KEY = os.getenv("AIRLABS_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") # Host ID
DATA_FILE = "data.json"

if not all([AIRLABS_API_KEY, TELEGRAM_BOT_TOKEN]):
    print("Error: Missing API keys.")
    sys.exit(1)

# ... (load_data, save_data, send_telegram_message, get_updates remain same) ...

def get_flight_status(flight_iata):
    url = "https://airlabs.co/api/v9/flight"
    params = {'api_key': AIRLABS_API_KEY, 'flight_iata': flight_iata}
    try:
        response = requests.get(url, params=params)
        data = response.json()
        # AirLabs returns a list in 'response' key
        return data['response'][0] if data.get('response') else None
    except Exception as e:
        print(f"Error fetching flight data: {e}")
        return None

def format_message(flight_data):
    if not flight_data: return "⚠️ Flight not found."
    
    # AirLabs fields
    status = flight_data.get('status', 'Unknown').upper()
    flight_num = flight_data.get('flight_iata')
    dep = flight_data.get('dep_iata')
    arr = flight_data.get('arr_iata')
    
    # Times
    dep_time = flight_data.get('dep_time')
    dep_est = flight_data.get('dep_estimated', dep_time)
    arr_time = flight_data.get('arr_time')
    arr_est = flight_data.get('arr_estimated', arr_time)
    
    # Gate/Baggage
    dep_gate = flight_data.get('dep_gate')
    arr_gate = flight_data.get('arr_gate')
    baggage = flight_data.get('arr_baggage')
    
    msg = f"✈️ **{flight_num} Status: {status}**\n🛫 {dep} -> 🛬 {arr}\n🕒 Dep: {dep_time}"
    
    if dep_gate: msg += f"\n🚪 Dep Gate: {dep_gate}"
    if arr_gate: msg += f"\n🚪 Arr Gate: {arr_gate}"
    if baggage: msg += f"\n🛄 Baggage: {baggage}"
    
    return msg

def process_commands(data):
    updates = get_updates()
    if not updates: return data
    
    last_update_id = 0
    for update in updates:
        last_update_id = update['update_id']
        if 'message' not in update: continue
        
        msg = update['message']
        text = msg.get('text', '').strip().split()
        chat_id = str(msg['chat']['id'])
        
        if not text: continue
        
        cmd = text[0].lower()
        
        if cmd == '/start':
            send_telegram_message(chat_id, f"👋 Welcome! Your Chat ID is `{chat_id}`.\nAsk the host to add you to a group.")
            
        elif cmd == '/track' and len(text) > 1:
            flight = text[1].upper()
            if flight not in data['subscriptions']: data['subscriptions'][flight] = []
            if chat_id not in data['subscriptions'][flight]:
                data['subscriptions'][flight].append(chat_id)
                send_telegram_message(chat_id, f"✅ Tracking {flight}")
                
        elif cmd == '/stop' and len(text) > 1:
            flight = text[1].upper()
            if flight in data['subscriptions'] and chat_id in data['subscriptions'][flight]:
                data['subscriptions'][flight].remove(chat_id)
                send_telegram_message(chat_id, f"🛑 Stopped tracking {flight}")
                if not data['subscriptions'][flight]: del data['subscriptions'][flight]

        elif cmd == '/addgroup' and len(text) > 2 and chat_id == str(TELEGRAM_CHAT_ID):
            group = text[1].lower()
            user_id = text[2]
            if group not in data['groups']: data['groups'][group] = []
            if user_id not in data['groups'][group]:
                data['groups'][group].append(user_id)
                send_telegram_message(chat_id, f"✅ Added {user_id} to group '{group}'")

        elif cmd == '/trackgroup' and len(text) > 2 and chat_id == str(TELEGRAM_CHAT_ID):
            group = text[1].lower()
            flight = text[2].upper()
            if group in data['groups']:
                if flight not in data['subscriptions']: data['subscriptions'][flight] = []
                for uid in data['groups'][group]:
                    if uid not in data['subscriptions'][flight]:
                        data['subscriptions'][flight].append(uid)
                send_telegram_message(chat_id, f"✅ Group '{group}' is now tracking {flight}")

    # Acknowledge updates so we don't process them again next time
    if last_update_id:
        get_updates(offset=last_update_id + 1)
        
    return data

def has_changed(old_state, new_data):
    """Check if meaningful data has changed."""
    if not old_state: return True
    
    # Fields to monitor for changes
    keys_to_check = [
        'status',
        'dep_gate',
        'arr_gate',
        'arr_baggage',
        'dep_estimated',
        'arr_estimated'
    ]
    
    for key in keys_to_check:
        new_val = str(new_data.get(key))
        old_val = str(old_state.get(key))
        
        if new_val != old_val:
            return True
            
    return False

def update_state(flight, new_data):
    """Extract relevant state to save."""
    return {
        "status": new_data.get('status'),
        "dep_gate": new_data.get('dep_gate'),
        "arr_gate": new_data.get('arr_gate'),
        "arr_baggage": new_data.get('arr_baggage'),
        "dep_estimated": new_data.get('dep_estimated'),
        "arr_estimated": new_data.get('arr_estimated')
    }

def main():
    data = load_data()
    
    # 1. Process new commands
    data = process_commands(data)
    
    # 2. Check flights
    for flight, subscribers in data['subscriptions'].items():
        print(f"Checking {flight} for {len(subscribers)} users...")
        flight_data = get_flight_status(flight)
        
        if not flight_data:
            continue
            
        # Check for changes
        old_state = data['flight_states'].get(flight)
        if has_changed(old_state, flight_data):
            print(f"Update detected for {flight}!")
            msg = format_message(flight_data)
            
            for chat_id in subscribers:
                send_telegram_message(chat_id, msg)
                
            # Update state
            data['flight_states'][flight] = update_state(flight, flight_data)
        else:
            print(f"No changes for {flight}.")

    save_data(data)

if __name__ == "__main__":
    main()
