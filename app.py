from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, ValidationError, validates, pre_load

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base.db'
db = SQLAlchemy(app)


class User(db.Model):
    """User (поля name, last_name, email, role (author, editor), state (active, inactive, deleted))"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(20), nullable=False)


class Post(db.Model):
    """Post (поля title, description, author (ссылка на таблицу User)."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    author = db.Column(db.Integer, db.ForeignKey('user.id'))


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


def paramtres_order_by(data):
    if not data in ['name', 'last_name', 'email']:
        raise ValidationError("Expected name or last_name or email")


class PrUserSchema(Schema):
    id = fields.Int()
    offset = fields.Int()
    limit = fields.Int()
    order_by = fields.Str(validate=paramtres_order_by)
    name_substr = fields.Str()
    email = fields.Email()

    @pre_load
    def default_parametres(self, data):
        limit = data.get("limit")
        offset = data.get("offset")
        if limit is None:
            limit = 5
        if offset is None:
            offset = 0
        data["offset"] = limit
        data["limit"] = offset
        return data


class PrPostSchema(Schema):
    offset = fields.Int()
    limit = fields.Int()
    order_by = fields.Str(validate=paramtres_order_by)
    author = fields.Int()


paramtres_post_schema = PrPostSchema()
paramtres_user_schema = PrUserSchema()
user_schema = UserSchema()
post_schema = PostSchema()


@app.route('/api/users', methods=['GET'])
def get_users():
    """
    @api {get} /api/users
    @apiParam {String} [order_by]
    @apiParam {Integer} [id]
    @apiParam {String} [email]
    @apiParam {String} [name_substr]
    @apiParam {Integer} [limit=5]
    @apiParam {Integer} [offset=0]
    """
    if not request.is_json:
        return {"message": "No input data provided"}, 400
    try:
        dict_params = paramtres_user_schema.load(request.json)
    except ValidationError as err:
        return err.messages, 422
    if len(dict_params) == 0:
        return {"message": "Data not provided."}, 422
    total_count = User.query
    items = None
    if 'order_by' in dict_params:
        total_count = total_count.order_by(User.__dict__[dict_params['order_by']])
        if items is None:
            items = total_count.order_by(User.__dict__[dict_params['order_by']])
    if 'id' in dict_params:
        total_count = total_count.get(dict_params['id'])
        return jsonify(user_schema.dump(total_count))
    if 'email' in dict_params:
        total_count = total_count.filter_by(email=dict_params['email'])
    if 'name_substr' in dict_params:
        search = "%{}%".format(dict_params['name_substr'])
        total_count = total_count.filter(User.name.like(search))
    if 'limit' in dict_params:
        if items is None:
            items = total_count.limit(dict_params['limit'])
        else:
            items = items.limit(dict_params['limit'])
    if 'offset' in dict_params:
        if items is None:
            items = total_count.offset(dict_params['offset'])
        else:
            items = items.offset(dict_params['offset'])
    result = {"total_count": user_schema.dump(total_count, many=True),
              "items": user_schema.dump(items, many=True)}
    return jsonify(result)


@app.route('/api/users', methods=['POST'])
def new_users():
    """
    @api {post} /api/users
    @apiParam {String} name
    @apiParam {String} last_name
    @apiParam {String} email
    @apiParam {String} state
    @apiParam {String} role
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
    return {"message": "Created new user.", "post": result}


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
    @api {get} /api/posts
    @apiParam {String} [order_by]
    @apiParam {Integer} [author]
    @apiParam {Integer} [limit=5]
    @apiParam {Integer} [offset=0]
    """
    if not request.is_json:
        return {"message": "No input data provided"}, 400
    try:
        dict_params = paramtres_post_schema.load(request.json)
    except ValidationError as err:
        return err.messages, 422
    if len(dict_params) == 0:
        return {"message": "Data not provided."}, 422
    total_count = db.session.query(User, Post).join(Post, User.id == Post.author)
    items = None
    if 'order_by' in dict_params:
        total_count = total_count.order_by(User.__dict__[dict_params['order_by']])
        if items is None and ('limit' in dict_params or 'offset' in dict_params):
            items = total_count.order_by(User.__dict__[dict_params['order_by']])
    if 'author' in dict_params:
        total_count = total_count.filter_by(author=dict_params['author'])
    if 'limit' in dict_params:
        if items is None:
            items = total_count.limit(dict_params['limit'])
        else:
            items = items.limit(dict_params['limit'])
    if 'offset' in dict_params:
        if items is None:
            items = total_count.offset(dict_params['offset'])
        else:
            items = items.offset(dict_params['offset'])
    if items is not None:
        items = [el.Post for el in items.all()]
    total_count = [el.Post for el in total_count.all()]
    result = {"total_count": post_schema.dump(total_count, many=True),
              "items": post_schema.dump(items, many=True)}
    return jsonify(result)


@app.route('/api/posts', methods=['POST'])
def new_posts():
    """
    @api {post} /api/posts
    @apiParam {String} title
    @apiParam {String} description
    @apiParam {Integer} author
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
    app.run(debug=True)
