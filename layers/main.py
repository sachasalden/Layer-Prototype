from application.application_layer import ApplicationLayer
import json

def pretty(response: str):
    print("\n-------\n")
    try:
        parsed = json.loads(response)
        print(json.dumps(parsed, indent=4))
    except:
        print(response)



app = ApplicationLayer()

pretty(app.process('{"type": "ping"}'))
pretty(app.process('{"type": "echo", "message": "Hallo"}'))
pretty(app.process('{"type": "login", "username": "ahmed", "password": "123"}'))
pretty(app.process('{"type": "login"}'))
pretty(app.process('{"type": 123}'))
pretty(app.process('{"x": 1}'))
pretty(app.process('BAD JSON'))
