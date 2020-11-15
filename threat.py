import cv2
import numpy as np
import time
import sys
import os
from twilio.rest import Client
import pyrebase # for connecting to firebase
import datetime
import firebase_admin
from firebase_admin import  storage 
from firebase_admin import credentials



# if an object is found process it
def pushinfo(obj,initobjs, image):
    if obj not in initobjs:
        #urltoimg = "https://firebasestorage.googleapis.com/v0/b/hackohio-199a4.appspot.com/o/images/"

        #data to save
        date = str(datetime.datetime.now())
        filename = obj +(((date.replace(' ','_')).replace(':','_')).replace('.','_')).strip('-')+".png"
        print(filename)
        data = {
            "object": obj, 
            "time_found": date
        }
        
        log = open("messagelog.txt", 'a')
        try:
            cv2.imwrite(obj+".png", image)
            store.child("images/"+ filename).put(obj+".png")
            blob = bucket.blob("images/"+ filename)

            urltoimg= str(blob.generate_signed_url(datetime.timedelta(seconds=2000), method='GET'))
            secnumber= '+17404058840'
            number = '+18577624985'
            #send message to client
            message = client.messages \
                            .create(
                                body="We saw a " + obj + "at: "+ date + "\n see image at "+
                                urltoimg,
                                #str(storage.child("images/"+ filename).get_url(custom_token)),
                                from_='+12058517392',
                                to=number)
                        
            
            log.write("\n----message sent to " +number +"at" + date+ '\n')
            
        except Exception as e:
                log.write("message unsuccesful to:" +number +"at: " + date+ '\n')
                log.write(e)
        
        try:
            db.child("hackohio-199a4").child("found_objects").push(data)
            log.write("uploaded to db")
        except Exception as e:
            log.write(e + " was not able to upload to db\n")
        log.close() 
        
        initobj.append(obj)


#firebase config
config = {
  "apiKey": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "authDomain": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX.firebaseapp.com",
  "databaseURL": "https://hackohio-199a4.firebaseio.com",
  "storageBucket": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXX.appspot.com",
  "serviceAccount": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.json"
}

#configuration tings
firebase = pyrebase.initialize_app(config)

# get firebase auth
auth =firebase.auth()

#connect to database and storage
db = firebase.database()
store = firebase.storage()


#twilio too
account_sid ='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
auth_token = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
client = Client(account_sid, auth_token)

#f= open("foundorNot.txt", 'r')
#names = f.readlines()
ids= {"person", "dog","gun", "knife","bottle", "cell phone"}
found= []
initobj = []

#uid = "2"
#custom_token = auth.create_custom_token(uid)


cred = credentials.Certificate("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX.json")

# Initialize the app with a service account, granting admin privileges
app = firebase_admin.initialize_app(cred, {
    'storageBucket': 'XXXXXXXXXXXXXXXXXX.com',
}, name='storage')

bucket = storage.bucket(app=app)





#print(message.sid)


CONFIDENCE  = 0.5
SCORE_THRESHOLD=  0.5
IOU_THRESHOLD = 0.5




config_path = "coco/yolov3.cfg"

weights = "coco/yolov3.weights"
labels  = open("coco/coco.names").read().strip().split("\n")

colors = np.random.randint(0, 255, size=(len(labels), 3), dtype="uint8")

net  =cv2.dnn.readNetFromDarknet(config_path,weights)

#get image

path_name = "C:/Users/micha/source/repos/codefromscratch/codefromscratch/busystreet.jpg"

cap = cv2.VideoCapture(0)

while True:

    #image = cv2.imread(path_name)
    _, image  = cap.read()
    file_name = os.path.basename(path_name)
    #git the filename and extension
    filename, ext = file_name.split(".")
    #getting the height and width of the image
    h, w = image.shape[:2]

    #creates a sort of blob from the image 
    blob = cv2.dnn.blobFromImage(image, 1/255.0,(416, 416) , swapRB =True, crop= False)
    
    # sets the first channel input to the blobs found
    net.setInput(blob)

    # sets 
    ln = net.getLayerNames()

    ln = [ln[i[0]-1] for i in net.getUnconnectedOutLayers()]

    start = time.perf_counter()
    layer_outputs = net.forward(ln)
    time_took = time.perf_counter()- start
    font_scale =1
    thickness = 1
    boxes, confidences, class_ids = [], [], []

    #removing all the low confidence boxes
    for output in layer_outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence >CONFIDENCE:
                box = detection[:4] * np.array([w,h,w,h])
                (centerX, centerY, width, height)= box.astype("int")

                x = int(centerX- (width/2))
                y = int(centerY - (height/2))

                boxes.append([x,y, int(width), int(height)])
                confidences.append(float(confidence))
                class_ids.append(class_id)


    # perform the non maximum suppression given the scores defined before
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, SCORE_THRESHOLD, IOU_THRESHOLD)

    if len(idxs) > 0 :
    # loop over the indexes we are keeping
        for i in idxs.flatten():
            # extract the bounding box coordinates
            x, y = boxes[i][0], boxes[i][1]
            w, h = boxes[i][2], boxes[i][3]
            # draw a bounding box rectangle and label on the image
            color = [int(c) for c in colors[class_ids[i]]]
            cv2.rectangle(image, (x, y), (x + w, y + h), color=color, thickness=thickness)
            text = f"{labels[class_ids[i]]}: {confidences[i]:.2f}"
        
            #passing all objects found into found arr
            found.append(text)

            #if the object is in the filter list it send a text to user
            
            if labels[class_ids[i]] in ids:
                pushinfo(labels[class_ids[i]],initobj, image)

            # calculate text width & height to draw the transparent boxes as background of the text
            (text_width, text_height) = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, fontScale=font_scale, thickness=thickness)[0]
            text_offset_x = x
            text_offset_y = y - 5
            box_coords = ((text_offset_x, text_offset_y), (text_offset_x + text_width + 2, text_offset_y - text_height))
            overlay = image.copy()
            cv2.rectangle(overlay, box_coords[0], box_coords[1], color=color, thickness=cv2.FILLED)
            # add opacity (transparency to the box)
            image = cv2.addWeighted(overlay, 0.6, image, 0.4, 0)
            # now put the text (label: confidence %)
            cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=font_scale, color=(0, 0, 0), thickness=thickness)
    cv2.imshow("image", image)
    if(ord("q")==cv2.waitKey(1)):
        break
    
    
cap.release()
cv2.destroyAllWindows()

# for images
#cv2.imwrite(filename + "_yolo3."+ ext, image)
#cv2.imshow("finished", image)
cv2.waitKey(0)







