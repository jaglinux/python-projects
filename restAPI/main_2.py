from flask import Flask, request
from flask_restful import Api, Resource, reqparse, abort

app = Flask(__name__)
api = Api(app)

data = {}

video_post_args = reqparse.RequestParser()

video_post_args.add_argument("name", type=str, help="Enter name of video", required=True)
video_post_args.add_argument("likes", type=int, help="Enter video likes", required=True)
video_post_args.add_argument("views", type=int, help="Enter video views", required=True)

def abort_id_not_found(param):
        if param not in data:
            abort(404, message = "video ID not available")

def abort_id_already_present(param):
        if param in data:
            abort(404, message = f"video data already created for the id {param}")

class Video(Resource):
    def get(self):
        param = request.args.get('id')
        abort_id_not_found(param)
        return data[param]
    
    def post(self):
        param = request.args.get('id')
        abort_id_already_present(param)
        args = video_post_args.parse_args()
        data[param] = args
        print(args)
        
    def delete(self):
        param = request.args.get('id')
        abort_id_not_found(param)
   

api.add_resource(Video, "/video/")

if __name__ == '__main__':
    app.run(debug=True)
