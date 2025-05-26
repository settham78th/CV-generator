from app import app

if __name__ == '__main__':
    # PWA Builder version runs on port 5003 to avoid conflicts
    app.run(host='0.0.0.0', port=5003, debug=True)