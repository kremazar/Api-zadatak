from app import app
from flask import request
from app.models import User, Objava
from app import db
from flask import jsonify


@app.route('/publicTimeline', methods=['GET', 'POST'])
def javni():
    page = request.args.get('page', 1, type=int)
    if request.method == 'POST':
        before = request.form['before']
        posts = User.query.join(Objava, User.id == Objava.user_id).add_columns(
            User.username, Objava.tekst, Objava.timestamp).filter((Objava.timestamp < before)).paginate(page=page, per_page=10).items
    if request.method == 'GET':
        before = request.form['before']
        posts = User.query.join(Objava, User.id == Objava.user_id).add_columns(
            User.username, Objava.tekst, Objava.timestamp).paginate(page=page, per_page=10).items
    return {"data": [
        {"username": post.username, "tekst": post.tekst, "time": post.timestamp}
        for post in posts
    ]}


@app.route('/user/<id>/privateTimeline', methods=['GET', 'POST'])
def privatni(id):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(id=id).first()
    posts = User.followed_posts(user).paginate(page=page, per_page=5).items
    return {"data": [
        {"username": post.username, "tekst": post.tekst}
        for post in posts
    ]}


@app.route('/')
@app.route('/addPost', methods=['POST'])
def index():
    tekst = request.form['tekst']
    user_id = request.form['user_id']
    add = Objava(tekst=tekst, user_id=user_id)
    db.session.add(add)
    db.session.commit()
    result = {
        'tekst': tekst,
        'user_id': user_id,
    }
    return jsonify({'result': result})


@app.route('/login', methods=['POST'])
def prijava():
    data = request.form
    user = User.authenticate(**data)

    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401
    else:
        return jsonify({'message': 'logged in'})


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    result = {
        'username': username,
        'password': password,
    }
    return jsonify({'result': result})


@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    objava = Objava.query.filter_by(id=id).first()
    db.session.delete(objava)
    db.session.commit()
    return "the post has been deleted"


@app.route('/follow/<id>', methods=['GET', 'POST'])
def prati(id):
    username = request.form['username']
    user = User.query.filter_by(id=id).first()
    current_user = User.query.filter_by(username=username).first()
    current_user.follow(user)
    db.session.commit()
    return 'follow'


@app.route('/unfollow/<id>', methods=['GET', 'POST'])
def neprati(id):
    username = request.form['username']
    user = User.query.filter_by(id=id).first()
    current_user = User.query.filter_by(username=username).first()
    current_user.unfollow(user)
    db.session.commit()
    return 'unfollow'


@app.route('/posts')
def posts():
    posts = Objava.query.all()
    return {"data": [
        {"id": doc.id, "body": doc.tekst, "user_id": doc.user_id, }
        for doc in posts
    ]}


@app.route('/search_user/<username>', methods=['GET', 'POST'])
def search_user(username):
    search = User.query.filter_by(username=username).first()
    return {"data": [
        {"id": search.id, "username": search.username}
    ]}


@app.route('/search_post/<post>')
def search_post(post):
    search = Objava.query.filter_by(tekst=post).all()
    return {"data": [
        {"id": doc.id, "body": doc.tekst, "user_id": doc.user_id, }
        for doc in search
    ]}


@app.route('/recommendation')
def recommendation():
    count = User.query.count()
    id = randint(1, count)
    user = User.query.filter_by(id=id).first()
    return {"data": [
        {"id": user.id, "body": user.username}
    ]}
