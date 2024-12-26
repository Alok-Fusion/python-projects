from tkinter import messagebox  # Importing messagebox for displaying notifications and warnings
import customtkinter as ctk  # Importing customtkinter for a modern, styled GUI

# Function to create and manage the to-do list
def todo_list():
    # Function to add a task to the task list
    def add_task():
        task = task_entry.get()  # Get the task name from the task entry field
        description = description_entry.get("1.0", "end").strip()  # Get the description from the description text box
        if task.strip() and description.strip():  # Check if task and description are not empty
            tasks.append((task, description))  # Add the task and description as a tuple to the task list
            update_task_list()  # Update the task list display
            task_entry.delete(0, "end")  # Clear the task entry field
            description_entry.delete("1.0", "end")  # Clear the description text box
            messagebox.showinfo("Task Added", "Task added successfully!")  # Show a success message
        else:
            # Show a warning if the task or description is empty
            messagebox.showwarning("Warning", "Task and description cannot be empty!")

    # Function to update the task list display
    def update_task_list():
        for widget in task_list_frame.winfo_children():  # Iterate through all child widgets in the task list frame
            widget.destroy()  # Remove each widget to refresh the frame

        for i, (task, description) in enumerate(tasks, 1):  # Loop through the tasks with their index
            # Create a frame for each task
            task_frame = ctk.CTkFrame(task_list_frame, fg_color="#2E3B4E", corner_radius=10)
            task_frame.pack(pady=5, fill="x", padx=10)  # Add padding and stretch horizontally

            # Display the task title
            task_label = ctk.CTkLabel(task_frame, text=f"{i}. {task}", font=("Helvetica", 16, "bold"))
            task_label.pack(anchor="w", padx=10, pady=5)  # Align the label to the left with padding

            # Display the task description below the title
            description_label = ctk.CTkLabel(task_frame, text=description, font=("Helvetica", 12), wraplength=600, fg_color="transparent")
            description_label.pack(anchor="w", padx=20, pady=5)  # Align the description to the left with more padding

    # Function to remove the last task in the list
    def remove_task():
        try:
            selected_task_index = len(tasks) - 1  # Get the index of the last task
            tasks.pop(selected_task_index)  # Remove the last task from the list
            update_task_list()  # Update the task list display
            messagebox.showinfo("Task Removed", "Task removed successfully!")  # Show a success message
        except IndexError:
            # Show a warning if there are no tasks to remove
            messagebox.showwarning("Warning", "Please select a task to remove!")

    # Function to exit the application
    def exit_app():
        root.destroy()  # Close the main application window

    tasks = []  # Initialize an empty list to store tasks

    # Configure the main application window
    ctk.set_appearance_mode("dark")  # Set the appearance mode to dark
    ctk.set_default_color_theme("blue")  # Set the color theme to blue
    root = ctk.CTk()  # Create the main window
    root.title("Python Made To-Do List")  # Set the window title
    root.geometry("800x600")  # Set the window size
    root.resizable(False, False)  # Disable resizing of the window

    # Header section
    header_label = ctk.CTkLabel(root, text="Your Professional To-Do List", font=("Helvetica", 24, "bold"), fg_color="transparent")
    header_label.pack(pady=20)  # Add the header label with padding

    # Input section for tasks
    input_frame = ctk.CTkFrame(root, fg_color="transparent")  # Create a transparent frame for input
    input_frame.pack(pady=10)  # Add padding to the input frame

    task_entry = ctk.CTkEntry(input_frame, placeholder_text="Task Name", width=300, height=40)  # Create an entry field for task name
    task_entry.grid(row=0, column=0, padx=10)  # Position the entry field in the grid

    add_button = ctk.CTkButton(input_frame, text="Add Task", command=add_task, width=100)  # Create a button to add tasks
    add_button.grid(row=0, column=1, padx=10)  # Position the button next to the entry field

    # Textbox for task description
    description_entry = ctk.CTkTextbox(root, height=100, width=700, corner_radius=10, font=("Helvetica", 12))  # Create a text box for task description
    description_entry.pack(pady=10)  # Add padding to the description box

    # Scrollable frame for task list
    task_list_frame = ctk.CTkScrollableFrame(root, width=750, height=300, fg_color="#1E293B", corner_radius=15)  # Create a scrollable frame for tasks
    task_list_frame.pack(pady=20)  # Add padding to the task list frame

    # Buttons for additional actions
    button_frame = ctk.CTkFrame(root, fg_color="transparent")  # Create a transparent frame for buttons
    button_frame.pack(pady=10)  # Add padding to the button frame

    remove_button = ctk.CTkButton(button_frame, text="Remove Last Task", command=remove_task, width=150, fg_color="#FF5C5C", hover_color="#FF7878")  # Button to remove the last task
    remove_button.grid(row=0, column=0, padx=10)  # Position the button in the grid

    exit_button = ctk.CTkButton(button_frame, text="Exit", command=exit_app, width=150, fg_color="#1F6AA5", hover_color="#3B82F6")  # Button to exit the application
    exit_button.grid(row=0, column=1, padx=10)  # Position the button next to the remove button

    root.mainloop()  # Run the main application loop

todo_list()  # Call the function to run the to-do list application
