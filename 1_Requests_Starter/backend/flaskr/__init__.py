import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy  # , or_
from flask_cors import CORS
import random

from models import setup_db, Book, db

BOOKS_PER_SHELF = 8    


# @TODO: General Instructions
#   - As you're creating endpoints, define them and then search for 'TODO' within the frontend to update the endpoints there.
#     If you do not update the endpoints, the lab will not work - of no fault of your API code!
#   - Make sure for each route that you're thinking through when to abort and with which kind of error
#   - If you change any of the response body keys, make sure you update the frontend to correspond.

def paginate_books(request,selection): #helper function
    page = request.args.get('page',1,type=int)
    start = (page - 1) * BOOKS_PER_SHELF
    end = start + BOOKS_PER_SHELF
    
    formatted_books = [book.format() for book in selection]
    books_range = formatted_books[start:end]
    return books_range

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    # @TODO: Write a route that retrivies all books, paginated.
    #         You can use the constant above to paginate by eight books.
    #         If you decide to change the number of books per page,
    #         update the frontend to handle additional books in the styling and pagination
    #         Response body keys: 'success', 'books' and 'total_books'
    # TEST: When completed, the webpage will display books including title, author, and rating shown as stars



    @app.route('/books')
    def get_books():
        books = Book.query.all()

        #--- this should be moved into the paginate_books() helper function
        # page = request.args.get('page',1,type=int)
        # start = (page - 1) * BOOKS_PER_SHELF
        # end = start + BOOKS_PER_SHELF
        
        # formatted_books = [book.format() for book in books]
        # books_range = formatted_books[start:end]
        #------------------------------------------------------------------

        current_books = paginate_books(request,books)

        if len(current_books) == 0:
            abort(404)

        return jsonify({
            'success':True,
            'books':current_books,
            'total_books':len(books)
        })

    # @TODO: Write a route that will update a single book's rating.
    #         It should only be able to update the rating, not the entire representation
    #         and should follow API design principles regarding method and route.
    #         Response body keys: 'success'
    # TEST: When completed, you will be able to click on stars to update a book's rating and it will persist after refresh
    # TO TEST FROM COMMAND LINE: curl http://127.0.0.1:5000/books/3/update-rating -X PATCH -H "Content-Type: application/json" -d "{\"rating\":\"4\"}"
    @app.route('/books/<int:book_id>/update-rating',methods=['PATCH'])
    def update_rating(book_id):
        error = False
        try:
            print("bp1 book_id:", book_id)
            body = request.get_json()
            print(body)
            rating = request.get_json()['rating']
            print("bp2")
            book = Book.query.get(book_id)
            print("bp3")
            book.rating = rating
            print("bp4")
            db.session.commit()
        except:
            error = True
            print("Error occurred")
            db.session.rollback()
        finally:
            db.session.close()
        if error:
            return jsonify({
                "success":False
            })
        else:
            return jsonify({
                "success":True
            })


    # @TODO: Write a route that will delete a single book.
    #        Response body keys: 'success', 'deleted'(id of deleted book), 'books' and 'total_books'
    #        Response body keys: 'success', 'books' and 'total_books'
    # TEST: When completed, you will be able to delete a single book by clicking on the trashcan.
    # TO TEST FROM COMMAND LINE: curl http://127.0.0.1:5000/books/3/delete-book -X DELETE -H "Content-Type: application/json"
    @app.route('/books/<int:book_id>/delete-book',methods=['DELETE'])
    def delete_book(book_id):
        print("deleting book id:",book_id)
        error = False
        try:
            print("bp8")
            book = Book.query.filter(Book.id == book_id).one_or_none()
            print(book)
            print("bp2")
            book.delete()
            db.session.commit()
            print("bp3")
        except:
            error = True
            print("bp4")
            db.session.rollback()
        finally:
            print("bp5")
            books = Book.query.all()
            print(books)
            db.session.close()
        
        if error:
            print("bp6")
            return jsonify({
                "success":True,
                "books":str(books),
                "total_books":len(books)
            })
        else:
            print("bp7")
            return jsonify({
                "success":True,
                "deleted":book_id,
                "books":str(books),
                "total_books":len(books)
            })


    # @TODO: Write a route that create a new book.
    #        Response body keys: 'success', 'created'(id of created book), 'books' and 'total_books'
    # TEST: When completed, you will be able to a new book using the form. Try doing so from the last page of books.
    #       Your new book should show up immediately after you submit it at the end of the page.
    @app.route('/books/create-book',methods=['POST'])
    def create_book():
        error = False
        body = {}
        try:
            my_request = request.get_json()
            title = my_request["title"]
            author = my_request["author"]
            rating = my_request["rating"]
            book = Book(title, author, rating)
            db.session.add(book)
            db.session.commit()
            print("create 1")
            # book = Book.query.filter_by(title == book.title).one_or_none()
            book_id = book.id
            print("create 2")
        except:
            error = True
            db.session.rollback()
        finally:
            books = Book.query.all()
            db.session.close()

        if error:
            return jsonify({
                "success":False,
                "books":str(books),
                "total books":len(books)
            })
        else:
            return jsonify({
                "success": True,
                "created":book_id,
                "books":str(books),
                "total books":len(books)
                # "request": str(my_request),
                # "request_type":str(type(my_request))
            })


    return app
