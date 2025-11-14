from application.application_layer import ApplicationLayer


if __name__ == '__main__':
    app = ApplicationLayer()
    print(app.process('{"type": "ping"}'))
    print(app.process('{"type": "echo", "message": "hallo"}'))
