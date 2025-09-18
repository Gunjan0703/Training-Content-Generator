from app import create_app

app = create_app()

if __name__ == "__main__":
    # Gunicorn will run this in containers; this block is for local dev
    app.run(host="0.0.0.0", port=5001, debug=True)
