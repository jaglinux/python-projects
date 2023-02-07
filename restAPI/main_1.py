from flask import Flask, request
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)

data = {}

class Video(Resource):
    def get(self):
        param = request.args.get('id')
        print(param)
        param = request.args.get('gid')
        print(param)
        return param
    
    def post(self, video_id):
        param = request.args.get('id')
        print(param)


api.add_resource(Video, "/video/")


if __name__ == '__main__':
    app.run(debug=True)

# python main_1.py
# http://127.0.0.1:5000/video/?id=9&gid=101
