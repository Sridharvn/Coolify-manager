import requests
import sys
import time
import os
import json

# Configuration file path
CONFIG_FILE = ".coolify_session.json"

class CoolifyManager:
    def __init__(self, base_url=None, token=None):
        self.base_url = base_url.rstrip('/') if base_url else None
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        } if token else {}
        self.resources = []
        self.pending_deletions = set()  # UUIDs deleted but not yet gone from API

    def save_session(self, url, token):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({"url": url, "token": token}, f)
        print(f"✅ Session saved to {CONFIG_FILE}")

    @staticmethod
    def load_session():
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return None

    def fetch_resources(self):
        try:
            apps_res = requests.get(f"{self.base_url}/api/v1/applications", headers=self.headers)
            services_res = requests.get(f"{self.base_url}/api/v1/services", headers=self.headers)
            
            apps_res.raise_for_status()
            services_res.raise_for_status()

            apps = [{"type": "applications", **a} for a in apps_res.json()]
            services = [{"type": "services", **s} for s in services_res.json()]

            all_resources = apps + services
            fetched_uuids = {r['uuid'] for r in all_resources}
            # Clear UUIDs that are now confirmed gone from the API
            self.pending_deletions -= (self.pending_deletions - fetched_uuids)
            # Hide resources still being deleted (async deletion in progress)
            self.resources = [r for r in all_resources if r['uuid'] not in self.pending_deletions]
            return self.resources
        except Exception as e:
            print(f"\n❌ Connection Error: {e}")
            return []

    def execute_action(self, resource, action):
        res_type = resource['type']
        uuid = resource['uuid']
        
        # Action Map: (Method, Endpoint)
        endpoints = {
            "delete": ("DELETE", f"/api/v1/{res_type}/{uuid}"),
            "restart": ("GET", f"/api/v1/{res_type}/{uuid}/restart"),
            "stop": ("GET", f"/api/v1/{res_type}/{uuid}/stop"),
            "deploy": ("GET", f"/api/v1/{res_type}/{uuid}/deploy")
        }

        method, path = endpoints[action]
        url = f"{self.base_url}{path}"
        params = {"delete_configurations": True, "delete_volumes": True} if action == "delete" else {}
        
        try:
            resp = requests.request(method, url, headers=self.headers, params=params)
            if resp.status_code in [200, 201, 204]:
                return True, None
            # Try to extract a readable error from the response body
            try:
                body = resp.json()
                message = body.get("message") or body.get("error") or json.dumps(body)
            except ValueError:
                message = resp.text.strip() or f"HTTP {resp.status_code}"
            return False, f"HTTP {resp.status_code}: {message}"
        except requests.exceptions.ConnectionError:
            return False, "Connection failed — check your Coolify URL"
        except requests.exceptions.Timeout:
            return False, "Request timed out"
        except Exception as e:
            return False, str(e)

    def stream_logs(self, resource):
        res_type = resource['type']
        uuid = resource['uuid']
        url = f"{self.base_url}/api/v1/{res_type}/{uuid}/logs"
        
        print(f"\n--- Streaming Logs for {resource.get('name')} (Ctrl+C to exit) ---")
        last_logs = ""
        try:
            while True:
                resp = requests.get(url, headers=self.headers)
                if resp.status_code == 200:
                    current_logs = resp.text
                    if current_logs != last_logs:
                        new_content = current_logs[len(last_logs):]
                        if new_content:
                            print(new_content, end="", flush=True)
                        last_logs = current_logs
                time.sleep(2) 
        except KeyboardInterrupt:
            print("\n--- Exiting Log Viewer ---")

def main():
    manager = CoolifyManager()
    session = manager.load_session()

    if session:
        print(f"Found saved session for: {session['url']}")
        use_saved = input("Use these credentials? (Y/n): ").lower() != 'n'
        if use_saved:
            manager.base_url = session['url']
            manager.headers = {"Authorization": f"Bearer {session['token']}", "Accept": "application/json"}
        else:
            session = None

    if not session:
        url = input("Coolify URL (e.g., https://app.coolify.io): ").strip()
        token = input("API Token: ").strip()
        manager.base_url = url.rstrip('/')
        manager.headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        
        if input("Save this session for next time? (y/N): ").lower() == 'y':
            manager.save_session(url, token)

    while True:
        resources = manager.fetch_resources()
        if not resources:
            print("No resources found. Check your API token and URL.")
            if input("Clear saved session and exit? (y/n): ").lower() == 'y':
                if os.path.exists(CONFIG_FILE): os.remove(CONFIG_FILE)
            break

        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{'ID':<4} | {'TYPE':<12} | {'NAME':<25} | {'STATUS':<15}")
        print("-" * 70)
        for i, res in enumerate(resources):
            name = (res.get('name') or "Unnamed")[:25]
            status = res.get('status', 'n/a')
            print(f"[{i:<2}] | {res['type'].upper():<12} | {name:<25} | {status:<15}")

        print("\nCommands: [numbers] Select | [all] Select All | [q] Quit")
        cmd = input("Input: ").strip().lower()

        if cmd == 'q': break
        
        try:
            indices = range(len(resources)) if cmd == 'all' else [int(x.strip()) for x in cmd.split(',')]
            selected = [resources[i] for i in indices if 0 <= i < len(resources)]
            
            if not selected: continue

            print(f"\nSelected: {', '.join([s.get('name') or s['uuid'] for s in selected])}")
            print("Actions: [r] Restart | [s] Stop | [d] Deploy | [l] Logs (1st only) | [rm] Delete")
            act_choice = input("Action: ").strip().lower()

            if act_choice == 'l':
                manager.stream_logs(selected[0])
                continue

            action_map = {'r': 'restart', 's': 'stop', 'd': 'deploy', 'rm': 'delete'}
            action = action_map.get(act_choice)

            if action:
                if action == 'delete' and input("Confirm PERMANENT delete? (y/n): ").lower() != 'y':
                    continue
                
                for res in selected:
                    print(f"Executing {action.upper()} on {res.get('name')}... ", end="", flush=True)
                    success, error = manager.execute_action(res, action)
                    if success:
                        print("✅")
                        if action == 'delete':
                            manager.pending_deletions.add(res['uuid'])
                    else:
                        print(f"❌  {error}")
                time.sleep(1.5)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()