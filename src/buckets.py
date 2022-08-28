from re import search
from src.constants.http_status_codes import HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_200_OK, \
    HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_304_NOT_MODIFIED, HTTP_409_CONFLICT
from flask import Blueprint, request, jsonify
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required
from flasgger import swag_from
from src.database import Bucket, Item, db

buckets = Blueprint("buckets", __name__, url_prefix="/api/v1/buckets")

''' 3. Create a new bucket list'''
@buckets.post('/')
@jwt_required()
@swag_from('./docs/buckets/buckets.yml')
def handle_buckets():
    current_user = get_jwt_identity()
    name = request.get_json().get('name', '')

    if not name.strip():
        return jsonify({'message': 'bucketlist name not provided'})

    if db.session.query(Bucket).filter_by(name=name, created_by=current_user).first() is not None:
        return jsonify({'message': 'bucketlist already exists'}), HTTP_400_BAD_REQUEST

    bucket = Bucket(name=name, created_by=current_user)
    db.session.add(bucket)

    try:
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({
            'message': 'error occured while creating bucketlist'}), HTTP_500_INTERNAL_SERVER_ERROR

    return jsonify(bucket.serialize()), HTTP_201_CREATED


''' 4. List all the created bucket lists '''
@buckets.get('/')
@jwt_required()
@swag_from('./docs/buckets/buckets.yml')
def get_bucketlists():
    current_user = get_jwt_identity()
    try:
        page = int(request.args.get('page', 1))
    except Exception:
        return jsonify({'message': 'Invalid Page Value'})
    try:
        limit = int(request.args.get('limit', 20))
    except Exception:
        return jsonify({'message': 'Invalid Limit Value'})
    search = request.args.get('q', '')

    if db.session.query(Bucket).filter_by(created_by=current_user).count() == 0:
        # return jsonify({'message': 'no bucketlist found'})
        return HTTP_400_BAD_REQUEST

    bucketlist_rows = Bucket.query.filter(
        Bucket.created_by == current_user,
        Bucket.name.like('%' + search + '%')).paginate(page, limit, False)

    all_pages = bucketlist_rows.pages
    next_page = bucketlist_rows.has_next
    previous_page = bucketlist_rows.has_prev

    if next_page:
        next_page_url = str(request.url_root) + 'bucketlists?' + \
            'limit=' + str(limit) + '&page=' + str(page + 1)
    else:
        next_page_url = None

    if previous_page:
        previous_page_url = str(request.url_root) + 'bucketlists?' + \
            'limit=' + str(limit) + '&page=' + str(page - 1)
    else:
        previous_page_url = None
    bucketlists = []
    for bucketlist in bucketlist_rows.items:
        bucketlistitems = []
        bucketlistitem_rows = Item.query.filter(
            Item.bucket_id == bucketlist.bucket_id).all()
        for bucketlistitem in bucketlistitem_rows:
            bucketlistitems.append({
                'id': bucketlistitem.item_id,
                'name': bucketlistitem.name,
                'date_created': bucketlistitem.date_created,
                'date_modified': bucketlistitem.date_modified,
                'done': bucketlistitem.done
            })
        bucketlists.append({
            'id': bucketlist.bucket_id,
            'name': bucketlist.name,
            'date_created': bucketlist.date_created,
            'date_modified': bucketlist.date_modified,
            'created_by': bucketlist.created_by,
            'items': bucketlistitems,
        })

    return jsonify(bucketlists)



''' 5 Get single bucket list '''

@buckets.get("/<int:bucket_id>")
@jwt_required()
@swag_from('./docs/buckets/single_bucket.yml')
def get_bucketbyId_(bucket_id):
    user_id = get_jwt_identity()

    if db.session.query(Bucket).filter_by(
            bucket_id=bucket_id, created_by=user_id).count() == 0:
        return jsonify({'message': 'bucket list not found'})

    bucketlist_rows = db.session.query(Bucket).filter_by(
        created_by=user_id, bucket_id=bucket_id).all()
    bucketlists = []
    bucketlistitems = []
    bucketlistitem_rows = db.session.query(Item).filter_by(
        bucket_id=bucket_id).all()
    for bucketlistitem in bucketlistitem_rows:
        bucketlistitems.append({
            'id': bucketlistitem.item_id,
            'name': bucketlistitem.name,
            'date_created': bucketlistitem.date_created,
            'date_modified': bucketlistitem.date_modified,
            'done': bucketlistitem.done
        })
    for bucketlist in bucketlist_rows:
        bucketlists.append({
            'id': bucketlist.bucket_id,
            'name': bucketlist.name,
            'items': bucketlistitems,
            'date_created': bucketlist.date_created,
            'date_modified': bucketlist.date_modified,
            'created_by': bucketlist.created_by
        })

    return jsonify(bucketlists), HTTP_200_OK
    
 
''' 6 Update this bucket list '''
@buckets.put('/<int:bucket_id>')
@jwt_required()
@swag_from('./docs/buckets/update_bucket.yml')
def update_buckets(bucket_id):
    current_user = get_jwt_identity()
    name = request.get_json().get('name', '')
    if not name.strip():
        return jsonify({'message': 'please provide a name'})

    if db.session.query(Bucket).filter_by(bucket_id=bucket_id, created_by=current_user).first() is None:
        return jsonify({'message': 'bucketlist does not exist'})

    # check if it exists
    bucket = Bucket.query.filter_by(created_by=current_user, bucket_id=bucket_id).first()
    bucket.bucket_name = name
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'message': 'error updating bucketlist'}), HTTP_500_INTERNAL_SERVER_ERROR
 
    return jsonify({
        'id': bucket.bucket_id,
        'name': bucket.bucket_name,
        'date_created': bucket.date_created,
        'date_modified': bucket.date_modified,
        'created_by': bucket.created_by,
        'message': 'bucktlist {0} updated succesfully'.format(bucket_id)
    }), HTTP_200_OK



''' 7 Delete single bucket list '''
@buckets.delete("/<int:bucket_id>")
@jwt_required()
@swag_from('./docs/buckets/delete_bucket.yml')
def delete_bucket(bucket_id):
    user_id = get_jwt_identity() # confirm if it's the user who created it

    if db.session.query(Bucket).filter_by(
            bucket_id=bucket_id, created_by=user_id).first() is None:
        return jsonify({'message': 'bucketlist not found'})

    # bucket = Bucket.query.filter_by(created_by=user_id, bucket_id=bucket_id).first()

    # db.session.delete(bucket)
    # db.session.commit()

    db.session.query(Bucket).filter_by(
        bucket_id=bucket_id, created_by=user_id
    ).delete()
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'message': 'error deleting bucketlist'}), HTTP_500_INTERNAL_SERVER_ERROR
    return jsonify({'message': 'successfully deleted bucketlist {0}'.format(bucket_id)}), HTTP_204_NO_CONTENT




''' 8 Create a new item in bucket list '''
@buckets.post("/<int:bucket_id>/items")
@jwt_required()
@swag_from('./docs/buckets/create_bucket_item.yml')
def add_bucket_item(bucket_id):
    user_id = get_jwt_identity() 
    name = request.get_json().get('name', '')
    done = request.get_json().get('done', False)


    if not name.strip():
        return jsonify({'message': 'please provide the name field'})

    if db.session.query(Bucket).filter_by(
            bucket_id=bucket_id, created_by=user_id) is None:
        return jsonify({'message': 'bucketlist not found'}), HTTP_404_NOT_FOUND

    if db.session.query(Item).filter_by(bucket_id=bucket_id,name=name).first() is not None:
        return jsonify({'message': 'bucketlist item already exists'}), HTTP_409_CONFLICT

    item = Item(bucket_id=bucket_id,name=name, done=done)
    db.session.add(item)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'message': 'error adding Bucket item'}), HTTP_500_INTERNAL_SERVER_ERROR
    # send back the Item details
    return jsonify({
        'id': item.item_id,
        'name': item.name,
        'date_created': item.date_created,
        'date_modified': item.date_modified,
        'done': item.done,
        'message':'successfully added item {0}'.format(name)
    }), HTTP_201_CREATED


''' 9 Update a bucket list item '''
@buckets.put("/<int:bucket_id>/items/<int:item_id>")
@jwt_required()
@swag_from('./docs/buckets/update_bucket_item.yml')
def update_bucket_item(bucket_id, item_id):
    current_user = get_jwt_identity()
    done = request.json.get('done')

    if done is None:
        return jsonify({'message': 'please indicate if done'})


    # Check if the current user owns this bucket list
    if db.session.query(Bucket).filter_by(
            bucket_id=bucket_id, created_by=current_user) is None:
        return jsonify({'message': 'bucketlist not found'}), HTTP_304_NOT_MODIFIED

    bucketlistitem = db.session.query(Item).filter_by(
        item_id=item_id).first()
    if bucketlistitem is None:
        return jsonify({'message': 'bucket list item not found'}), HTTP_404_NOT_FOUND
    name = request.json.get('name', bucketlistitem.name)
    if not name.strip():
        return jsonify({'message': 'please enter a valid name'})
    bucketlistitem.name = name
    bucketlistitem.done = done

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'message': 'error updating bucket list item'}), HTTP_500_INTERNAL_SERVER_ERROR
    return jsonify({'message': 'successfully updated bucket list item'}), HTTP_200_OK


''' 10 Delete an item in a bucket list '''


@buckets.delete("/<int:bucket_id>/items/<int:item_id>")
@jwt_required()
@swag_from('./docs/buckets/delete_bucket_item.yml')
def delete_bucket_item(bucket_id, item_id):
    current_user = get_jwt_identity() 

    if db.session.query(Bucket).filter_by(
            bucket_id=bucket_id, created_by=current_user).first() is None:
        return jsonify({'message': 'bucketlist not found'}), HTTP_404_NOT_FOUND

    if db.session.query(Item).filter_by(item_id=item_id).count() == 0:
        return jsonify({'message': 'bucketlist item does not exist'}), HTTP_204_NO_CONTENT

    db.session.query(Item).filter_by(
        item_id=item_id
    ).delete()
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'message': 'error deleting bucketlist item'}),HTTP_500_INTERNAL_SERVER_ERROR
    return jsonify({'message': 'successfully deleted bucketlist item'}), HTTP_204_NO_CONTENT