import cv2
import os
import numpy as np
from PIL import Image

names = ['None']
point = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,]
face_id = 0
id_num = 0
while(1):
    flag_m = 0
    flag = int(input('\n new register press 1 or login press 2  ==>  '))
    if flag == int(1):
        cam = cv2.VideoCapture(0)
        cam.set(3, 640) # set video width
        cam.set(4, 480) # set video height
        face_detector = cv2.CascadeClassifier('/home/pi/term/database/Cascades/haarcascade_frontface.xml')
        # For each person, enter one numeric face id
        #face_id = input('\n enter user id end press <return> ==>  ')
        id_num = id_num +1
        if id_num == 10:
            id_num = 1
        face_id = id_num
        face_init = input('\n enter user init end press <return> ==>  ')
        names.append(face_init)
        print("\n [INFO] Initializing face capture. Look the camera and wait ...")
        # Initialize individual sampling face count
        count = 0
        while(True):
            ret, img = cam.read()
            img = cv2.flip(img, -1) # flip video image vertically
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_detector.detectMultiScale(gray, 1.3, 5)
            for (x,y,w,h) in faces:
                cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
                count += 1
                # Save the captured image into the datasets folder
                cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])
                cv2.imshow('image', img)
            k = cv2.waitKey(100) & 0xff # Press 'ESC' for exiting video
            if k == 27:
                break
            elif count >= 30: # Take 30 face sample and stop video
                break 
        # Do a bit of cleanup
        cam.release()
        cv2.destroyAllWindows()
        
        # Path for face image database
        path = '/home/pi/end1/dataset'
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        detector = cv2.CascadeClassifier("/home/pi/term/database/Cascades/haarcascade_frontface.xml");
        # function to get the images and label data
        def getImagesAndLabels(path):
            imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
            faceSamples=[]
            ids = []
            for imagePath in imagePaths:
                PIL_img = Image.open(imagePath).convert('L') # convert it to grayscale
                img_numpy = np.array(PIL_img,'uint8')
                id = int(os.path.split(imagePath)[-1].split(".")[1])
                faces = detector.detectMultiScale(img_numpy)
                for (x,y,w,h) in faces:
                    faceSamples.append(img_numpy[y:y+h,x:x+w])
                    ids.append(id)
            return faceSamples,ids
        print ("\n [INFO] For saving your face,. please wait a few seconds.")
        faces,ids = getImagesAndLabels(path)
        recognizer.train(faces, np.array(ids))
        # Save the model into trainer/trainer.yml
        recognizer.write('/home/pi/team/trainer/trainer.yml') # recognizer.save() worked on Mac, but not on Pi
        # Print the numer of faces trained and end program
        #print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))
        

    elif flag == int(2):
        print ("\n [INFO] Look the camera and wait ...")
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read('/home/pi/team/trainer/trainer.yml')
        cascadePath = "/home/pi/term/database/Cascades/haarcascade_frontface.xml"
        faceCascade = cv2.CascadeClassifier(cascadePath)
        font = cv2.FONT_HERSHEY_SIMPLEX
        #iniciate id counter
        id = 0
        id_copy = 0
        point_cnt = 0
        #confidence_copy = 0

        # Initialize and start realtime video capture
        cam = cv2.VideoCapture(0)
        cam.set(3, 640) # set video widht
        cam.set(4, 480) # set video height
        # Define min window size to be recognized as a face
        minW = 0.1*cam.get(3)
        minH = 0.1*cam.get(4)
        flag2 = 1
        while flag2:
            ret, img =cam.read()
            img = cv2.flip(img, -1) # Flip vertically
            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        
            faces = faceCascade.detectMultiScale( 
                gray,
                scaleFactor = 1.2,
                minNeighbors = 5,
                minSize = (int(minW), int(minH)),
               )
            for(x,y,w,h) in faces:
                cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
                id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
                # Check if confidence is less them 100 ==> "0" is perfect match 
                if (confidence < 100):
                    id_copy = id
                    id = names[id]
                    if (confidence> 25):
                        print("\n Are you ",id,"?")
                        flag1 = int(input('\n Yes: 1 or No: 2  ==>  '))
                        if flag1 == 1:
                            point_cnt = point.pop(id_copy)
                            print("\n [INFO] Now ",id,"'s point is ",point_cnt)
                            flag3 = int(input('\n Point Save: 1 or Point Use: 2  ==>  '))
                            flag_m = 1
                            if flag3 == 1:
                                point_cnt = point_cnt + 1
                                point.insert(id_copy, point_cnt)
                                print("\n",id, "'s point : ",point_cnt)
                                flag2 =0
                                break
                            if flag3 == 2:
                                if point_cnt < 10:
                                    print("\n [INFO] Not enough point. Your point will be saved")
                                    point_cnt = point_cnt + 1
                                    point.insert(id_copy, point_cnt)
                                    print("\n[INFO] ",id,"'s point is ",point_cnt)
                                    flag2 =0
                                    break
                                elif point_cnt >= 10:
                                    point_cnt = point_cnt - 10
                                    point.insert(id_copy, point_cnt)
                                    print("\n[INFO] 10 Point used completely. And Now ",id, "'s point : ",point_cnt)
                                    flag2 =0
                                    break
                        elif flag1 == 2:
                            print("\n [INFO] Try again please...")
                            flag2 = 0
                            continue
                else:
                    flag2 = 1
                    continue
                        #confidence = " {0}%".format(round(100 - confidence))
        # Do a bit of cleanup
    if flag_m:
        print("\n [INFO] Thanks  for using!")
    cam.release()
    cv2.destroyAllWindows()