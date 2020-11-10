from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, ValidationError, validates, pre_load

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(20), nullable=False)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    author = db.Column(db.Integer, db.ForeignKey('user.id'))


# Валидация параметров в POST запросе
def must_not_be_blank(data):
    if not data:
        raise ValidationError("Data not provided.")


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=must_not_be_blank)
    last_name = fields.Str(required=True, validate=must_not_be_blank)
    email = fields.Email(required=True, validate=must_not_be_blank)
    role = fields.Str(required=True, validate=must_not_be_blank)
    state = fields.Str(required=True, validate=must_not_be_blank)

    @validates('role')
    def validate_role(self, role):
        if role in ['author', 'editor']:
            return role
        else:
            raise ValidationError("Expected author or editor.")

    @validates('state')
    def validate_role(self, state):
        if state in ['active', 'inactive', 'deleted']:
            return state
        else:
            raise ValidationError("Expected active or inactive or deleted.")


class PostSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=must_not_be_blank)
    description = fields.Str(required=True, validate=must_not_be_blank)
    author = fields.Int(required=True, validate=must_not_be_blank)


user_schema = UserSchema()
post_schema = PostSchema()


@app.route('/api/users', methods=['GET'])
def get_users():
    """
    @api {get} /api/users

    @apiParam {String} [order_by] сортировка по полю (name, last_name, email)
    @apiParam {Integer} [id] получение элемента по идентификатору
    @apiParam {String} [email] фильтр по полю email
    @apiParam {String} [name_substr] фильтр по полю name (совпадение по подстроке)
    @apiParam {Integer} [limit=5] количество возвращаемых элементов (для пагинации)
    @apiParam {Integer} [offset=0] Количество пропускаемых элементов (для пагинации)
    """
    id = request.args.get("author", type=int)
    limit = request.args.get("limit", default=5, type=int)
    offset = request.args.get("offset", default=0, type=int)
    email = request.args.get("email", "")
    name_substr = request.args.get("name_substr", "")

    order_by_choices = ['name', 'last_name', 'email']
    order_by = request.args.get("order_by", "")
    is_descending = False
    if order_by.startswith("-"):
        is_descending = True
        order_by = order_by[1:]

    total_count = User.query
    items = total_count
    if order_by in order_by_choices:
        if is_descending:
            total_count = total_count.order_by(getattr(User, order_by).desc())
            items = total_count.order_by(getattr(User, order_by).desc())
        else:
            total_count = total_count.order_by(getattr(User, order_by))
            items = total_count.order_by(getattr(User, order_by))
    if id:
        total_count = total_count.get(id)
        return jsonify(user_schema.dump(total_count))
    if email:
        total_count = total_count.filter_by(email=email)
        items = total_count.filter_by(email=email)
    if name_substr:
        search = "%{}%".format(name_substr)
        total_count = total_count.filter(User.name.like(search))
        items = total_count.filter(User.name.like(search))
    if limit:
        items = items.limit(limit)
    if offset:
        items = items.offset(offset)
    result = {"total_count": user_schema.dump(total_count, many=True),
              "items": user_schema.dump(items, many=True)}
    return jsonify(result)


@app.route('/api/users', methods=['POST'])
def new_users():
    """
    @api {post} /api/users

    @apiParam {String} name Имя
    @apiParam {String} last_name Фамилия
    @apiParam {String} email электронная почта
    @apiParam {String} state один из параметров: active, inactive, deleted
    @apiParam {String} role author или editor
    """
    if not request.is_json:
        return {"message": "No input data provided"}, 400
    try:
        data = user_schema.load(request.json)
    except ValidationError as err:
        return err.messages, 422
    email = User.query.filter_by(email=data['email'])
    if len(email.all()) == 0:
        user = User(name=data['name'], last_name=data['last_name'], email=data['email'],
                    state=data['state'], role=data['role'])
        db.session.add(user)
        db.session.commit()
    else:
        return {"message": "This email address is already in use"}, 422
    result = user_schema.dump(User.query.get(user.id))
    return {"message": "Created new user.", "user": result}


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
    @api {get} /api/posts

    @apiParam {String} [order_by] сортировка по полю (name, last_name, email)
    @apiParam {Integer} [author] фильтр по полю author
    @apiParam {Integer} [limit=5] количество возвращаемых элементов (для пагинации)
    @apiParam {Integer} [offset=0] количество пропускаемых элементов (для пагинации)
    """
    author = request.args.get("author", type=int)
    limit = request.args.get("limit", default=5, type=int)
    offset = request.args.get("offset", default=0, type=int)

    order_by_choices = ['name', 'last_name', 'email']
    order_by = request.args.get("order_by", "")
    is_descending = False
    if order_by.startswith("-"):
        is_descending = True
        order_by = order_by[1:]

    total_count = db.session.query(User, Post).join(Post, User.id == Post.author)
    items = total_count
    if order_by in order_by_choices:
        if is_descending:
            total_count = total_count.order_by(getattr(User, order_by).desc())
            items = items.order_by(getattr(User, order_by))
        else:
            total_count = total_count.order_by(getattr(User, order_by))
            items = items.order_by(getattr(User, order_by))
    if author:
        total_count = total_count.filter_by(author=author)
        items = items.filter_by(author=author)
    if limit:
        items = items.limit(limit)
    if offset:
        items = items.offset(offset)
    items = [el.Post for el in items.all()]
    total_count = [el.Post for el in total_count.all()]
    result = {"total_count": post_schema.dump(total_count, many=True),
              "items": post_schema.dump(items, many=True)}
    return jsonify(result)


@app.route('/api/posts', methods=['POST'])
def new_posts():
    """
    @api {post} /api/posts

    @apiParam {String} title загаловок
    @apiParam {String} description описание
    @apiParam {Integer} author id автора
    """
    if not request.is_json:
        return {"message": "No input data provided"}, 400
    try:
        data = post_schema.load(request.json)
    except ValidationError as err:
        return err.messages, 422
    user = User.query.get(data['author'])
    if user is not None:
        post = Post(title=data['title'], description=data['description'], author=data['author'])
        db.session.add(post)
        db.session.commit()
    else:
        return {"message": "The author is not found"}, 422
    result = post_schema.dump(Post.query.get(post.id))
    return {"message": "Created new post.", "post": result}


if __name__ == '__main__':
    app.run(debug=False)
