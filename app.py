from flask import Flask, render_template,request
from picamera2 import Picamera2
import libcamera
from time import sleep
import time
import os
import cv2
import face_recognition
import numpy as np

app = Flask(__name__)
name = 'non'
captured =0
id = 0
verify = False
faceImages=[]

def findEncodings(images):
            encodeList = []
            for img in images:
                im = face_recognition.load_image_file(f'./static/{img}')
                print(im.shape)
                encode = face_recognition.face_encodings(im)
                print(len(encode))
                if len(encode) == 0:
                    print('No face found in the image')
                    os.remove(f'./static/{img}')
                    return [0]
                else:    
                    encode = encode[0]
                encodeList.append(encode)
            return encodeList

def faceRec():
    try:
        global faceImages
        faceImages=[]
        face_path = './static/'
        listd = os.listdir(face_path)
        print('Fetching saved images...')

        for d in listd:
            sp = d.split('.')
            if sp[-1] == 'jpg':
                faceImages.append(d)
        print(faceImages)
        print('Done fetching!')

        

        print('Encoding known images..')
        encList = findEncodings(faceImages)
        if encList == [0]:
            return False,0
        print('Done encoding!')

        print('Stand in front of the camera.')
        time.sleep(2)
        filename = './static2/newpic.jpg'
        os.system('libcamera-still -o ./static2/newpic.jpg')

        print("Comparing...")

        img = face_recognition.load_image_file(filename)

        facesCurFrame = face_recognition.face_locations(img)
        encodeCurFrame = face_recognition.face_encodings(img, facesCurFrame)

        res = 'initial_val'
        print(len(facesCurFrame), len(encodeCurFrame))

        for encodeFace, faceLoc in zip(encodeCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encList, encodeFace)
            faceDis = face_recognition.face_distance(encList, encodeFace)

            matchIndex = np.argmin(faceDis)
            print('matches[matchIndex]', matches[matchIndex])

            if matches[matchIndex]:
                print('Found match')
                return True, matchIndex
            else:
                print('Unknown')
                return False,0
        #os.remove(filename)
        print('Done comparing!', res)
        time.sleep(0.1)
        return False,0

    except KeyboardInterrupt:
        print('error')
        return False,0


def capturePic(Name,n):
    picam2 = Picamera2()
    preview_config = picam2.create_preview_configuration(main={"format": 'BGR888','size':(1280,720)})
    #preview_config["transform"] = libcamera.Transform(hflip=1, vflip=1)
    picam2.configure(preview_config)
    picam2.start()
    image = picam2.capture_image("main")
    image.save('./static/img'+Name+str(n)+'.jpg')
    picam2.stop()
    picam2.close()

@app.route('/', methods=['POST','GET'])
def index():
    global name
    #if the verfy button is press
    if request.method == "POST":
        global captured, faceImages
        
        global verify
        verify = faceRec()
        print(verify[0])
        if verify[0] == True:
            name = faceImages[verify[1]]
            name = name.split('.')[0][3:]
            print(name)
            return render_template('index.html',Aut=verify[0],name=name)
        else:
            return render_template('index.html',Aut=verify[0],name=name)
    else:
        pass
    return render_template('index.html',Aut=verify,name=name)




@app.route('/delete',methods=['POST','GET'])
def delete():
    if request.method == 'POST':
        global name
        global captured
        global verify
        verify = False
        captured=0
        name = 'non'
    else:
        pass
    return render_template('index.html')

@app.route('/input',methods=['POST','GET'])
def input():
    if request.method == 'POST':
        global name
        global id
        global captured
        name = request.form['name']
        id = request.form['id']
        captured=1
        capturePic(name,1)
        #sleep(2)
        capturePic(name,2)
        images=['img'+name+'1.jpg','img'+name+'2.jpg']
        if findEncodings(images) == [0]:
            captured = False
        return render_template('input.html',captured=captured,name=name)
    else:
        pass
    return render_template('input.html')

@app.route('/confermation')
def conf():
    return render_template('index.html')



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0' , port=5000)
