import httplib2
import json
import random
import requests
import string
from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import make_response
from flask_httpauth import HTTPBasicAuth
from oauth2client.client import FlowExchangeError
from oauth2client.client import flow_from_clientsecrets
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError

from catalogDBSetup import Category, CatalogItem, Base, User, DB_CONNECT_STRING

auth = HTTPBasicAuth()

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine(DB_CONNECT_STRING)
Base.metadata.bind = engine

session = scoped_session(sessionmaker(bind=engine))
allCatsCached = []


@app.teardown_request
def remove_session(ex=None):
    session.remove()


def getCatalogItemJson(catalogItem):
    """This is a utility method designed to get the json
    serialization of a catalog item"""
    return jsonify({
        'name': catalogItem.name,
        'description': catalogItem.description,
        'categoryId': catalogItem.categoryId,
        'id': catalogItem.id,
        'creator': catalogItem.creator_id
    })


def getCategoryJson(category):
    """This is a utility method designed to get
    the json serialization of a category"""
    return jsonify({
        'name': category.name,
        'description': category.description,
        'id': category.id,
        'creator': category.creator_id
    })


# Utility Method. It queries the DB and creates an array of dictionaries
def fillCatTableData():
    """This is a utility method designed to get
        the json serialization of all category which
        contains catalog items within them"""
    global allCatsCached
    allCatsFromCatTable = session.query(Category).all()
    allCatsCached = []
    for category in allCatsFromCatTable:
        categoryObj = {
            'name': category.name,
            'description': category.description,
            'id': category.id,
            'catalogItems': [],
            'creator': category.creator_id
        }
        allItemsForThisCat = session.query(CatalogItem).filter(
            CatalogItem.categoryId == category.id)
        for catItem in allItemsForThisCat:
            categoryObj['catalogItems'].append({
                'name': catItem.name,
                'description': catItem.description,
                'id': catItem.id,
                'categoryId': catItem.categoryId,
                'creator': catItem.creator_id
            })
        allCatsCached.append(categoryObj)


def getCategoriesData():
    if len(allCatsCached) == 0:
        fillCatTableData()
    return allCatsCached


def getRequestDataInJson(dataToLoad):
    return json.loads(dataToLoad.decode('utf-8'))


@app.route('/loginUser/<provider>', methods=['POST'])
def loginUser(provider):
    """Handler for Loggin a user in
    Provider could be google or userInput
    """
    # STEP 1 - Parse the auth code
    requestData = getRequestDataInJson(request.data)
    requestData = requestData['body']
    if provider == 'google':
        auth_code = requestData['access_token']
        print("Step 1 - Complete, received auth code %s" % auth_code)
        # STEP 2 - Exchange for a token
        try:
            # Upgrade the authorization code into a credentials object
            oauth_flow = flow_from_clientsecrets(
                '/var/www/itemCatalog/client_secrets.json', scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(auth_code)
        except FlowExchangeError as e:
            print(str(e))
            response = make_response(
                json.dumps('Failed to upgrade the authorization code.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Check that the access token is valid.
        access_token = credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?'
               'access_token=%s' % access_token)
        h = httplib2.Http()
        result = getRequestDataInJson(h.request(url, 'GET')[1])
        # If there was an error in the access token info, abort.
        if result.get('error') is not None:
            print('Authorization code is not valid')
            print('Error %s' % result.get('error'))
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'

        print("Step 2 Complete! Access Token : %s " % credentials.access_token)

        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        answer = requests.get(userinfo_url, params=params)

        data = answer.json()

        name = data['name']
        picture = data['picture']
        email = data['email']

        # see if user exists, if it doesn't make a new one
        try:
            user = session.query(User).filter_by(email=email).first()
            if not user:
                user = User(username=name, picture=picture, email=email)
                session.add(user)
                session.commit()
        except SQLAlchemyError:
            print("Oops!", sys.exc_info()[0], "occured.")
            response = make_response(
                json.dumps(
                    'Error occured while performing DB operations. %s'
                    % str(sys.exc_info()[0])), 500)
            response.headers['Content-Type'] = 'application/json'
            return response

        # STEP 4 - Make token
        token = user.generate_auth_token(6000)

        # STEP 5 - Send back token to the client
        return jsonify({'token': token.decode('ascii'), 'userId': user.id})

        # return jsonify({'token': token.decode('ascii'), 'duration': 6000})
    elif provider == 'userInput':
        email = requestData['email']
        password = requestData['password']

        if email is None or password is None:
            print("Missing Arguments")
            return jsonify('Missing Arguments. '
                           'Please enter a valid email and password. '
                           'Password is greater than 6 chars.'), 400

        try:
            if session.query(User).filter_by(email=email).first() is not None:
                print("existing user")
                user = session.query(User).filter_by(email=email).first()
                if not user.verify_password(password):
                    print('Invalid Username / Password for %s' % email)
                    return jsonify('Email Id and Password don\'t match. '
                                   'Please try again.'), 445
                else:
                    messageToSend = 'Login Successful. Enjoy!!'
                    print('Login successful')
            else:
                print('Creating a new user : %s' % email)
                user = User(email=email, username=email)
                user.hash_password(password)
                session.add(user)
                session.commit()
                messageToSend = 'Created a new User. ' \
                                'Please update your name in Profile Section'
                print('User created successfully')
        except SQLAlchemyError:
            print("Oops!", sys.exc_info()[0], "occured.")
            response = make_response(
                json.dumps('Error occured while performing DB operations. %s'
                           % str(sys.exc_info()[0])), 500)
            response.headers['Content-Type'] = 'application/json'
            return response
        token = user.generate_auth_token(600)
        return jsonify({
            'token': token.decode('ascii'),
            'message': messageToSend,
            'userId': user.id,
            'username': user.username})
    else:
        return 'Unrecoginized Provider'


@app.route('/profile/update', methods=['POST'])
def updateUserInfo():
    """
    Its a API call handler to update the user profile
    """
    reqData = getRequestDataInJson(request.data)
    token = reqData['token']
    reqData = reqData['body']
    userEditing = User.verify_auth_token(token)
    if userEditing is None:
        response = make_response(
            json.dumps('Bad Authorization Token. Please re-login'), 444)
        response.headers['Content-Type'] = 'application/json'
        return response
    print(reqData)

    try:
        user = session.query(User).filter_by(id=userEditing).first()
        if user is None:
            response = make_response(
                json.dumps('User not found. '
                           'Please re-login or Create a New User'), 444)
            response.headers['Content-Type'] = 'application/json'
            return response
        if reqData['username']:
            user.username = reqData['username']
        if reqData['password']:
            user.hash_password(reqData['password'])
        session.add(user)
        session.commit()
    except SQLAlchemyError:
        print("Oops!", sys.exc_info()[0], "occured.")
        response = make_response(
            json.dumps('Error occured while performing DB operations. %s'
                       % str(sys.exc_info()[0])), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('User info Updated')
    return 'User info updated successfully'


@app.route('/item/new', methods=['GET', 'POST'])
def newItemInCategory():
    """
    API handler to add a new item in DB
    """
    if request.method == 'GET':
        return render_template('index.html', categoryData=getCategoriesData())
    elif request.method == 'POST':
        reqData = getRequestDataInJson(request.data)
        token = reqData['token']
        reqData = reqData['body']
        userEditing = User.verify_auth_token(token)
        if userEditing is None:
            response = make_response(
                json.dumps('Bad Authorization Token. Please re-login'), 444)
            response.headers['Content-Type'] = 'application/json'
            return response
        print(reqData)

        try:
            category = session.query(Category).\
                filter_by(id=reqData['categoryId']).one()
            user = session.query(User).filter_by(id=userEditing).one()
            if category:
                print('Trying to create a new item now')
                newItem = CatalogItem(
                    name=reqData['name'],
                    description=reqData['description'],
                    categoryId=category.id,
                    creator=user)
                newItem.category = category
                session.add(newItem)
                session.commit()
                fillCatTableData()
                return getCatalogItemJson(newItem)
            else:
                response = make_response(
                    json.dumps('Category Not Found. '
                               'Please select a valid category'), 401)
                response.headers['Content-Type'] = 'application/json'
                return response
        except SQLAlchemyError:
            print("Oops!", sys.exc_info()[0], "occured.")
            response = make_response(
                json.dumps('Error occured while performing DB operations. %s'
                           % str(sys.exc_info()[0])), 500)
            response.headers['Content-Type'] = 'application/json'
            return response


@app.route('/category/new', methods=['GET', 'POST'])
def addCategory():
    """API handler to add a new Category"""
    if request.method == 'GET':
        return render_template('index.html', categoryData=getCategoriesData())
    elif request.method == 'POST':
        reqData = getRequestDataInJson(request.data)
        token = reqData['token']
        reqData = reqData['body']
        userEditing = User.verify_auth_token(token)
        if userEditing is None:
            response = make_response(
                json.dumps('Bad Authorization Token. Please re-login'), 444)
            response.headers['Content-Type'] = 'application/json'
            return response
        print(reqData)

        try:
            user = session.query(User).filter_by(id=userEditing).one()
            newCategory = Category(
                name=reqData['name'],
                description=reqData['description'],
                creator=user)
            session.add(newCategory)
            session.commit()
        except SQLAlchemyError:
            print("Oops!", sys.exc_info()[0], "occured.")
            response = make_response(
                json.dumps('Error occured while performing DB operations. %s'
                           % str(sys.exc_info()[0])), 500)
            response.headers['Content-Type'] = 'application/json'
            return response
        fillCatTableData()
        return getCategoryJson(newCategory)


@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
def editCategory(category_id):
    """API handler to edit a particular category"""
    if request.method == 'GET':
        return render_template('index.html', categoryData=getCategoriesData())
    elif request.method == 'POST':
        reqData = getRequestDataInJson(request.data)
        token = reqData['token']
        reqData = reqData['body']
        userEditing = User.verify_auth_token(token)
        if userEditing is None:
            response = make_response(
                json.dumps('Bad Authorization Token. Please re-login'), 444)
            response.headers['Content-Type'] = 'application/json'
            return response
        print(reqData)

        try:
            categoryToEdit = session.query(Category).\
                filter_by(id=category_id).one()

            if categoryToEdit.creator_id != userEditing:
                response = make_response(json.dumps(
                    'Only owner is allowed to edit this category'), 401)
                response.headers['Content-Type'] = 'application/json'
                return response

            if reqData['name']:
                categoryToEdit.name = reqData['name']
            if reqData['description']:
                categoryToEdit.description = reqData['description']
            session.add(categoryToEdit)
            session.commit()
            categoryAfterEdit = session.query(Category).\
                filter_by(id=category_id).one()
        except SQLAlchemyError:
            print("Oops!", sys.exc_info()[0], "occured.")
            response = make_response(
                json.dumps('Error occured while performing DB operations. %s'
                           % str(sys.exc_info()[0])), 500)
            response.headers['Content-Type'] = 'application/json'
            return response

        fillCatTableData()
        return getCategoryJson(categoryAfterEdit)


@app.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(item_id):
    """API handler to edit the item"""
    if request.method == 'GET':
        return render_template('index.html', categoryData=getCategoriesData())
    elif request.method == 'POST':
        reqData = getRequestDataInJson(request.data)
        token = reqData['token']
        reqData = reqData['body']
        userEditing = User.verify_auth_token(token)
        if userEditing is None:
            response = make_response(
                json.dumps('Bad Authorization Token. Please re-login'), 444)
            response.headers['Content-Type'] = 'application/json'
            return response
        print(reqData)

        try:
            itemToEdit = session.query(CatalogItem).filter_by(id=item_id).one()

            if itemToEdit.creator_id != userEditing:
                response = make_response(json.dumps(
                    'Only owner is allowed to edit this item'), 401)
                response.headers['Content-Type'] = 'application/json'
                return response

            if reqData['name']:
                itemToEdit.name = reqData['name']
            if reqData['description']:
                itemToEdit.description = reqData['description']
            session.add(itemToEdit)
            session.commit()
            itemAfterEdit = session.query(CatalogItem).\
                filter_by(id=item_id).one()
        except SQLAlchemyError:
            print("Oops!", sys.exc_info()[0], "occured.")
            response = make_response(
                json.dumps('Error occured while performing DB operations. %s'
                           % str(sys.exc_info()[0])), 500)
            response.headers['Content-Type'] = 'application/json'
            return response
        fillCatTableData()
        return getCatalogItemJson(itemAfterEdit)


@app.route('/category/<int:category_id>/delete', methods=['GET', 'POST'])
def deleteCategoryAndItsItems(category_id):
    """API handler to delete a category and
    all items associated with this category"""
    if request.method == 'GET':
        return render_template('index.html', categoryData=getCategoriesData())
    else:
        reqData = getRequestDataInJson(request.data)
        token = reqData['token']
        userEditing = User.verify_auth_token(token)
        if userEditing is None:
            response = make_response(
                json.dumps('Bad Authorization Token. Please re-login'), 444)
            response.headers['Content-Type'] = 'application/json'
            return response
        try:
            categoryToDelete = session.query(Category).\
                filter_by(id=category_id).one()

            if categoryToDelete.creator_id != userEditing:
                response = make_response(json.dumps(
                    'Only owner is allowed to delete this category'), 401)
                response.headers['Content-Type'] = 'application/json'
                return response

            itemsForCategory = session.query(CatalogItem).\
                filter(CatalogItem.categoryId == categoryToDelete.id)
            for item in itemsForCategory:
                session.delete(item)
                session.commit()

            session.delete(categoryToDelete)
            session.commit()
        except SQLAlchemyError:
            print("Oops!", sys.exc_info()[0], "occured.")
            response = make_response(
                json.dumps('Error occured while performing DB operations. %s'
                           % str(sys.exc_info()[0])), 500)
            response.headers['Content-Type'] = 'application/json'
            return response

        fillCatTableData()
        return {}


@app.route('/item/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteSingleCatalogItem(item_id):
    """
    API handler to delete a single item
    """
    if request.method == 'GET':
        return render_template('index.html', categoryData=getCategoriesData())
    else:
        reqData = getRequestDataInJson(request.data)
        token = reqData['token']
        userEditing = User.verify_auth_token(token)
        if userEditing is None:
            response = make_response(
                json.dumps('Bad Authorization Token. Please re-login'), 444)
            response.headers['Content-Type'] = 'application/json'
            return response
        try:
            itemToDelete = session.query(CatalogItem)\
                .filter_by(id=item_id).one()

            if itemToDelete.creator_id != userEditing:
                response = make_response(json.dumps(
                    'Only owner is allowed to delete this item'), 401)
                response.headers['Content-Type'] = 'application/json'
                return response
            session.delete(itemToDelete)
            session.commit()
        except SQLAlchemyError:
            print("Oops!", sys.exc_info()[0], "occured.")
            response = make_response(
                json.dumps('Error occured while performing DB operations. %s'
                           % str(sys.exc_info()[0])), 500)
            response.headers['Content-Type'] = 'application/json'
            return response

        fillCatTableData()
        return {}


@app.route('/getAllCategories')
def returnJSONOfAllCatsAndItems():
    """
    Returns a pretty json of all categories and items for each category
    """
    return jsonify(getCategoriesData())


@app.route('/')
@app.route('/items')
@app.route('/categories')
@app.route('/login')
def showAllItems():
    return render_template('index.html', categoryData=getCategoriesData())


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
