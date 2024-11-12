import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageChops
import torch
from scipy.ndimage import binary_erosion

class ScreentoneFilter:
    """
    Node to apply a manga-style screentone filter with adjustable grayscale quantization levels,
    threshold, overlay pattern, mask shrink, and overlay opacity.
    """

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "dot_spacing": ("INT", {
                    "default": 10,
                    "min": 5,
                    "max": 50,
                    "step": 1,
                }),
                "dot_size": ("INT", {
                    "default": 4,
                    "min": 1,
                    "max": 20,
                    "step": 1,
                }),
                "quantization": ("INT", {
                    "default": 4,
                    "min": 1,
                    "max": 256,
                    "step": 1,
                }),
                "white_threshold": ("FLOAT", {
                    "default": 0.95,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                }),
                "black_threshold": ("FLOAT", {
                    "default": 0.1,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                }),
                "mask_shrink": ("INT", {
                    "default": 5,
                    "min": 0,
                    "max": 10,
                    "step": 1,
                }),
                "overlay_opacity": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                }),
                "mode": (["Multiply", "Screentone Only"],),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_screentone"
    CATEGORY = "pixelworld_ai"

    # Generate a dot pattern for the screentone overlay
    def create_dot_pattern(self, size, spacing, dot_size, color=0):
        pattern = Image.new("L", size, color=255)  # White background
        draw = ImageDraw.Draw(pattern)
        for x in range(0, size[0], spacing):
            for y in range(0, size[1], spacing):
                draw.ellipse((x - dot_size // 2, y - dot_size // 2,
                              x + dot_size // 2, y + dot_size // 2), fill=color)  # Black dots
        return pattern

    def apply_screentone(self, image, dot_spacing, dot_size, quantization, white_threshold, mask_shrink, overlay_opacity, mode, black_threshold):
        # Convert tensor to PIL Image
        image_np = (image.squeeze().cpu().numpy() * 255).astype(np.uint8)
        pil_image = Image.fromarray(image_np)

        # Convert image to grayscale
        grayscale_image = ImageOps.grayscale(pil_image)
        grayscale_array = np.array(grayscale_image)

        # Sort grayscale values and calculate threshold for dark pixels
        sorted_pixels = np.sort(grayscale_array.flatten())
        total_pixels = sorted_pixels.size
        threshold_index = int(black_threshold * total_pixels)
        threshold_value = sorted_pixels[threshold_index]  # Get the pixel value at the threshold

        # Quantization levels are now based on the number of colors selected (1 to 256)
        num_colors = quantization
        bins = np.linspace(threshold_value, 255, num_colors)  # Create bins from threshold to white
        bins[0] = threshold_value  # Ensure pixels below the threshold become pure black
        bins[-1] = 255  # Force the top bin to stay white

        # Apply quantization to the grayscale array
        quantized_image = np.digitize(grayscale_array, bins) * (255 // (num_colors - 1))  # Map to the selected colors
        quantized_image = np.clip(quantized_image, 0, 255)
        quantized_image = Image.fromarray(quantized_image.astype(np.uint8))

        # Generate dot pattern overlay
        img_size = quantized_image.size
        dot_pattern = self.create_dot_pattern(img_size, dot_spacing, dot_size)

        # Adjust opacity of the dot pattern
        if overlay_opacity < 1.0:
            dot_pattern = Image.blend(Image.new("L", img_size, color=255), dot_pattern, overlay_opacity)

        # Create mask for non-white regions (based on threshold)
        mask = quantized_image.point(lambda p: 255 if p < (white_threshold * 255) else 0)
        mask_np = np.array(mask) // 255  # Convert to binary (0 and 1)

        # Apply binary erosion for sharp mask shrink
        if mask_shrink > 0:
            mask_np = binary_erosion(mask_np, structure=np.ones((mask_shrink, mask_shrink))).astype(np.uint8)
        
        mask = Image.fromarray((mask_np * 255).astype(np.uint8))

        # Apply the selected mode
        if mode == "Multiply":
            # Use multiply blend for the dot pattern to create the screentone effect
            blended_image = ImageChops.multiply(quantized_image.convert("RGB"), dot_pattern.convert("RGB"))
            output_image = Image.composite(blended_image, quantized_image.convert("RGB"), mask)
        
        elif mode == "Screentone Only":
            # In "Screentone Only" mode, preserve only the black lineart (pure black pixels)
            lineart = quantized_image.point(lambda p: 0 if p == 0 else 255)  # Make sure lineart is pure black

            # Apply the screentone pattern in multiply mode on top of the lineart (no grey levels)
            blended_image = ImageChops.multiply(lineart.convert("RGB"), dot_pattern.convert("RGB"))

            # The output image is just the multiplied lineart with the dot pattern
            output_image = Image.composite(blended_image, lineart.convert("RGB"), mask)

        # Convert output image back to tensor
        output_tensor = torch.from_numpy(np.array(output_image.convert("L")).astype(np.float32) / 255).unsqueeze(0)

        return (output_tensor,)


# Map the node to its class
NODE_CLASS_MAPPINGS = {
    "ScreentoneFilter": ScreentoneFilter
}

# Display name for UI
NODE_DISPLAY_NAME_MAPPINGS = {
    "ScreentoneFilter": "Screentone Filter"
}
