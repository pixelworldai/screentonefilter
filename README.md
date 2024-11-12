# ComfyUI Screentone Filter Node

This project provides a ComfyUI node to apply a manga-style screentone filter with adjustable grayscale quantization levels, threshold, overlay pattern, mask shrink, and overlay opacity.

## Installation

```sh

cd ComfyUI/custom_nodes
git clone https://github.com/pixelworldai/screentonefilter.git
pip install -r requirements.txt

```
Usage:

-- Not all types of images will work, this works best with cartoon shaded images, play around with the settings to find what works best for your image! --

Screentone only mode:
This removes all color values except for black to keep only the lineart and the screentone overlay

![image](https://github.com/user-attachments/assets/24e9b82c-79e6-4bf4-8901-f7ea7b967bad)

Multiply mode:
This keeps the gray levels and overlays the screentone effect.

![image](https://github.com/user-attachments/assets/a1f4b484-8670-484b-abdd-330f20923679)

More examples:

Input image
![image](https://github.com/user-attachments/assets/bdd62a94-9d4a-4c83-887e-25731b671406)

Multiply
![image](https://github.com/user-attachments/assets/cc0b9811-beea-45b1-8154-5a02bcca9258)

Screentone only
![image](https://github.com/user-attachments/assets/bf6c676f-1218-4765-9101-de093133775f)

Screentone only + quantization: 2 = no shading
![image](https://github.com/user-attachments/assets/56d5b3d2-31c5-4a51-9d0c-7da4d2c80516)

Hope you enjoy!




