# Robot-Arm-Control

# Tacit learning research project
The program takes in image data and controls the robot arm to recreate the drawing on paper. 
The arm has 7 degrees of freedom with movable index finger, thumb, wrist, and a 2D linear actuator that the arm is mounted on. 

The program includes two types of drawing techniques

1. Pixel-by-pixel: the arm mvoes in very small steps in both x and y direction to create the draw "pixel-by-pixel"
2. Stroke simulation: the arm uses an existing state-of-the-art image-to-stroke conversion algorithm to generate stroke paths to recreate an image. In this technique, the arm creates linear or curving strokes to recreate the drawing.
