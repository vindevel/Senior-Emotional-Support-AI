import sys
import os
from flask_cors import CORS

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from flask import Flask
from routes.face import face_bp
from routes.conversation import conversation_bp
from routes.user import user_bp

app = Flask(__name__)
CORS(app)
app.register_blueprint(face_bp)
app.register_blueprint(conversation_bp)
app.register_blueprint(user_bp)

if __name__ == "__main__":
    app.run(debug=False)

