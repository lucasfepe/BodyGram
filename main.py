from api.bodygram_client import BodygramClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    # Check if API key and org ID are set
    if not os.getenv("BODYGRAM_API_KEY") or not os.getenv("BODYGRAM_ORG_ID"):
        print("Error: BODYGRAM_API_KEY and BODYGRAM_ORG_ID must be set in .env file")
        return
    
    print("Bodygram Tailor Measurements App")
    print("--------------------------------")
    print("This CLI version uses the actual Bodygram API to extract measurements from photos.")
    
    # Get user info
    user_id = input("Enter user ID (for reference): ")
    height = float(input("Enter height in cm: "))
    weight = float(input("Enter weight in kg: "))
    gender = input("Enter gender (male/female): ")
    age = input("Enter age (or press Enter for default): ")
    
    user_info = {
        "user_id": user_id,
        "height": height,
        "weight": weight,
        "gender": gender
    }
    
    if age.strip():
        user_info["age"] = int(age)
    
    # Get image paths
    print("\nThe Bodygram API requires two photos:")
    print("1. A front-facing photo")
    print("2. A right-side facing photo")
    
    front_image = input("\nPath to front-facing image: ")
    right_image = input("Path to right-side facing image: ")
    
    if not os.path.isfile(front_image) or not os.path.isfile(right_image):
        print("Error: One or more image files not found")
        return
    
    image_paths = {
        "front": front_image,
        "right": right_image
    }
    
    # Initialize client and run process
    print("\nProcessing your request...")
    bodygram = BodygramClient()
    measurements = bodygram.run_scan_process(user_info, image_paths)
    
    if measurements:
        print("\n=== Your Tailor Measurements ===")
        for name, value in measurements.items():
            print(f"{name}: {value}")
        print("\nMeasurements successfully collected!")
        print("A 3D avatar file (avatar.obj) has also been saved to the current directory.")
    else:
        print("Failed to collect measurements. Please check your API credentials and images.")

if __name__ == "__main__":
    main()