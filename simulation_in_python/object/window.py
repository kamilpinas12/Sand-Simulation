from typing import Tuple
import numpy as np
import cv2
import matplotlib.pyplot as plt
import keyboard


from object.element import Element



class Window():
    def __init__(self, window_size: Tuple, num_elements: int = None, element_size: int = 1, scattering_factor: float = 0.5):
        if num_elements is None:
            self.num_elements = window_size[0] * window_size[1] // 2
        
        elif (window_size[0] * window_size[1]) < num_elements:
           raise Exception(f"{num_elements} is too many elements for {window_size[0]}x{window_size[1]} window size, max number of elements for this window is {window_size[0]*window_size[1]}")
        
        else:
            self.num_elements = num_elements

        self.element_size = element_size
        self.scattering_angle = ((1 - scattering_factor) * 45) / 2

        # create empty tab
        x = [None for _ in range(window_size[1])]
        img = [x for _ in range(window_size[0])]
        self.image = np.array(img)
        self.acceleration_x = -1
        self.acceleration_y = 0



        #add sand to image
        added = 0
        elements = []
        for y in range(self.image.shape[0]-1, -1, -1):
            for x in range(self.image.shape[1]):
                if added == self.num_elements:
                    break
                new = Element(x, y)
                elements.append(new)
                self.image[y, x] = new
                added += 1
            if added == self.num_elements:
                break
        self.elements = np.array(elements)


    def simulation_start(self, delay_ms: int):
        cv2.namedWindow('Simulation')
        angle = 0
        
        while True:
            if keyboard.is_pressed('q'):
                break

            resize_img = np.zeros((self.image.shape[0]*self.element_size, self.image.shape[1]*self.element_size), dtype=np.uint8)
            
            for i in range(self.elements.size):
                x, y = self.elements[i].x, self.elements[i].y
                resize_img[y*self.element_size: self.element_size*(y+1), x*self.element_size:(x+1)*self.element_size] = 255

            rotated_image = rotate_image(resize_img, angle+90)

            cv2.imshow('Simulation', rotated_image)
            if keyboard.is_pressed('w'):
                angle += 1
            if keyboard.is_pressed('s'):
                angle -= 1
            if angle < 0:
                angle = 359
            if angle > 359:
                angle = 0

            print(angle)
            self.update(angle)
            cv2.waitKey(delay_ms)

        cv2.destroyAllWindows()



    def update(self, angle=None):
        #calculate angle
        if angle is None:
            if self.acceleration_y > 0:
                x = -self.acceleration_x
                angle = np.rad2deg(np.arctan2(self.acceleration_y, x))
            else:
                angle = -np.rad2deg(np.arctan2(self.acceleration_y, self.acceleration_x)) + 180

        self.sort_elements(angle)
         
        # coś jest popsute dla angle = 296 !!!!!!!

        for i in range(self.elements.size): 
            x, y = self.elements[i].x, self.elements[i].y
            #random = np.random.randint(2)

            if 0 <= angle < 22.5 or angle > 337.5:
                if self.is_move_possible(x-1, y):
                    self.move(x-1, y, i)
                elif 0 <= angle < 22.5 and self.is_move_possible(x-1, y-1):
                    self.move(x-1, y-1, i)
                elif self.is_move_possible(x-1, y+1):
                    self.move(x-1, y+1, i)
                # elif angle == 0:
                #     if self.is_move_possible(x-1, y-1) and random == 1:
                #         self.move(x-1, y-1, i)
                #     elif self.is_move_possible(x-1, y+1) and random == 0:
                #         self.move(x-1, y+1, i)
                elif self.scattering_angle <= angle <= 22.5 and self.is_move_possible(x, y-1):
                    self.move(x, y-1, i)
                elif 337.5 <= angle <= 360 - self.scattering_angle and self.is_move_possible(x, y+1):
                        self.move(x, y+1, i)

            elif 22.5 < angle <= 67.5:
                if self.is_move_possible(x-1, y-1):
                    self.move(x-1, y-1, i)

                elif angle >= 45 and self.is_move_possible(x+1, y-1):
                    self.move(x+1, y-1, i)
                elif self.is_move_possible(x-1, y):
                    self.move(x-1, y, i)

                elif angle > 45 + self.scattering_angle and self.is_move_possible(x+1, y-1):
                    self.move(x+1, y-1, i)
                elif angle < 45 - self.scattering_angle and self.is_move_possible(x-1, y+1):
                    self.move(x-1, y+1, i)                 

            elif 67.5 < angle <= 112.5:
                if self.is_move_possible(x, y-1):
                    self.move(x, y-1, i)

                elif angle >= 90 and self.is_move_possible(x+1, y-1):
                    self.move(x+1, y-1, i)
                elif self.is_move_possible(x-1, y-1):
                    self.move(x-1, y-1, i)

                elif angle > 90 + self.scattering_angle and self.is_move_possible(x+1, y):
                    self.move(x+1, y, i)
                elif angle < 90 - self.scattering_angle and self.is_move_possible(x-1, y):
                    self.move(x-1, y, i)
                

            elif 112.5 < angle <= 157.5:
                if self.is_move_possible(x+1, y-1):
                    self.move(x+1, y-1, i)

                elif angle >= 135 and self.is_move_possible(x+1, y):
                    self.move(x+1, y, i)
                elif self.is_move_possible(x, y-1):
                    self.move(x, y-1, i)

                elif angle > 135 + self.scattering_angle and self.is_move_possible(x+1, y+1):
                    self.move(x+1, y+1, i)
                elif angle < 130 - self.scattering_angle and self.is_move_possible(x-1, y-1):
                        self.move(x-1, y-1, i)

            elif 157.5 < angle <= 202.5:
                if self.is_move_possible(x+1, y):
                    self.move(x+1, y, i)

                elif angle >= 180 and self.is_move_possible(x+1, y+1):
                    self.move(x+1, y+1, i)
                elif self.is_move_possible(x+1, y-1):
                    self.move(x+1, y-1, i)

                elif angle > 180 + self.scattering_angle and self.is_move_possible(x, y+1):
                    self.move(x, y+1, i)
                elif angle < 180 - self.scattering_angle and self.is_move_possible(x, y-1):
                    self.move(x, y-1, i)
                

            elif 202.5 < angle <= 247.5:
                if self.is_move_possible(x+1, y+1):
                    self.move(x+1, y+1, i)

                elif angle >= 225 and self.is_move_possible(x+1, y):
                    self.move(x+1, y, i)
                elif self.is_move_possible(x, y+1):
                    self.move(x, y+1, i)

                elif angle > 225 + self.scattering_angle and self.is_move_possible(x-1, y+1):
                    self.move(x-1, y+1, i)
                elif angle < 255 - self.scattering_angle and self.is_move_possible(x+1, y-1):
                    self.move(x+1, y-1, i)


            elif 247.5 < angle <= 292.5:
                if self.is_move_possible(x, y+1):
                    self.move(x, y+1, i)

                elif angle >= 270 and self.is_move_possible(x+1, y+1):
                    self.move(x+1, y+1, i)
                elif self.is_move_possible(x-1, y+1):
                    self.move(x-1, y+1, i)

                elif angle > 270 + self.scattering_angle and self.is_move_possible(x-1, y):
                    self.move(x-1, y, i)
                elif angle < 270 - self.scattering_angle and self.is_move_possible(x+1, y):
                    self.move(x+1, y, i)
                

            elif 292.5 < angle <= 337.5:
                if self.is_move_possible(x-1, y+1):
                    self.move(x-1, y+1, i)

                elif angle > 315 and self.is_move_possible(x-1, y):
                    self.move(x-1, y, i)
                elif self.is_move_possible(x, y+1):
                    self.move(x, y+1, i)

                elif angle > 315 + self.scattering_angle and self.is_move_possible(x-1, y-1):
                    self.move(x-1, y-1, i)
                elif angle < 315 - self.scattering_angle and self.is_move_possible(x+1, y-1):
                    self.move(x+1, y-1, i)
                

    def is_move_possible(self, x: int, y: int):
        row, col = self.image.shape
        if not(0 <= x < col):
            return False
        if not(0 <= y < row):
            return False
        
        if self.image[y, x] is None:
            return True
        return False

    def move(self, x: int, y: int, element_idx: int):
        self.image[y, x] = self.image[self.elements[element_idx].y, self.elements[element_idx].x]
        self.image[self.elements[element_idx].y, self.elements[element_idx].x] = None
        self.elements[element_idx].x, self.elements[element_idx].y = x, y

    def sort_elements(self, angle):
        pass







    def show_img(self):
        img = np.where(self.image, 255, 0).astype(np.uint8)
        cv2.imshow('Klepsydra', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()




def rotate_image(rotateImage, angle): 
    imgHeight, imgWidth = rotateImage.shape[0], rotateImage.shape[1] 
  
    centreY, centreX = imgHeight//2, imgWidth//2
  
    rotationMatrix = cv2.getRotationMatrix2D((centreY, centreX), angle, 1.0) 
 
    cosofRotationMatrix = np.abs(rotationMatrix[0][0]) 
    sinofRotationMatrix = np.abs(rotationMatrix[0][1]) 

    newImageHeight = int((imgHeight * sinofRotationMatrix) +
                         (imgWidth * cosofRotationMatrix)) 
    newImageWidth = int((imgHeight * cosofRotationMatrix) +
                        (imgWidth * sinofRotationMatrix)) 
 
    rotationMatrix[0][2] += (newImageWidth/2) - centreX 
    rotationMatrix[1][2] += (newImageHeight/2) - centreY 
  
    rotatingimage = cv2.warpAffine( 
        rotateImage, rotationMatrix, (newImageWidth, newImageHeight)) 
  
    return rotatingimage