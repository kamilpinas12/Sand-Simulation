from typing import Tuple
import numpy as np
import cv2
import matplotlib.pyplot as plt
import keyboard


from .element import Element



class Window():
    def __init__(self, window_size: Tuple, num_elements: int = None, element_size: int = 1, scattering_factor: float = 0.9, hourglass:bool = False):
        if num_elements is None:
            self.num_elements = window_size[0] * window_size[1] // 2
        
        elif (window_size[0] * window_size[1]) < num_elements:
           raise Exception(f"{num_elements} is too many elements for {window_size[0]}x{window_size[1]} window size, max number of elements for this window is {window_size[0]*window_size[1]}")
        
        else:
            self.num_elements = num_elements

        self.hourglass =hourglass 
        self.element_size = element_size
        self.scattering_angle = ((1 - scattering_factor) * 45) / 2

        # create empty tab
        x = [None for _ in range(window_size[1])]
        img = [x for _ in range(window_size[0])]
        self.image = np.array(img)
        self.acceleration_x = -1
        self.acceleration_y = 0

        if hourglass:
            for i in range((window_size[1]-1)//2):
                self.image[i: window_size[0]-i, i] = 255
            for i in range((window_size[0]-1)//2):
                self.image[i: window_size[0]-i, window_size[1]-i-1] = 255


        #add sand to image
        added = 0
        elements = []
        for y in range(self.image.shape[0]-1, -1, -1):
            for x in range(self.image.shape[1]):
                if added == self.num_elements:
                    break
                if self.image[y, x] is not None:
                    continue
                new = Element(x, y)
                elements.append(new)
                self.image[y, x] = new
                added += 1
            if added == self.num_elements:
                break
        else:
            raise Exception(f"Not enough space for all elements")
        
        self.elements = np.array(elements)


    def simulation_start(self, delay_ms: int):
        cv2.namedWindow('Simulation')
        angle = 90
        np.random.shuffle(self.elements)
        
        while True:
            if keyboard.is_pressed('q'):
                break

            


            if self.hourglass:
                resize_img = np.ones((self.image.shape[0]*self.element_size, self.image.shape[1]*self.element_size), dtype=np.uint8) * 100
                for i in range(self.image.shape[0]):
                    for j in range(self.image.shape[1]):
                        if self.image[i, j] == 255:
                            resize_img[i*self.element_size: self.element_size*(i+1), j*self.element_size:(j+1)*self.element_size] = 0
            else:
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


        #self.sort_elements(angle)
                

        for i in range(self.elements.size): 
            x, y = self.elements[i].x, self.elements[i].y
            #random = np.random.randint(2)

            if 0 <= angle < 22.5 or angle > 337.5:
                if self.is_move_possible(x-1, y):
                    self.move(x-1, y, i)
                    continue

                elif 0 <= angle < 22.5:
                    if self.is_move_possible(x-1, y-1):
                        self.move(x-1, y-1, i)
                        continue
                    if self.is_move_possible(x-1, y+1):
                        self.move(x-1, y+1, i)
                        continue
                else:
                    if self.is_move_possible(x-1, y+1):
                        self.move(x-1, y+1, i)
                        continue
                    if self.is_move_possible(x-1, y-1):
                        self.move(x-1, y-1, i)
                        continue

                if self.elements[i].is_moving:
                    continue

                if self.scattering_angle <= angle <= 22.5 and self.is_move_possible(x, y-1):
                    self.move(x, y-1, i)
                elif 337.5 <= angle < 360 - self.scattering_angle and self.is_move_possible(x, y+1):
                    self.move(x, y+1, i)


            elif 22.5 < angle <= 67.5:
                if self.is_move_possible(x-1, y-1):
                    self.move(x-1, y-1, i)
                    continue
                    
                elif angle >= 45:
                    if self.is_move_possible(x, y-1):
                        self.move(x, y-1, i)
                        continue
                    if self.is_move_possible(x-1, y):
                        self.move(x-1, y, i) 
                        continue
                else:
                    if self.is_move_possible(x-1, y):
                        self.move(x-1, y, i)
                        continue
                    if self.is_move_possible(x, y-1):
                        self.move(x, y-1, i)
                        continue
                
                if self.elements[i].is_moving:
                    continue
                
                if angle > 45 + self.scattering_angle and self.is_move_possible(x+1, y-1):
                    self.move(x+1, y-1, i)
                elif angle < 45 - self.scattering_angle and self.is_move_possible(x-1, y+1):
                    self.move(x-1, y+1, i)                 



            elif 67.5 < angle <= 112.5:
                if self.is_move_possible(x, y-1):
                    self.move(x, y-1, i)
                    continue

                elif angle >= 90:
                    if self.is_move_possible(x+1, y-1):
                        self.move(x+1, y-1, i)
                        continue
                    if self.is_move_possible(x-1, y-1):
                        self.move(x-1, y-1, i)
                        continue
                else:
                    if self.is_move_possible(x-1, y-1):
                        self.move(x-1, y-1, i)
                        continue
                    if self.is_move_possible(x+1, y-1):
                        self.move(x+1, y-1, i)
                        continue

                if self.elements[i].is_moving:
                    continue

                if angle > 90 + self.scattering_angle and self.is_move_possible(x+1, y):
                    self.move(x+1, y, i)
                elif angle < 90 - self.scattering_angle and self.is_move_possible(x-1, y):
                    self.move(x-1, y, i)
                

            elif 112.5 < angle <= 157.5:
                if self.is_move_possible(x+1, y-1):
                    self.move(x+1, y-1, i)
                    continue

                elif angle >= 135:
                    if self.is_move_possible(x+1, y):
                        self.move(x+1, y, i)
                        continue
                    if self.is_move_possible(x, y-1):
                        self.move(x, y-1, i)
                        continue
                else:
                    if self.is_move_possible(x, y-1):
                        self.move(x, y-1, i)
                        continue
                    if self.is_move_possible(x+1, y):
                        self.move(x+1, y, i)
                        continue

                if self.elements[i].is_moving:
                    continue

                if angle > 135 + self.scattering_angle and self.is_move_possible(x+1, y+1):
                    self.move(x+1, y+1, i)
                elif angle < 135 - self.scattering_angle and self.is_move_possible(x-1, y-1):
                    self.move(x-1, y-1, i)



            elif 157.5 < angle <= 202.5:
                if self.is_move_possible(x+1, y):
                    self.move(x+1, y, i)
                    continue

                elif angle >= 180:
                    if self.is_move_possible(x+1, y+1):
                        self.move(x+1, y+1, i)
                        continue
                    if self.is_move_possible(x+1, y-1):
                        self.move(x+1, y-1, i)
                        continue
                else:
                    if self.is_move_possible(x+1, y-1):
                        self.move(x+1, y-1, i)
                        continue
                    if self.is_move_possible(x+1, y+1):
                        self.move(x+1, y+1, i)
                        continue

                if self.elements[i].is_moving:
                    continue

                if angle > 180 + self.scattering_angle and self.is_move_possible(x, y+1):
                    self.move(x, y+1, i)
                elif angle < 180 - self.scattering_angle and self.is_move_possible(x, y-1):
                    self.move(x, y-1, i)
                
                

            elif 202.5 < angle <= 247.5:
                if self.is_move_possible(x+1, y+1):
                    self.move(x+1, y+1, i)
                    continue

                elif angle >= 225:
                    if self.is_move_possible(x, y+1):
                        self.move(x, y+1, i)
                        continue
                    if self.is_move_possible(x+1, y):
                        self.move(x+1, y, i)
                        continue
                else:
                    if self.is_move_possible(x+1, y):
                        self.move(x+1, y, i)
                        continue
                    if self.is_move_possible(x, y+1):
                        self.move(x, y+1, i)

                if self.elements[i].is_moving:
                    continue      
        
                if angle > 225 + self.scattering_angle and self.is_move_possible(x-1, y+1):
                    self.move(x-1, y+1, i)
                elif angle < 225 - self.scattering_angle and self.is_move_possible(x+1, y-1):
                    self.move(x+1, y-1, i)
                


            elif 247.5 < angle <= 292.5:
                if self.is_move_possible(x, y+1):
                    self.move(x, y+1, i)
                    continue

                elif angle >= 270:
                    if self.is_move_possible(x-1, y+1):
                        self.move(x-1, y+1, i)
                        continue
                    if self.is_move_possible(x+1, y+1):
                        self.move(x+1, y+1, i)
                        continue
                else:
                    if self.is_move_possible(x+1, y+1):
                        self.move(x+1, y+1, i)
                        continue
                    if self.is_move_possible(x-1, y+1):
                        self.move(x-1, y+1, i)
                        continue
                    
                if self.elements[i].is_moving:
                    continue


                if angle > 270 + self.scattering_angle and self.is_move_possible(x-1, y):
                    self.move(x-1, y, i)
                elif angle < 270 - self.scattering_angle and self.is_move_possible(x+1, y):
                    self.move(x+1, y, i)
                
                

            elif 292.5 < angle <= 337.5:
                if self.is_move_possible(x-1, y+1):
                    self.move(x-1, y+1, i)
                    continue

                elif angle >= 315:
                    if self.is_move_possible(x-1, y):
                        self.move(x-1, y, i)
                        continue
                    if self.is_move_possible(x, y+1):
                        self.move(x, y+1, i)
                        continue
                else:
                    if self.is_move_possible(x, y+1):
                        self.move(x, y+1, i)
                        continue
                    if self.is_move_possible(x-1, y):
                        self.move(x-1, y, i)
                        continue

                if self.elements[i].is_moving:
                    continue

                if angle > 315 + self.scattering_angle and self.is_move_possible(x-1, y-1):
                    self.move(x-1, y-1, i)
                elif angle < 315 - self.scattering_angle and self.is_move_possible(x+1, y+1):
                    self.move(x+1, y+1, i)
                
            
            else:
                self.elements[i] = False



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
        self.elements[element_idx].is_moving = True


    def sort_elements(self, angle):
        # na razie z tym działa beznadziejnie
        if angle == 0:
            point_line_distance = lambda elem: elem.x
        elif angle == 90:
            point_line_distance = lambda elem: elem.y
        elif angle == 180:
            point_line_distance = lambda elem: self.image.shape[1]-elem.x
        elif angle == 270:
            point_line_distance = lambda elem: self.image.shape[0]-elem.y
        
        elif 0 < angle < 90:
            a = np.tan(np.deg2rad(-angle + 90))
            point_line_distance = lambda elem: abs(a*elem.x + elem.y)/np.sqrt(a**2 + 1)

        elif 90 < angle < 180:
            a = np.tan(np.deg2rad(-angle - 90))
            c = -a*self.image.shape[1]
            point_line_distance = lambda elem: abs(a*elem.x - elem.y + c)/np.sqrt(a**2 + 1)

        elif 180 < angle < 270:
            a = -np.tan(np.deg2rad(angle-90))
            c = -self.image.shape[0] - a*(-self.image.shape[1])
            point_line_distance = lambda elem: abs(a*elem.x - elem.y - c)/np.sqrt(a**2 + 1)

        elif 270 < angle < 360:
            a = -np.tan(np.deg2rad(angle-90))
            point_line_distance = lambda elem: abs(a*elem.x - elem.y -self.image.shape[0])/np.sqrt(a**2 + 1)

        self.elements = np.array(sorted(self.elements, key=point_line_distance))






    def show_img(self):
        img = np.where(self.image, 255, 0).astype(np.uint8)
        cv2.imshow('hourglass', img)
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