from app import app
if __name__ == '__main__':
    app.run(ssl_context=('server.crt', 'server.key'), debug=True, port=5000, host="0.0.0.0")