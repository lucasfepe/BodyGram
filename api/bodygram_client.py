import requests
import base64
import os
from dotenv import load_dotenv
import json

class BodygramClient:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("BODYGRAM_API_KEY")
        self.org_id = os.getenv("BODYGRAM_ORG_ID")
        self.api_base_url = "https://platform.bodygram.com/api"
        self.headers = {
            "Authorization": self.api_key
        }
    
    def encode_image(self, image_path):
        """
        Encode an image to base64 ensuring it meets Bodygram's requirements:
        - 9:16 aspect ratio (portrait orientation)
        - Dimensions between 720x1280 and 1080x1920 pixels
        - Correct orientation
        """
        try:
            # Open the image with PIL
            from PIL import Image, ExifTags
            import io
            
            # Open the image
            img = Image.open(image_path)
            
            # Fix orientation based on EXIF data
            try:
                # Get EXIF data if available
                exif = img._getexif()
                if exif:
                    # Find the orientation tag
                    orientation_tag = None
                    for tag, tag_value in ExifTags.TAGS.items():
                        if tag_value == 'Orientation':
                            orientation_tag = tag
                            break
                    
                    if orientation_tag and orientation_tag in exif:
                        orientation = exif[orientation_tag]
                        
                        # Apply rotation based on orientation value
                        if orientation == 2:
                            img = img.transpose(Image.FLIP_LEFT_RIGHT)
                        elif orientation == 3:
                            img = img.transpose(Image.ROTATE_180)
                        elif orientation == 4:
                            img = img.transpose(Image.FLIP_TOP_BOTTOM)
                        elif orientation == 5:
                            img = img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_90)
                        elif orientation == 6:
                            img = img.transpose(Image.ROTATE_270)
                        elif orientation == 7:
                            img = img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_270)
                        elif orientation == 8:
                            img = img.transpose(Image.ROTATE_90)
                        
                        print(f"Applied orientation correction from EXIF data: {orientation}")
            except Exception as e:
                print(f"Warning: Could not process EXIF orientation: {e}")
            
            # Get current dimensions
            width, height = img.size
            print(f"Image dimensions after orientation fix: {width}x{height}")
            
            # Check if image is in landscape orientation and rotate if needed
            if width > height:
                print("Image is in landscape orientation, rotating to portrait...")
                # Use ROTATE_270 to ensure correct orientation (prevents upside down)
                img = img.transpose(Image.ROTATE_270)
                width, height = height, width
                print(f"Rotated image dimensions: {width}x{height}")
            
            # Calculate current aspect ratio
            current_ratio = width / height
            target_ratio = 9/16  # The required 9:16 aspect ratio
            
            # Crop to 9:16 aspect ratio
            if current_ratio > target_ratio:  # Too wide
                # Need to reduce width
                new_width = int(height * target_ratio)
                left = (width - new_width) // 2
                img = img.crop((left, 0, left + new_width, height))
                width = new_width
            elif current_ratio < target_ratio:  # Too tall
                # Need to reduce height
                new_height = int(width / target_ratio)
                top = (height - new_height) // 2
                img = img.crop((0, top, width, top + new_height))
                height = new_height
            
            print(f"Cropped to 9:16 ratio: {width}x{height}")
            
            # Resize to acceptable dimensions
            target_height = 1600  # A middle value in their range
            target_width = int(target_height * (9/16))
            
            img = img.resize((target_width, target_height), Image.LANCZOS)
            print(f"Final dimensions: {target_width}x{target_height}")
            
            # Optional: Save a copy of the processed image for verification
            debug_path = f"processed_{os.path.basename(image_path)}"
            img.save(debug_path)
            print(f"Saved processed image to {debug_path} for verification")
            
            # Save to a BytesIO object with compression
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=85, optimize=True)
            buffer.seek(0)
            
            # Encode to base64
            return base64.b64encode(buffer.read()).decode()
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            raise
    
    def create_scan(self, user_info, image_paths):
        """Create a body scan with front and right images"""
        # Encode images
        try:
            front_photo_base64 = self.encode_image(image_paths["front"])
            right_photo_base64 = self.encode_image(image_paths["right"])
        except Exception as e:
            print(f"Error encoding images: {e}")
            return None
        
        # Prepare API endpoint
        endpoint = f"{self.api_base_url}/orgs/{self.org_id}/scans"
        
        # Convert height from cm to mm and weight from kg to grams
        height_mm = int(user_info["height"] * 10)
        weight_g = int(user_info["weight"] * 1000)
        
        # Prepare request data
        data = {
            "customScanId": user_info["user_id"],
            "photoScan": {
                "age": user_info.get("age", 30),
                "weight": weight_g,
                "height": height_mm,
                "gender": user_info["gender"],
                "frontPhoto": front_photo_base64,
                "rightPhoto": right_photo_base64
            }
        }
        
        # Make API request
        try:
            print("Sending scan request to Bodygram API...")
            response = requests.post(endpoint, headers=self.headers, json=data)
            
            # Store response data for debugging
            status_code = response.status_code
            response_text = response.text
            
            # Try to parse JSON response
            try:
                response_data = response.json()
            except Exception as e:
                response_data = None
                print(f"Error parsing response JSON: {e}")
            
            # Check status code
            if status_code == 200:
                print("API call successful!")
                return response_data
            else:
                print(f"API request failed with status code {status_code}")
                print(f"Response: {response_text}")
                return None
        except Exception as e:
            print(f"Error making API request: {e}")
            return None
    
    def extract_measurements(self, scan_response):
        """Extract and format measurements from API response"""
        if not scan_response:
            print("No scan response data to extract measurements from")
            return None
        
        # Debug the response structure
        print("\nExtracting measurements from response...")
        
        # Check if 'entry' exists
        if "entry" not in scan_response:
            print("Response doesn't contain 'entry' key")
            print("Response keys:", list(scan_response.keys()))
            return None
        
        entry = scan_response["entry"]
        
        # Check for status
        if "status" in entry:
            status = entry["status"]
            print(f"Scan status: {status}")
            if status != "success":
                print(f"Scan not completed successfully, status: {status}")
                return None
        
        # Check for measurements
        if "measurements" not in entry:
            print("No measurements found in response")
            print("Entry keys:", list(entry.keys()))
            return None
        
        measurements_data = entry["measurements"]
        print(f"Found {len(measurements_data)} measurements")
        
        # Map API measurement names to tailor measurement names
        measurement_mapping = {
            "neckCircumference": "Neck Circumference",
            "acrossBackShoulderWidth": "Shoulder Width",  # Note: this matches the documentation example
            "chestCircumference": "Chest Circumference",
            "waistCircumference": "Waist/Stomach Circumference",
            "armLength": "Sleeve Length",  # This might be different in actual API
            "wristCircumference": "Wrist Circumference",
            "backLength": "Back Length",
            "bicepCircumference": "Bicep Circumference"
        }
        
        # Format measurements for tailor use
        tailor_measurements = {}
        
        for measurement in measurements_data:
            # Check the structure of each measurement
            if "name" not in measurement or "value" not in measurement:
                print(f"Unexpected measurement format: {measurement}")
                continue
                
            api_name = measurement["name"]
            value = measurement["value"]
            unit = measurement.get("unit", "mm")
            
            # Try to find matching tailor measurement
            if api_name in measurement_mapping:
                tailor_name = measurement_mapping[api_name]
                # Convert from mm to inches (1 mm = 0.0393701 inches) if unit is mm
                if unit == "mm":
                    value_inches = value * 0.0393701
                    tailor_measurements[tailor_name] = f"{value_inches:.2f}\""
                else:
                    tailor_measurements[tailor_name] = f"{value} {unit}"
            else:
                # Also collect unknown measurements for debugging
                print(f"Unknown measurement: {api_name} = {value} {unit}")
        
        return tailor_measurements

    def save_avatar(self, scan_response, output_path="avatar.obj"):
        """Save the 3D avatar from the scan response"""
        if not scan_response or "entry" not in scan_response:
            return False
            
        avatar_data = scan_response["entry"].get("avatar", {}).get("data")
        if not avatar_data:
            print("No avatar data found in response")
            return False
            
        try:
            # Decode the base64 avatar data
            decoded_avatar = base64.b64decode(avatar_data)
            
            # Save to file
            with open(output_path, "wb") as f:
                f.write(decoded_avatar)
            
            print(f"3D avatar saved to {output_path}")
            return True
        except Exception as e:
            print(f"Error saving avatar: {e}")
            return False
    
    def run_scan_process(self, user_info, image_paths):
        """Run the full body scan process"""
        # Validate inputs
        required_keys = ["front", "right"]
        for key in required_keys:
            if key not in image_paths:
                print(f"Error: Missing required image '{key}'")
                return None
                
        # Create scan
        scan_response = self.create_scan(user_info, image_paths)
        if not scan_response:
            return None
            
        # Extract measurements
        measurements = self.extract_measurements(scan_response)
        
        # Save avatar
        self.save_avatar(scan_response)
        
        return measurements