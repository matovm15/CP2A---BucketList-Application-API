from src.constants.http_status_codes import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_201_CREATED, HTTP_200_OK, \
    HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT
from flask import Blueprint, request, jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required
from flasgger import swag_from
from src.database import Bucket, db

buckets = Blueprint("buckets", __name__, url_prefix="/api/v1/buckets")


@buckets.route('/', methods=['POST', 'GET'])
@jwt_required()
def buckets_post():
    current_user = get_jwt_identity()

    if request.method == 'POST':

        #body = request.get_json().get('body', '')
        name = request.get_json().get('name', '')

        if not validators.name(name):
            return jsonify({
                'error': 'Enter a valid url'
            }), HTTP_400_BAD_REQUEST

        if Bucket.query.filter_by(name=name).first():
            return jsonify({
                'error': 'URL already exists'
            }), HTTP_409_CONFLICT

        bucket = Bucket(name=name, user_id=current_user)
        db.session.add(bucket)
        db.session.commit()

        return jsonify({
            'bucket_id': bucket.id,
            'name': bucket.name,
            #'short_url': bucket.short_url,
            #'visit': bucket.visits,
            #'body': bucket.body,
            'date_created': bucket.date_created,
            'date_modified': bucket.date_modified
        }), HTTP_201_CREATED
    else:
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 5, type=int)
        bucket_datas = Bucket.query.filter_by(user_id=current_user).paginate(page=page, per_page=size)

        data = list()

        for bucket in bucket_datas.items:
            data.append({
                'bucket_id': bucket.id,
                'name': bucket.name,
                #'short_url': bucket.short_url,
                #'visit': bucket.visits,
                #'body': bucket.body,
                'date_created': bucket.date_created,
                'date_modified': bucket.date_modified
            })
        meta = {
            "page": bucket_datas.page,
            'pages': bucket_datas.pages,
            'total_count': bucket_datas.total,
            'prev_page': bucket_datas.prev_num,
            'next_page': bucket_datas.next_num,
            'has_next': bucket_datas.has_next,
            'has_prev': bucket_datas.has_prev,

        }
        return jsonify({
            'data': data, 'meta': meta
        }), HTTP_200_OK


@buckets.get("/<int:id>")
@jwt_required()
def get_bucket(id):
    user_id = get_jwt_identity()

    bucket = Bucket.query.filter_by(user_id=user_id, id=id).first()

    if not bucket:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    return jsonify({
        'bucket_id': bucket.id,
        'name': bucket.name,
        #'short_url': bucket.short_url,
        #'visit': bucket.visits,
        #'body': bucket.body,
        'date_created': bucket.date_created,
        'date_modified': bucket.date_modified
    }), HTTP_200_OK


@buckets.put('/<int:id>')
@buckets.patch('/<int:id>')
@jwt_required()
def update_buckets(id):
    user_id = get_jwt_identity()

    bucket = Bucket.query.filter_by(user_id=user_id, id=id).first()

    if not bucket:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    #body = request.get_json().get('body', '')
    name = request.get_json().get('name', '')

    if not validators.name(name):
        return jsonify({
            'error': 'Enter a valid name'
        }), HTTP_400_BAD_REQUEST

    bucket.name = name
    bucket.body = body

    db.session.commit()

    return jsonify({
        'bucket_id': bucket.id,
        'name': bucket.name,
        #'short_url': bucket.short_url,
        #'visit': bucket.visits,
        #'body': bucket.body,
        'date_created': bucket.date_created,
        'date_modified': bucket.date_modified
    }), HTTP_200_OK


@buckets.delete("/<int:id>")
@jwt_required()
def delete_bucket(id):
    user_id = get_jwt_identity()

    bucket = Bucket.query.filter_by(user_id=user_id, id=id).first()

    if not bucket:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    db.session.delete(bucket)
    db.session.commit()

    return jsonify({}), HTTP_204_NO_CONTENT


@buckets.get("/stats")
@jwt_required()
@swag_from('./docs/buckets/stats.yml')
def get_statistics():
    user_id = get_jwt_identity()

    data = []

    items = Bucket.query.filter_by(user_id=user_id).all()

    for item in items:
        new_link = {
            'visits': item.visits,
            'url': item.url,
            'id': item.id,
            'short_url': item.short_url,
        }

        data.append(new_link)
    return jsonify({'data': data}), HTTP_200_OK
