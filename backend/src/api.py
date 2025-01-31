import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
        returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def drinks():

    drinks = [drink.long() for drink in Drink.query.all()]

    if len(drinks) == 0:
        print("no Drinks")
        abort(404)

    return jsonify({
        "success": True,
        "drinks": drinks}), 200


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth("get:drinks-detail")
def get_drinks_detail(payload):

    try:
        drinks = [drink.long() for drink in Drink.query.all()]

        if len(drinks) == 0:
            print("no Drinks")
            abort(404)

        return jsonify({
            "success": True,
            "drinks": drinks}), 200

    except AuthError:
        abort(401)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def new_drinks(payload):
    try:
        body = request.get_json()

        if body is None:
            print("no drink input")
            abort(404)

        new_title = body.get('title')
        new_recipe = body.get('recipe')

        new_drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
        new_drink.insert()
        new_drink = Drink.query.filter_by(id=new_drink.id).first()

        return jsonify({
                            "success": True,
                            "message": "New drink added",
                            "drinks": [new_drink.long()]
                        }), 200

    except AuthError:
        abort(422)


'''
@TODO implement endpoint
    PATCH /drinks/<int:id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(payload, id):

    patch_drink = Drink.query.filter(Drink.id == id).one_or_none()

    if patch_drink is None:
        print("no drink with that id found")
        abort(404)

    try:
        body = request.get_json()

        if body is None:
            print("no drink update input")
            abort(404)

        patch_drink.title = body.get('title')
        patch_drink.recipe = json.dumps(body.get('recipe'))
        patch_drink.update()

        return jsonify({
                        "success": True,
                        "message": "Drink Updated",
                        "drinks": [patch_drink.long()]
                    }), 200

    except AuthError:
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
    where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
    try:
        delete_drink = Drink.query.filter_by(id=id).first()
        delete_drink.delete()
        return jsonify({
                        "success": True,
                        "delete": id,
                    }), 200

    except AuthError:
        abort(422)

# Error Handling


'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 404,
                    "message": "Not Fund"
                    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def unauthorized(error):
    return jsonify({
                    "success": False,
                    "error": error.status_code,
                    "message": error.error['description']
                    }), error.status_code
