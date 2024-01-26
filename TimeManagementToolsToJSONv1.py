import streamlit as st
from datetime import datetime, time

# Initialize session state for storing tasks if not already present
if 'tasks' not in st.session_state:
    st.session_state['tasks'] = []


# Function to create a time input for hours and minutes
def time_input(label):
    col1, col2 = st.columns(2)
    with col1:
        hours = st.number_input(f"{label} - Hours", min_value=0, max_value=23, format="%d")
    with col2:
        minutes = st.number_input(f"{label} - Minutes", min_value=0, max_value=59, format="%d")
    return time(hours, minutes)


# Function to add a task
def add_task():
    with st.form(key='task_form'):
        task = st.text_input("Task Name")
        priority = st.selectbox("Priority",
                                ["Critical", "Important", "Emerging", "Moderate", "Undefined", "No Priority"])

        # Updated time inputs using the time_input function
        start_time = time_input("Start Time")
        end_time = time_input("End Time")
        work_time = time_input("Work Time")
        research_time = time_input("Research Time")
        roadblock_time = time_input("Time Spent Addressing Roadblocks")

        tools = st.text_area("Tools")
        resources = st.text_area("Resources")
        people = st.text_area("People Involved")
        additional_tasks = st.text_area("Additional Tasks")
        research_sources = st.text_area("Research Sources")
        roadblocks = st.text_area("Roadblocks")
        research_completed = st.text_area("Research Activities Completed")
        research_needed = st.text_area("Research Activities Needed")
        accomplishments = st.text_area("Accomplishments Related To This Task")
        error_recognition_events = st.text_area("Recursive Error Recognition Events")
        expenses = st.text_area("Itemized Expenses (Enter each expense on a new line)")
        submit_button = st.form_submit_button(label='Add Task')

        if submit_button:
            current_date = datetime.now().strftime("%Y-%m-%d")
            new_task = {
                "date": current_date,
                "task": task,
                "priority": priority,
                "start_time": str(start_time),
                "end_time": str(end_time),
                "work_time": str(work_time),
                "research_time": str(research_time),
                "roadblock_time": str(roadblock_time),
                "tools": tools,
                "resources": resources,
                "people": people,
                "additional_tasks": additional_tasks,
                "research_sources": research_sources,
                "roadblocks": roadblocks,
                "research_completed": research_completed,
                "research_needed": research_needed,
                "accomplishments": accomplishments,
                "error_recognition_events": error_recognition_events,
                "expenses": expenses.split('\n')  # Split expenses by newline
            }
            st.session_state['tasks'].append(new_task)
            st.success('Task Added Successfully!')


def view_tasks():
    if st.session_state['tasks']:
        for idx, task in enumerate(st.session_state['tasks']):
            st.subheader(f"Task {idx + 1}")
            st.json(task)
    else:
        st.write("No tasks added yet")


def main():
    st.title("Time Management App")

    st.sidebar.title("Navigation")
    menu = st.sidebar.radio("Menu", ["Add Task", "View Tasks"])

    if menu == "Add Task":
        add_task()
    elif menu == "View Tasks":
        view_tasks()


if __name__ == "__main__":
    main()
