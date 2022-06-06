from flask import request, redirect, render_template, jsonify
from app import app
from models import *
import face_recognition
import numpy as np
from PIL import Image
import pickle
import json
from mask_detection import give_predictions


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/verify')
def verify():
    return render_template('verify.html')


@app.route('/result')
def result():
    return render_template('final.html')


@app.route('/send_details', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        name = request.form['demo-name']
        email = request.form['demo-email']
        gender = request.form['demo-gender']
        age = int(request.form['demo-age'])
        contact = request.form['demo-contact']
        face_encoding = np.array(json.loads(request.form['encoding']))  #TODO
        register_image = request.form['register_image']
        new_User = User(name=name, email=email, gender=gender, age=age, contact=contact,
                        register_image=register_image, face_encoding=pickle.dumps(face_encoding))
        try:
            db.session.add(new_User)
            db.session.commit()
            return redirect('/register')
        except Exception as e:
            print(e)
            return 'There was an issue adding the details of the User to your database'
    else:
        users = User.query.order_by(User.id).all()
        return render_template('register.html', users=users)


@app.route('/verification_details', methods=['POST'])
def details():
    temperature = float(request.form['demo-temp'])
    try:
        user_id = int(request.form['user-id'])
    except:
        user_id = None
    mask_detected = bool(int(request.form['mask-detected']))
    if user_id:
        new_Scan = Scan(mask_detected, temperature, user_id)
        try:
            db.session.add(new_Scan)
            db.session.commit()
            if(new_Scan.temperature < 99.0 and new_Scan.mask_detected == True):
                return render_template('verified.html', person=new_Scan.person)
            elif(new_Scan.temperature < 99.0 and new_Scan.mask_detected == False):
                return render_template('notmask.html', person=new_Scan.person)
            elif(new_Scan.temperature > 99.0 and new_Scan.mask_detected == True):
                return render_template('nottemp.html', person=new_Scan.person)
            else:
                return render_template('failed.html', person=new_Scan.person)
        except Exception as e:
            print(e)
            return 'There was an issue adding the details of the User to your database'
    else:
        if(temperature < 99.0 and mask_detected == True ):
            return render_template('noface.html')
        elif (temperature > 99.0 and mask_detected == True ):
            return render_template('notemp.html')
        elif (temperature < 99.0 and mask_detected == False ):
            return render_template('nomask.html')
        else:
            return render_template('notverified.html')
        
        

@app.route('/register-image', methods=['POST'])
def register_face():
    image = request.files['webcam']
    image = np.array(Image.open(image))
    try:
        face_locations = face_recognition.face_locations(image)
        top, right, bottom, left = face_locations[0]
        face_image = image[top:bottom, left:right]
        face_encoding = face_recognition.face_encodings(face_image)
        dump = pickle.dumps(face_encoding[0])
        return jsonify(face_encoding[0].tolist())
    except:
        return jsonify([])


@app.route('/verify-face', methods=['POST'])
def verify_face():
    image = request.files['webcam']
    image = np.array(Image.open(image))
    try:
        face_locations = face_recognition.face_locations(image)
        top, right, bottom, left = face_locations[0]
        face_image = image[top:bottom, left:right]
        face_encoding = face_recognition.face_encodings(face_image)
        all_users = User.query.all()
        face_encodings = [pickle.loads(user.face_encoding)
                          for user in all_users]
        user_ids = [user.id for user in all_users]
        results = face_recognition.face_distance(
            face_encodings, face_encoding[0])
        best_match_index = np.argmin(results)
        if results[best_match_index] <= 0.35:
            verified_user_id = user_ids[best_match_index]
            print('Person Verified!', 'User ID:', verified_user_id)
        else:
            print(results[best_match_index])
            raise Exception
        return jsonify({'user_id': verified_user_id})  
    except Exception as e:
        print(e)
        print('No face detected!', flush=True)
        return jsonify({'user_id': None})


@app.route('/verify-mask', methods=['POST'])
def verify_mask():
    image = request.files['webcam']
    mask_on = give_predictions(image)
    return jsonify({'mask': int(mask_on)})