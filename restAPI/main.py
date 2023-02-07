from flask import Flask
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)

data = {}

video_post_args = reqparse.RequestParser()

video_post_args.add_argument("name", type=str, help="Enter name of video", required=True)
video_post_args.add_argument("likes", type=int, help="Enter video likes", required=True)
video_post_args.add_argument("views", type=int, help="Enter video views", required=True)

class Video(Resource):
    def get(self, video_id):
        if video_id not in data:
            return None
        return data[video_id]
    
    def post(self, video_id):
        args = video_post_args.parse_args()
        data[video_id] = args
        return {"data": args}


api.add_resource(Video, "/video/<int:video_id>")


if __name__ == '__main__':
    app.run(debug=True)
