import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import sys
import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
import time
import queue
import os       # Import the os module to interact with the operating system
import platform # Import platform to check OS type

# ===================================================================
# PART 1: THE WEB SCRAPING LOGIC (MODIFIED TO RETURN FILENAME)
# ===================================================================

def scrape_book_details_with_dual_limits():
    """
    Scrapes books and returns the filename upon success, or None on failure.
    """
    PAGE_LIMIT = 4
    BOOK_LIMIT = 49
    base_url = "http://books.toscrape.com/"
    catalogue_url = urljoin(base_url, 'catalogue/')
    current_url = urljoin(catalogue_url, 'page-1.html')
    scraped_data = []
    page_count = 0
    book_count = 0

    while current_url:
        page_count += 1
        if page_count > PAGE_LIMIT:
            print(f"\nReached the page limit of {PAGE_LIMIT}. Stopping.")
            break
        print(f"Scraping catalogue page {page_count}/{PAGE_LIMIT}: {current_url}")
        # ... (The scraping loop is the same as before, so it's shortened here for brevity)
        try:
            response = requests.get(current_url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching catalogue page: {e}")
            break
        soup = BeautifulSoup(response.content, 'lxml')
        books_on_page = soup.find_all('article', class_='product_pod')
        if not books_on_page:
            break
        for book in books_on_page:
            if book_count >= BOOK_LIMIT:
                break 
            book_count += 1
            book_relative_url = book.find('h3').find('a')['href']
            book_absolute_url = urljoin(catalogue_url, book_relative_url)
            print(f"  ({book_count}/{BOOK_LIMIT}) Scraping book detail...")
            try:
                detail_response = requests.get(book_absolute_url)
                detail_response.raise_for_status()
                detail_soup = BeautifulSoup(detail_response.content, 'lxml')
                name = book.find('h3').find('a')['title']
                price = book.find('p', class_='price_color').text
                rating = book.find('p', class_='star-rating').get('class')[1]
                stock_p = detail_soup.find('p', class_='instock availability')
                stock = stock_p.text.strip() if stock_p else 'N/A'
                product_description_div = detail_soup.find('div', id='product_description')
                description_p = product_description_div.find_next_sibling('p') if product_description_div else None
                description = description_p.text if description_p else 'N/A'
                scraped_data.append({
                    'Name': name, 'Price': price, 'Rating': rating,
                    'Stock': stock, 'Description': description
                })
                time.sleep(0.05) # Slightly faster for the demo
            except requests.RequestException:
                continue
        if book_count >= BOOK_LIMIT:
            print(f"\nReached the book limit of {BOOK_LIMIT}. Stopping.")
            break 
        next_button_li = soup.find('li', class_='next')
        if next_button_li:
            current_url = urljoin(catalogue_url, next_button_li.find('a')['href'])
        else:
            current_url = None
    
    if scraped_data:
        print(f"\nScraping complete. Total books found: {len(scraped_data)}")
        csv_file_name = 'books_data_limited_output.csv'
        headers = ['Name', 'Price', 'Rating', 'Stock', 'Description']
        print(f"Saving data to {csv_file_name}...")
        try:
            with open(csv_file_name, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                writer.writerows(scraped_data)
            print(f"\nSUCCESS: Data saved to '{csv_file_name}'.")
            return csv_file_name # Return the filename on success
        except IOError as e:
            print(f"I/O error while writing to CSV: {e}")
    
    return None # Return None if no file was created

# ===================================================================
# PART 2: THE TKINTER GUI APPLICATION (WITH "OPEN FILE" BUTTON)
# ===================================================================

class ScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Scraper")
        self.root.geometry("700x500")
        self.log_queue = queue.Queue()
        self.last_csv_file = None # Variable to store the last created filename

        self.title_label = ttk.Label(root, text="Web Scraper for books.toscrape.com", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        # Frame to hold the buttons side-by-side
        button_frame = ttk.Frame(root)
        button_frame.pack(pady=5)

        self.start_button = ttk.Button(button_frame, text="Start Scraping", command=self.start_scraping_thread)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.open_button = ttk.Button(button_frame, text="Open Last CSV File", command=self.open_csv_file, state=tk.DISABLED)
        self.open_button.pack(side=tk.LEFT, padx=5)

        self.output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=22, state='disabled')
        self.output_text.pack(pady=10, padx=10)

    def start_scraping_thread(self):
        self.start_button.config(state=tk.DISABLED)
        self.open_button.config(state=tk.DISABLED) # Disable while running
        self.output_text.config(state='normal')
        self.output_text.delete('1.0', tk.END)
        
        thread = threading.Thread(target=self.run_scraper)
        thread.start()
        self.process_log_queue()

    def run_scraper(self):
        sys.stdout = TextRedirector(self.log_queue)
        # Capture the returned filename from the scraper function
        csv_filename = scrape_book_details_with_dual_limits()
        # Schedule the completion handler to run on the main thread
        self.root.after(100, self.on_scraping_complete, csv_filename)

    def on_scraping_complete(self, filename):
        """This runs on the main GUI thread after scraping is done."""
        sys.stdout = sys.__stdout__ # Restore original stdout
        self.start_button.config(state=tk.NORMAL) # Re-enable start button
        self.output_text.config(state='disabled')
        
        if filename and os.path.exists(filename):
            self.last_csv_file = filename
            self.open_button.config(state=tk.NORMAL) # Enable the open button
        else:
            self.last_csv_file = None
            self.open_button.config(state=tk.DISABLED) # Keep it disabled if no file

    def open_csv_file(self):
        """Opens the last saved CSV file using the OS's default application."""
        if self.last_csv_file:
            try:
                # This is the most cross-platform way to do it
                if platform.system() == 'Darwin':       # macOS
                    os.system(f'open "{self.last_csv_file}"')
                elif platform.system() == 'Windows':    # Windows
                    os.startfile(self.last_csv_file)
                else:                                   # linux variants
                    os.system(f'xdg-open "{self.last_csv_file}"')
            except Exception as e:
                # If opening fails, show an error in the log
                self.output_text.config(state='normal')
                self.output_text.insert(tk.END, f"\nError opening file: {e}")
                self.output_text.config(state='disabled')

    def process_log_queue(self):
        try:
            message = self.log_queue.get_nowait()
            self.output_text.config(state='normal')
            self.output_text.insert(tk.END, message)
            self.output_text.see(tk.END)
            self.output_text.config(state='disabled')
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_log_queue)

class TextRedirector(object):
    def __init__(self, queue):
        self.queue = queue
    def write(self, str):
        self.queue.put(str)
    def flush(self):
        pass

# ===================================================================
# PART 3: RUNNING THE APPLICATION
# ===================================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = ScraperApp(root)
    root.mainloop()