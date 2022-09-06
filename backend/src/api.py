from crypt import methods
import os
import sys
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

# ROUTES

@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    if (len(drinks) == 0):
        abort(404)
    
    return jsonify({
        'success': True,
        'drinks': [drink.short() for drink in drinks]
    })

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    drinks = Drink.query.all()
    
    if (len(drinks) == 0):
        abort(404)
    
    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks]
    })

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(payload):
    body = request.get_json()
    title = body['title']
    recipe = json.dumps(body['recipe'])

    try:
        drink = Drink(title=title, recipe=recipe)
        drink.insert()
        
        return jsonify({
            'success': True,
            'drinks': drink.long(),
        })
    except:
        print(sys.exc_info())
        abort(422)

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    
    if drink is None:
        abort(404)
    
    try:
        body = request.get_json()
        title = body['title']
        recipe = json.dumps(body['recipe'])
        
        drink.title = title
        drink.recipe = recipe
        
        drink.update()
        
        return jsonify({
            'success': True,
            'drinks': drink.long()
        })
    except:
        print(sys.exc_info())
        abort(422)

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    
    if drink is None:
        abort(404)
    
    try:
        drink.delete()
        
        return jsonify({
            'success': True,
            'delete': drink.id
        })
    except:
        print(sys.exc_info())
        abort(422)

# Error Handling

@app.errorhandler(400)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400

@app.errorhandler(401)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized"
    }), 401

@app.errorhandler(403)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "Forbidden"
    }), 403

@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not Found"
    }), 404

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable Entity"
    }), 422
