from flask import Flask, request
from flask_restful import Api, Resource, reqparse, abort

app = Flask(__name__)
api = Api(app)

books = {}

book_post_args = reqparse.RequestParser()

book_post_args.add_argument("name", type=str, help="Enter name of book", required=True)
book_post_args.add_argument("price", type=int, help="Enter price of book", required=True)
book_post_args.add_argument("author", type=str, help="Enter author of book", required=True)

def abort_id_not_found(param):
        if param not in books:
            abort(404, message = "book ID not available")

def abort_id_already_present(param):
        if param in books:
            abort(404, message = f"book already created for the id {param}")

class Book(Resource):
    def get(self):
        param = request.args.get('id')
        abort_id_not_found(param)
        return books[param]
    
    def post(self):
        param = request.args.get('id')
        abort_id_already_present(param)
        args = book_post_args.parse_args()
        books[param] = args
        return args
        
    def delete(self):
        param = request.args.get('id')
        abort_id_not_found(param)

class BookSearch(Resource):
    def get(self):
        resultBooks = None
        dictArgs = request.args.to_dict()
        if 'price' in dictArgs:
            priceComparision = int(dictArgs['price'])
            print('jag-------- ', priceComparision)
            booksFiltered = dict(filter(lambda a:a[1]['price'] > priceComparision,  books.items()))
            booksFiltered = sorted(booksFiltered.items(), key=lambda a:a[1].price, reverse=True)
            print(booksFiltered, len(booksFiltered))
        if "size" in dictArgs:
            size = int(dictArgs['size'])
            if size > len(booksFiltered):
                size = len(booksFiltered)
            return {"search result is ": booksFiltered[:size]}
        

api.add_resource(Book, "/book/")
api.add_resource(BookSearch, "/book/search/")

if __name__ == '__main__':
    app.run(debug=True)
