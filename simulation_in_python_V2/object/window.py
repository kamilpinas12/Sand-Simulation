import numpy as np
import cv2
import keyboard
from typing import Tuple


from .element import Element




class Window():
    def __init__(self, window_size: Tuple, num_elements: int = None, element_size: int = 1, hourglass:bool = False, move_threshold: float = 0.005):
        if num_elements is None:
            self.num_elements = window_size[0] * window_size[1] // 2
        
        elif (window_size[0] * window_size[1]) < num_elements:
           raise Exception(f"{num_elements} is too many elements for {window_size[0]}x{window_size[1]} window size, max number of elements for this window is {window_size[0]*window_size[1]}")
        
        else:
            self.num_elements = num_elements

        self.hourglass =hourglass 
        self.element_size = element_size
        self.move_threshold = move_threshold
        
        # create empty tab
        x = [None for _ in range(window_size[1])]
        img = [x for _ in range(window_size[0])]
        self.image = np.array(img)

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
                angle += 10
            if keyboard.is_pressed('s'):
                angle -= 10
            if angle < 0:
                angle = 359
            if angle > 359:
                angle = 0


            print(angle)
            ax, ay = -np.cos(np.deg2rad(angle)), np.sin(np.deg2rad(angle))
            print(ax, ay)
            self.update(ax, ay)
            cv2.waitKey(delay_ms)

        cv2.destroyAllWindows()




    def update(self, ax: float, ay: float):
        dt = 0.1
        acceleration_threshold = 0.1
        resistance_factor = 0.75

        for i in range(self.elements.size):
            # to debug
            elem = self.elements[i]

            #update speed
            if abs(ax) > acceleration_threshold:
                self.elements[i].v_x *= resistance_factor
                self.elements[i].v_x += ax * dt
            if abs(ay) > acceleration_threshold:
                self.elements[i].v_y *= resistance_factor
                self.elements[i].v_y += ay * dt

            moves_x = dt*abs(self.elements[i].v_x) // self.move_threshold
            moves_y = dt*abs(self.elements[i].v_y) // self.move_threshold
            const_moves_x = moves_x
            const_moves_y = moves_y

            if moves_x == 0 and moves_y == 0:
                continue

            #current position
            x, y = self.elements[i].x, self.elements[i].y

            if self.elements[i].v_x >= 0:

                if self.elements[i].v_y > 0:
                    while moves_x or moves_y:
                        if self.is_move_possible(x + 1, y - 1) and moves_x and moves_y:
                            x += 1
                            y -= 1
                            moves_x -= 1
                            moves_y -= 1
                        elif self.is_move_possible(x + 1, y) and moves_x:
                            x += 1
                            moves_x -= 1
                        elif self.is_move_possible(x, y - 1) and moves_y:
                            y -= 1
                            moves_y -= 1
                        else:
                            break

                    if const_moves_x:
                        self.elements[i].v_x = self.move_threshold * (x - self.elements[i].x) / dt
                    if const_moves_y:
                        self.elements[i].v_y = self.move_threshold * -(y - self.elements[i].y) / dt
                    vx = (moves_x * self.move_threshold) / dt
                    vy = (moves_y * self.move_threshold) / dt
                    self.energy_transfer(x + 1, y, vx, 0)
                    self.energy_transfer(x, y - 1, 0, -vy)

                
                    if x != self.elements[i].x or y != self.elements[i].y:
                        self.move(x, y, i)

                else:

                    while moves_x or moves_y:
                        if self.is_move_possible(x + 1, y + 1) and moves_x and moves_y:
                            x += 1
                            y += 1
                            moves_y -= 1
                            moves_x -= 1

                        elif self.is_move_possible(x + 1, y) and moves_x:
                            x += 1
                            moves_x -= 1
                        elif self.is_move_possible(x, y + 1) and moves_y:
                            y += 1
                            moves_y -= 1
                        else: 
                            break

                    if const_moves_x:
                        self.elements[i].v_x = self.move_threshold * (x - self.elements[i].x) / dt
                    if const_moves_y:
                        self.elements[i].v_y = self.move_threshold * -(y - self.elements[i].y) / dt
                    vx = (moves_x * self.move_threshold) / dt
                    vy = (moves_y * self.move_threshold) / dt
                    self.energy_transfer(x + 1, y, vx, 0)
                    self.energy_transfer(x, y + 1, 0, vy)
                    

                    if x != self.elements[i].x or y != self.elements[i].y:
                        self.move(x, y, i)
            

            else:
                if self.elements[i].v_y > 0:
                    while moves_x or moves_y:
                        if self.is_move_possible(x - 1, y - 1) and moves_y and moves_x:
                            x -= 1
                            y -= 1
                            moves_x -= 1
                            moves_y -= 1

                        elif self.is_move_possible(x - 1, y) and moves_x:
                            x -= 1
                            moves_x -= 1
                        elif self.is_move_possible(x, y - 1) and moves_y:
                            y -= 1
                            moves_y -= 1
                        else: 
                            break

                    if const_moves_x:
                        self.elements[i].v_x = self.move_threshold * (x - self.elements[i].x) / dt
                    if const_moves_y:
                        self.elements[i].v_y = self.move_threshold * -(y - self.elements[i].y) / dt
                    vx = (moves_x * self.move_threshold) / dt
                    vy = (moves_y * self.move_threshold) / dt
                    self.energy_transfer(x - 1, y, -vx, 0)
                    self.energy_transfer(x, y - 1, 0, -vy)

                    if x != self.elements[i].x or y != self.elements[i].y:
                        self.move(x, y, i)
                    
                else:

                    while moves_x or moves_y:
                        if self.is_move_possible(x - 1, y + 1) and moves_x and moves_y:
                            x -= 1
                            y += 1
                            moves_x -= 1
                            moves_y -= 1

                        elif self.is_move_possible(x - 1, y) and moves_x:
                            x -= 1
                            moves_x -= 1
                        elif self.is_move_possible(x, y + 1) and moves_y:
                            y += 1
                            moves_y -= 1
                        else: 
                            break


                    if const_moves_x:
                        self.elements[i].v_x = self.move_threshold * (x - self.elements[i].x) / dt
                    if const_moves_y:
                        self.elements[i].v_y = self.move_threshold * -(y - self.elements[i].y) / dt
                    vx = (moves_x * self.move_threshold) / dt
                    vy = (moves_y * self.move_threshold) / dt
                    self.energy_transfer(x - 1, y, -vx, 0)
                    self.energy_transfer(x, y + 1, 0, vy)
                                
                    if x != self.elements[i].x or y != self.elements[i].y:
                        self.move(x, y, i)
                    
    

    def sort_elemetn(self, ax, ay):
        if ay > 0:
            angle = np.rad2deg(np.arctan2(ay, -ax))
        else:
            angle = -np.rad2deg(np.arctan2(ay, ax)) + 180 

        # "normalize" vector
        if ax >= ay:
            val = int(round(ax/ay, 0))
        else:
            val = int(round(ay/ax, 0))






    def energy_transfer(self, x: int, y: int, vx: float, vy: float):
        row, col = self.image.shape
        if not(0 <= x < col):
            return None
        if not(0 <= y < row):
            return None
        
        energy_loss_factor = 1
        if isinstance(self.image[y, x], Element):
            self.image[y, x].v_x += vx * energy_loss_factor
            self.image[y, x].v_y += vy * energy_loss_factor



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