# Real Estate Web Application

A full-stack real estate web application built with Python and Flask. This project includes user authentication, property listings, and an admin dashboard for property management.

## How to Run on a Laptop (VS Code)

Follow these steps to run the application on your local machine using Visual Studio Code (VS Code):

1. **Open the Project in VS Code**
   - Open VS Code.
   - Go to `File` -> `Open Folder...` and select the `realestate` folder.

2. **Open a New Terminal**
   - In the top menu of VS Code, click on `Terminal` -> `New Terminal` (or press `` Ctrl + ` ``).

3. **Activate the Virtual Environment**
   - Before running the app, you need to activate the Python virtual environment where all the dependencies are installed.
   - Run the following command in the terminal:
     ```powershell
     .\venv\Scripts\activate
     ```
   - *Note: You should see `(venv)` appear at the beginning of your terminal prompt. This means the virtual environment is successfully activated.*

4. **Start the Flask Server**
   - Run the application by executing this command:
     ```powershell
     python app.py
     ```

5. **Open in Your Browser**
   - The terminal will display text saying something like: `* Running on http://127.0.0.1:5000`
   - Hold down the **`Ctrl`** key on your keyboard and click the `http://127.0.0.1:5000` link in the terminal to view the application in your web browser.

## Features
- Dynamic property listings
- Search and filter functionality
- User registration and login
- Admin dashboard to add/manage properties
