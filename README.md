# Book Scraping Application

This project is a Python application that extracts book information from the e-commerce website [books.toscrape.com](http://books.toscrape.com), a site specifically designed for web scraping practice.

The application features a simple Graphical User Interface (GUI) built with Tkinter, allowing users to start the scraping process with a button click and view the progress in real-time.

## Features
- **Web Scraping:** Extracts detailed information for each book, including its Name, Price, Star Rating, Stock Availability, and Product Description.
- **Multi-Page Scraping:** Automatically navigates through multiple catalogue pages.
- **Configurable Limits:** The script is set to scrape a maximum of 4 pages or 49 books, whichever comes first.
- **Graphical User Interface (GUI):** A user-friendly window to start the process and monitor progress.
- **Data Export:** Saves the final extracted data into a structured `books_data_limited_output.csv` file.
- **File Access:** Includes a button to directly open the generated CSV file using the system's default application.


## Requirements
- Python 3.x
- The libraries listed in `requirements.txt`.

## How to Run the Application

Follow these steps to set up and run the project on your local machine.

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/varlabuggaiah/PRODIGY_SD_05.git
    cd PRODIGY_SD_05
    ```

2.  **Create and Activate a Virtual Environment**

    *On Windows:*
    ```bash
    # Create the virtual environment
    py -m venv venv

    # Activate it
    venv\Scripts\activate
    ```
    *On macOS/Linux:*
    ```bash
    # Create the virtual environment
    python3 -m venv venv

    # Activate it
    source venv/bin/activate
    ```

3.  **Install the Required Packages**
    With your virtual environment active, install the necessary libraries from the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Launch the Application**
    Run the main application file.
    ```bash
    python app.py
    ```
    The GUI window will appear. Click the "Start Scraping" button to begin.

## Output
After the scraping process is complete, the application will generate a file named `books_data_limited_output.csv` in the root of the project directory. You can also click the "Open Last CSV File" button in the GUI to view this file directly.