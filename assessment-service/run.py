from app import create_app

# Create an instance of the Flask application using the factory pattern
app = create_app()

if __name__ == '__main__':
    # Run the app, making it accessible on the container's network
    app.run(host='0.0.0.0', port=5000, debug=True)
