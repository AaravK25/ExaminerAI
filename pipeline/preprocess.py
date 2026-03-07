#Image preprocessing
# 2. Increase contrast
# 3. Remove noise
# 4. Binarize (black & white)


import cv2 as cv
import os



def preprocessImg():
    imgs = os.listdir("data\\raw_images")
    proc_imgs=[]
    for img in imgs:             
        path = os.path.join("data\\raw_images", img)        #Joining image path names for OpenCV to receive them properly
        proc_imgs.append(path)

    for proc_img in proc_imgs:
        img = cv.imread(proc_img)
        gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)         #Convert to grayscale           
        alpha = 1.5 #increases contrat highly
        beta = 0.25 #increases brightness slightly
        cont_img = cv.convertScaleAbs(gray_img, alpha=alpha, beta=beta)   # contrasted image
        blur_img = cv.GaussianBlur(cont_img, (5,5), 0)  #to remove noise from image
        binary = cv.adaptiveThreshold(                  #So that text seperates from background, making text black, background white
        blur_img,
        255,
        cv.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv.THRESH_BINARY,
        11,
        2
        )
        filename = os.path.basename(proc_img)
        save_path = os.path.join("data\\processed_images", filename)
        cv.imwrite(save_path,binary)
    
    return "preprocessing successful", f"Images processed: {proc_imgs}",f"Saved: {save_path}"
