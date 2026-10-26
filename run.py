import sys
sys.path.append(r'C:\Users\Bhargav Shetty\OneDrive\Desktop\projects\AI-Powered Support & Analytics Platform')
from app import create_app
app = create_app()
app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
