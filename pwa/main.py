
from app import app

if __name__ == '__main__':
    # PWA version runs on port 5002 to avoid conflicts
    app.run(host='0.0.0.0', port=5002, debug=True)
