import csv
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
import pyperclip  # Import pyperclip for clipboard functionality
import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


# Function to scrape website data
def scrape_website(url, tags):
    try:
        # Send HTTP request
        response = requests.get(url)
        response.raise_for_status()  # Will raise HTTPError if the status code is not 200

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, "html.parser")

        # Dictionary to hold extracted data
        extracted_data = {}

        # Extract content based on the provided tags
        for tag in tags:
            elements = soup.find_all(tag)  # Find all occurrences of the tag
            if elements:
                extracted_data[tag] = [element.get_text(strip=True) for element in elements]

        if not extracted_data:
            messagebox.showwarning("No Data", "No data found for the provided tags!")
            return None

        return extracted_data

    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error fetching the page: {e}")
        return None

# Function to save data to CSV file
def save_data_to_csv(data, filename):
    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Tag", "Extracted Text"])

            # Save each tag's text content line by line
            for tag, text_list in data.items():
                for text in text_list:
                    lines = text.splitlines()  # Split the text into multiple lines if it exceeds one line
                    for line in lines:
                        writer.writerow([tag, line])  # Write each line as a new row

        messagebox.showinfo("Success", f"Data saved to {filename}")
    except Exception as e:
        messagebox.showerror("Error", f"Error saving data to CSV: {e}")

# Function to save data to PDF
def save_data_to_pdf(data, filename):
    try:
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter

        # Add title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(30, height - 40, "Scraped Data")

        y_position = height - 60  # Set initial Y position

        # Save each tag's text content line by line
        for tag, texts in data.items():
            c.setFont("Helvetica", 12)
            c.drawString(30, y_position, f"{tag}:")
            y_position -= 20
            c.setFont("Helvetica", 12)
            for text in texts:
                lines = text.splitlines()  # Split the text into multiple lines
                for line in lines:
                    c.drawString(50, y_position, f"- {line}")
                    y_position -= 15
                y_position -= 10  # Space between tags

        c.save()
        messagebox.showinfo("Success", f"Data saved to {filename}")
    except Exception as e:
        messagebox.showerror("Error", f"Error saving data to PDF: {e}")

# Function to copy the content from the result_text to clipboard
def copy_to_clipboard(result_text_widget):
    try:
        # Extract content from the Text widget, strip trailing newlines
        content = result_text_widget.get("1.0", "end-1c").strip()
        
        # Check if there is any content to copy
        if content:
            pyperclip.copy(content)  # Copy the content to the clipboard
            messagebox.showinfo("Success", "Content copied to clipboard!")
        else:
            messagebox.showwarning("No Content", "There is no content to copy.")
    except Exception as e:
        messagebox.showerror("Clipboard Error", f"An error occurred while copying: {e}")

# Main GUI function
def run_gui():
    def on_scrape_button_click():
        url = url_entry.get().strip()
        tags = tags_entry.get().strip().split(',')

        if url and tags:
            extracted_data = scrape_website(url, tags)
            if extracted_data:
                display_scraped_data(extracted_data)
                global data_scraped
                data_scraped = extracted_data  # Store the scraped data globally
            else:
                data_scraped = None  # Reset data_scraped if no data is found
        else:
            messagebox.showwarning("Input Error", "Please provide both URL and tags.")

    def display_scraped_data(data):
        result_text.delete(1.0, "end")  # Clear the previous text

        # Display the data in the Text widget
        for idx, (tag, text_list) in enumerate(data.items(), 1):
            result_text.insert("end", f"Link {idx}:\n")
            for text in text_list:
                result_text.insert("end", f"- {text}\n")
            result_text.insert("end", "\n")

    def save_as_csv():
        if data_scraped is None:
            messagebox.showwarning("No Data", "No data to save.")
            return
        
        # Ask the user where to save the CSV file
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if file_path:
            save_data_to_csv(data_scraped, file_path)

    def save_as_pdf():
        if data_scraped is None:
            messagebox.showwarning("No Data", "No data to save.")
            return
        
        # Ask the user where to save the PDF file
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            save_data_to_pdf(data_scraped, file_path)

    def exit_app():
        root.destroy()

    global data_scraped  # Global variable to store extracted data
    data_scraped = None  # Initialize to None

    # Create the main window
    root = ctk.CTk()
    root.title("GUI Web Scraper")
    root.geometry("900x700")

    # URL Input Section
    url_frame = ctk.CTkFrame(root)
    url_frame.pack(pady=20)

    url_label = ctk.CTkLabel(url_frame, text="Enter URL:")
    url_label.grid(row=0, column=0, padx=10)

    url_entry = ctk.CTkEntry(url_frame, placeholder_text="https://example.com", width=500)
    url_entry.grid(row=0, column=1, padx=10)

    # Tags Input Section
    tags_frame = ctk.CTkFrame(root)
    tags_frame.pack(pady=10)

    tags_label = ctk.CTkLabel(tags_frame, text="Enter Tags (comma separated):")
    tags_label.grid(row=0, column=0, padx=10)

    tags_entry = ctk.CTkEntry(tags_frame, placeholder_text="h1, p, h2", width=500)
    tags_entry.grid(row=0, column=1, padx=10)

    # Scrape Button
    scrape_button = ctk.CTkButton(root, text="Scrape Website", command=on_scrape_button_click)
    scrape_button.pack(pady=20)

    # Display Scraped Data
    result_text = ctk.CTkTextbox(root, width=850, height=400, corner_radius=10)
    result_text.pack(pady=20)

    # Buttons for Saving, Copying, and Exiting at the Bottom
    button_frame = ctk.CTkFrame(root, fg_color="transparent")
    button_frame.pack(pady=10)

    save_csv_button = ctk.CTkButton(button_frame, text="Save as CSV", command=save_as_csv, width=150)
    save_csv_button.grid(row=0, column=0, padx=10)

    save_pdf_button = ctk.CTkButton(button_frame, text="Save as PDF", command=save_as_pdf, width=150)
    save_pdf_button.grid(row=0, column=1, padx=10)

    copy_button = ctk.CTkButton(button_frame, text="Copy to Clipboard", command=lambda: copy_to_clipboard(result_text), width=150)
    copy_button.grid(row=0, column=2, padx=10)

    exit_button = ctk.CTkButton(button_frame, text="Exit", command=exit_app, width=150)
    exit_button.grid(row=0, column=3, padx=10)

    # Start the GUI main loop
    root.mainloop()

if __name__ == "__main__":
    run_gui()
