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
@swag_from('./docs/buckets/buckets.yml')
def handle_buckets():
    current_user = get_jwt_identity()

    if request.method == 'POST':

        bucket_name = request.get_json().get('bucket_name', '')

        # This Bucket item already exists don't add it again
        # if Bucket.query.filter_by(bucket_name=bucket_name).first():
        #     return jsonify({
        #         'error': 'Bucket name already exists'
        #     }), HTTP_409_CONFLICT

        bucket = Bucket(bucket_name=bucket_name, user_id=current_user)
        db.session.add(bucket)
        db.session.commit()
        # send back the bucketlist details
        return jsonify({
            'bucket_id': bucket.id,
            'bucket_name': bucket.bucket_name,
            'done': bucket.done,
            'date_created': bucket.date_created,
            'date_modified': bucket.date_modified
        }), HTTP_201_CREATED
        #If it's not a post we send back the "GET request for this user
    else:
        # If the user doesn't specify the page we send them page 1
        page = request.args.get('page', 1, type=int)
        size = request.args.get('size', 5, type=int)
        bucket_datas = Bucket.query.filter_by(user_id=current_user).paginate(page=page, per_page=size)

        BucketList1 = list()

        for bucket in bucket_datas.items:
            BucketList1.append({
                'bucket_id': bucket.id,
                'bucket_name': bucket.bucket_name,
                'done': bucket.done,
                'date_created': bucket.date_created,
                'date_modified': bucket.date_modified
            })

        # add page nav to the front-end
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
            'BucketList1': BucketList1, 'meta': meta
        }), HTTP_200_OK


'''Retrieving a single item'''
@buckets.get("/<int:id>")
@jwt_required()
@swag_from('./docs/buckets/single_bucket.yml')
def get_bucket(id):
    user_id = get_jwt_identity()

    bucket = Bucket.query.filter_by(user_id=user_id, id=id).first()

    # if we can't get the item
    if not bucket:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND


    return jsonify({
        'bucket_id': bucket.id,
        'bucket_name': bucket.bucket_name,
        'done': bucket.done,
        'date_created': bucket.date_created,
        'date_modified': bucket.date_modified
    }), HTTP_200_OK


'''Updating Bucketlist Items'''
@buckets.put('/<int:id>')
@buckets.patch('/<int:id>')
@jwt_required()
@swag_from('./docs/buckets/update_bucket.yml')
def update_buckets(id):
    current_user = get_jwt_identity()
    # check if it exists
    bucket = Bucket.query.filter_by(user_id=current_user, id=id).first()

    if not bucket:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND


    bucket_name = request.get_json().get('bucket_name', '')

    bucket.bucket_name = bucket_name

    db.session.commit()
 
    return jsonify({
        'bucket_id': bucket.id,
        'bucket_name': bucket.bucket_name,
        'done': bucket.done,
        'date_created': bucket.date_created,
        'date_modified': bucket.date_modified
    }), HTTP_200_OK



''' Delete Bucket Item'''
@buckets.delete("/<int:id>")
@jwt_required()
@swag_from('./docs/buckets/delete_bucket.yml')
def delete_bucket(id):
    user_id = get_jwt_identity() # confirm if it's the user who created it

    bucket = Bucket.query.filter_by(user_id=user_id, id=id).first()

    if not bucket:
        return jsonify({'message': 'Item not found'}), HTTP_404_NOT_FOUND

    db.session.delete(bucket)
    db.session.commit()

    return jsonify({}), HTTP_204_NO_CONTENT


