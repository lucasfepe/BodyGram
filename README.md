# 👔 Bodygram Tailor App

A command-line tool that uses the Bodygram API to generate tailor measurements and 3D avatars from two user photos.

---

## ✅ Prerequisites

Before you begin, make sure you have the following installed:

- [Git](https://git-scm.com/)
- [Python 3.9+](https://www.python.org/downloads/)
- [Visual Studio Code](https://code.visualstudio.com/)
- A **Bodygram API key** and **Organization ID**

---

## 🚀 Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/bodygram-tailor-app.git

# Navigate to the project directory
cd bodygram-tailor-app
```

---

## 🐍 Step 2: Set Up Python Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install requests python-dotenv pillow
```

---

## 🔐 Step 3: Configure API Credentials

Create a `.env` file in the project root with the following content:

```env
BODYGRAM_API_KEY=YourApiKey
BODYGRAM_ORG_ID=YourOrgId
```

---

## 📁 Step 4: Project Structure

Ensure your project is organized as follows:

```
bodygram-tailor-app/
├── .env                 # API credentials
├── main.py              # Main application entry point
├── api/
│   ├── __init__.py
│   └── bodygram_client.py  # Bodygram API client
├── venv/                # Virtual environment (auto-created)
```

---

## 📸 Step 5: Prepare Test Images

Take two photos:
- Front-facing photo
- Right-side facing photo (from the camera's perspective)

**Photo requirements:**
- Good lighting
- Plain background
- Subject wearing form-fitting clothes

Save them in the project directory with names like:

```
front.jpg
side.jpg
```

---

## ▶️ Step 6: Run the Application

```bash
# Make sure your virtual environment is activated
# (venv) should appear in your command prompt

# Run the application
python main.py
```

---

## 📋 Step 7: Follow the Prompts

You'll be asked to input the following:

- User ID (for reference)
- Height in cm (e.g., 177)
- Weight in kg (e.g., 64)
- Gender (male/female)
- Age (or press Enter to use default)
- Paths to your front and side images

---

## 📊 Step 8: View Results

If successful, the application will:
- Display tailor-fit body measurements
- Save a 3D avatar file as `avatar.obj` in your project directory

---

## 🧵 Perfect Fit, Every Time.

Happy tailoring!
