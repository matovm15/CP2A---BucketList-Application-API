# Bookmark RestAPI

----

Create a virtualenv
```shell
$virtualenv bucket-env
```

Activate the environment
```shell
$source bucket-env/bin/activate
```
Install dependencies
```shell
$pip install -r requirements.txt
```

Running the flask dev server
```shell
$flask run # using flask server
    or
$gunicorn src.runner:application # if install gunicorn
```

You can access on web browser
```
flask - http://127.0.0.1:5000

gunicorn - http://127.0.0.1:8000
```
