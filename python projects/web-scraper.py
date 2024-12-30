import csv
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
import pyperclip
import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Developer: Alok Kushwaha
# Description: A modern web scraper application with a responsive GUI.

# Function to scrape website data
def scrape_website(url, tags):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise error for unsuccessful status codes
        soup = BeautifulSoup(response.content, "html.parser")
        extracted_data = {tag: [element.get_text(strip=True) for element in soup.find_all(tag)] for tag in tags}
        if not extracted_data:
            messagebox.showwarning("No Data", "No data found for the provided tags!")
        return extracted_data
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error fetching the page: {e}")
        return None

# Function to save data to a CSV file
def save_data_to_csv(data, filename):
    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Tag", "Extracted Text"])
            for tag, texts in data.items():
                for text in texts:
                    writer.writerow([tag, text])
        messagebox.showinfo("Success", f"Data saved to {filename}")
    except Exception as e:
        messagebox.showerror("Error", f"Error saving data to CSV: {e}")

# Function to save data to a PDF file
def save_data_to_pdf(data, filename):
    try:
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        c.setFont("Helvetica-Bold", 16)
        c.drawString(30, height - 40, "Scraped Data")
        y_position = height - 60
        for tag, texts in data.items():
            c.setFont("Helvetica", 12)
            c.drawString(30, y_position, f"{tag}:")
            y_position -= 20
            for text in texts:
                c.drawString(50, y_position, f"- {text}")
                y_position -= 15
            y_position -= 10
        c.save()
        messagebox.showinfo("Success", f"Data saved to {filename}")
    except Exception as e:
        messagebox.showerror("Error", f"Error saving data to PDF: {e}")

# Function to copy data to clipboard
def copy_to_clipboard(content_widget):
    content = content_widget.get("1.0", "end-1c").strip()
    if content:
        pyperclip.copy(content)
        messagebox.showinfo("Success", "Content copied to clipboard!")
    else:
        messagebox.showwarning("No Content", "There is no content to copy.")

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
                data_scraped = extracted_data
            else:
                data_scraped = None
        else:
            messagebox.showwarning("Input Error", "Please provide both URL and tags.")

    def display_scraped_data(data):
        result_text.delete("1.0", "end")
        for idx, (tag, texts) in enumerate(data.items(), 1):
            result_text.insert("end", f"Tag {idx} ({tag}):\n")
            for text in texts:
                result_text.insert("end", f"  • {text}\n")
            result_text.insert("end", "\n")

    def save_as_csv():
        if data_scraped is None:
            messagebox.showwarning("No Data", "No data to save.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if file_path:
            save_data_to_csv(data_scraped, file_path)

    def save_as_pdf():
        if data_scraped is None:
            messagebox.showwarning("No Data", "No data to save.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if file_path:
            save_data_to_pdf(data_scraped, file_path)

    def exit_app():
        root.destroy()

    global data_scraped
    data_scraped = None

    # Main Window
    root = ctk.CTk()
    root.title("Responsive Web Scraper")
    
    # Adjusting screen size for better visibility
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"{int(screen_width * 0.8)}x{int(screen_height * 0.85)}")  # Increased height to 85%
    root.configure(fg_color="#2E2E2E")

    # Scrollable Frame
    canvas = tk.Canvas(root, bg="#2E2E2E", highlightthickness=0)
    scrollbar = ctk.CTkScrollbar(root, orientation="vertical", command=canvas.yview)
    scrollable_frame = ctk.CTkFrame(canvas, fg_color="#2E2E2E")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Title Section
    title_label = ctk.CTkLabel(scrollable_frame, text="Web Scraper", font=("Roboto", 24, "bold"), text_color="#FF6F61")
    title_label.pack(pady=10)
    developer_label = ctk.CTkLabel(scrollable_frame, text="Developed by Alok Kushwaha", font=("Roboto", 14), text_color="#BBBBBB")
    developer_label.pack(pady=5)

    # URL Input Section
    url_frame = ctk.CTkFrame(scrollable_frame, corner_radius=10, fg_color="#393E46")
    url_frame.pack(pady=10, padx=20, fill="x")
    url_label = ctk.CTkLabel(url_frame, text="Enter URL:", font=("Roboto", 16), text_color="#EEEEEE")
    url_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
    url_entry = ctk.CTkEntry(url_frame, placeholder_text="https://example.com", width=int(screen_width * 0.5), corner_radius=8)
    url_entry.grid(row=0, column=1, padx=10, pady=10)

    # Tags Input Section
    tags_frame = ctk.CTkFrame(scrollable_frame, corner_radius=10, fg_color="#393E46")
    tags_frame.pack(pady=10, padx=20, fill="x")
    tags_label = ctk.CTkLabel(tags_frame, text="Enter Tags:", font=("Roboto", 16), text_color="#EEEEEE")
    tags_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
    tags_entry = ctk.CTkEntry(tags_frame, placeholder_text="h1, p, div", width=int(screen_width * 0.5), corner_radius=8)
    tags_entry.grid(row=0, column=1, padx=10, pady=10)

    # Scrape Button
    scrape_button = ctk.CTkButton(scrollable_frame, text="Scrape Website", command=on_scrape_button_click, width=int(screen_width * 0.2), corner_radius=10)
    scrape_button.pack(pady=20)

    # Display Scraped Data
    result_text = ctk.CTkTextbox(scrollable_frame, width=int(screen_width * 0.75), height=int(screen_height * 0.4), corner_radius=10, fg_color="#1B1B1B", text_color="#FFFFFF")
    result_text.pack(pady=20)

    # Buttons Section
    button_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
    button_frame.pack(pady=10)
    save_csv_button = ctk.CTkButton(button_frame, text="Save as CSV", command=save_as_csv, width=int(screen_width * 0.1), corner_radius=10)
    save_csv_button.grid(row=0, column=0, padx=10)
    save_pdf_button = ctk.CTkButton(button_frame, text="Save as PDF", command=save_as_pdf, width=int(screen_width * 0.1), corner_radius=10)
    save_pdf_button.grid(row=0, column=1, padx=10)
    copy_button = ctk.CTkButton(button_frame, text="Copy to Clipboard", command=lambda: copy_to_clipboard(result_text), width=int(screen_width * 0.1), corner_radius=10)
    copy_button.grid(row=0, column=2, padx=10)
    exit_button = ctk.CTkButton(button_frame, text="Exit", command=exit_app, width=int(screen_width * 0.1), corner_radius=10)
    exit_button.grid(row=0, column=3, padx=10)

    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    run_gui()
