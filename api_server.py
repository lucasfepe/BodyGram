from flask import Flask, request, jsonify
from flask_cors import CORS
from api.bodygram_client import BodygramClient
import os
from werkzeug.utils import secure_filename
import tempfile

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/scan', methods=['POST'])
def scan():
    try:
        # Get form data
        user_id = request.form.get('user_id', 'anonymous')
        height = float(request.form.get('height'))
        weight = float(request.form.get('weight'))
        gender = request.form.get('gender')
        age = request.form.get('age')
        
        # Create user info dictionary
        user_info = {
            "user_id": user_id,
            "height": height,
            "weight": weight,
            "gender": gender
        }
        
        if age:
            user_info["age"] = int(age)
        
        # Get images from the request
        front_image = request.files.get('front_image')
        profile_image = request.files.get('profile_image')
        
        if not front_image or not profile_image:
            return jsonify({"error": "Both front and profile images are required"}), 400
        
        # Create temporary files for the images
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as front_tmp:
            front_image.save(front_tmp.name)
            front_path = front_tmp.name
            
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as profile_tmp:
            profile_image.save(profile_tmp.name)
            profile_path = profile_tmp.name
        
        image_paths = {
            "front": front_path,
            "right": profile_path
        }
        
        # Initialize client and run process
        bodygram = BodygramClient()
        measurements = bodygram.run_scan_process(user_info, image_paths)
        
        # Clean up temporary files
        os.unlink(front_path)
        os.unlink(profile_path)
        
        if measurements:
            return jsonify({
                "success": True,
                "measurements": measurements
            })
        else:
            return jsonify({
                "success": False,
                "message": "Failed to collect measurements"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)