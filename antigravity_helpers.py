def extract_feature_request(query):
    """Extract the actual feature request from the command"""
    triggers = [
        'self update', 'upgrade yourself', 'enhance yourself', 'improve yourself',
        'update yourself', 'add feature', 'implement', 'give yourself',
        'ask antigravity to', 'tell antigravity to', 'ask anti gravity to', 'tell anti gravity to',
        'ask antigravity', 'tell antigravity', 'ask anti gravity', 'tell anti gravity',
        'antigravity', 'anti gravity',
        'make yourself', 'learn to', 'learn how to'
    ]
    
    # Sort triggers by length (descending) to match longest first
    triggers.sort(key=len, reverse=True)
    
    request = query
    for trigger in triggers:
        if trigger in query:
            # removing trigger
            request = query.split(trigger, 1)[-1].strip()
            # remove leading 'to ' if present (e.g. "learn how to [to] fly")
            if request.startswith('to '):
                 request = request[3:].strip()
            if request:
                return request
                
    return None

def type_to_antigravity(prompt):
    """Type the prompt into Antigravity (VS Code)"""
    try:
        # 1. Find VS Code window
        vscode_windows = [w for w in gw.getWindowsWithTitle("Visual Studio Code")]
        if not vscode_windows:
            vscode_windows = [w for w in gw.getWindowsWithTitle("VS Code")]
            
        if not vscode_windows:
            print("[Error: VS Code window not found]")
            return False
            
        # 2. Focus clean workspace
        vscode = vscode_windows[0]
        if not vscode.isActive:
            try:
                vscode.activate()
                time.sleep(0.5) 
            except:
                vscode.minimize()
                vscode.restore()
                time.sleep(0.5)
        
        # 3. Type text (using clipboard for speed)
        # Use simple text writing
        full_command = f"Antigravity, please {prompt}"
        
        # Safety: Don't overwrite clipboard if not needed, but here it's fastest
        pyautogui.write(full_command, interval=0.01) 
        pyautogui.press('enter')
        
        return True
    except Exception as e:
        print(f"[Error typing to Antigravity: {e}]")
        return False
