import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
import plotly.express as px
import plotly.graph_objects as go
import json
from io import BytesIO
import base64

# Set page configuration
st.set_page_config(page_title="Time Management Dashboard", layout="wide")

# Initialize session states
if 'tasks' not in st.session_state:
    st.session_state['tasks'] = []
if 'current_task' not in st.session_state:
    st.session_state['current_task'] = None

# Custom CSS
st.markdown("""
    <style>
    .stButton button {
        width: 100%;
        margin-bottom: 10px;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .metrics-container {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
    }
    </style>
""", unsafe_allow_html=True)

def time_input(label, key_prefix):
    """Enhanced time input with validation"""
    col1, col2 = st.columns(2)
    with col1:
        hours = st.number_input(f"{label} - Hours", 
                              min_value=0, 
                              max_value=23, 
                              format="%d",
                              key=f"{key_prefix}_hours")
    with col2:
        minutes = st.number_input(f"{label} - Minutes", 
                                min_value=0, 
                                max_value=59, 
                                format="%d",
                                key=f"{key_prefix}_minutes")
    return time(hours, minutes)

def calculate_duration(start_time, end_time):
    """Calculate duration between two time objects"""
    start_dt = datetime.combine(datetime.today(), start_time)
    end_dt = datetime.combine(datetime.today(), end_time)
    if end_dt < start_dt:
        end_dt += timedelta(days=1)
    return (end_dt - start_dt).total_seconds() / 3600  # Returns hours

def generate_download_link(df, filename, text):
    """Generate a download link for dataframe"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def add_task():
    """Enhanced task addition form with validation and auto-calculation"""
    with st.form(key='task_form', clear_on_submit=True):
        st.subheader("Task Details")
        col1, col2 = st.columns(2)
        
        with col1:
            task = st.text_input("Task Name", key="task_name")
            priority = st.select_slider("Priority",
                                     options=["Critical", "Important", "Emerging", 
                                             "Moderate", "Undefined", "No Priority"],
                                     value="Moderate")
            start_time = time_input("Start Time", "start")
            end_time = time_input("End Time", "end")
            
        with col2:
            work_time = time_input("Work Time", "work")
            research_time = time_input("Research Time", "research")
            roadblock_time = time_input("Roadblock Time", "roadblock")

        # Expandable sections for detailed information
        with st.expander("Resources and Tools"):
            tools = st.text_area("Tools Used")
            resources = st.text_area("Resources Utilized")
            people = st.text_area("People Involved")

        with st.expander("Research Details"):
            col3, col4 = st.columns(2)
            with col3:
                research_sources = st.text_area("Research Sources")
                research_completed = st.text_area("Completed Research Activities")
            with col4:
                research_needed = st.text_area("Needed Research Activities")
                roadblocks = st.text_area("Encountered Roadblocks")

        with st.expander("Task Progress and Outcomes"):
            accomplishments = st.text_area("Accomplishments")
            error_recognition = st.text_area("Error Recognition Events")
            additional_tasks = st.text_area("Additional Tasks Identified")

        with st.expander("Expenses"):
            expenses = st.text_area("Itemized Expenses (One per line)")

        submit_button = st.form_submit_button(label='Save Task')
        
        if submit_button:
            if not task:
                st.error("Task name is required!")
                return

            # Calculate total duration
            total_duration = calculate_duration(start_time, end_time)
            
            new_task = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "task": task,
                "priority": priority,
                "start_time": str(start_time),
                "end_time": str(end_time),
                "duration_hours": round(total_duration, 2),
                "work_time": str(work_time),
                "research_time": str(research_time),
                "roadblock_time": str(roadblock_time),
                "tools": tools,
                "resources": resources,
                "people": people,
                "research_sources": research_sources,
                "roadblocks": roadblocks,
                "research_completed": research_completed,
                "research_needed": research_needed,
                "accomplishments": accomplishments,
                "error_recognition_events": error_recognition,
                "additional_tasks": additional_tasks,
                "expenses": [exp.strip() for exp in expenses.split('\n') if exp.strip()]
            }
            
            st.session_state['tasks'].append(new_task)
            st.success('Task successfully added!')

def view_tasks():
    """Enhanced task viewing with filtering and sorting"""
    if not st.session_state['tasks']:
        st.info("No tasks recorded yet. Start by adding a task!")
        return

    # Convert tasks to DataFrame for easier manipulation
    df = pd.DataFrame(st.session_state['tasks'])
    
    # Filtering options
    col1, col2, col3 = st.columns(3)
    with col1:
        date_filter = st.date_input("Filter by date", 
                                   value=datetime.now().date(),
                                   key="date_filter")
    with col2:
        priority_filter = st.multiselect("Filter by priority",
                                       options=df['priority'].unique(),
                                       default=df['priority'].unique())
    with col3:
        sort_by = st.selectbox("Sort by",
                              options=['date', 'priority', 'duration_hours'],
                              index=0)

    # Apply filters
    filtered_df = df[
        (df['date'] == date_filter.strftime("%Y-%m-%d")) &
        (df['priority'].isin(priority_filter))
    ].sort_values(by=sort_by)

    # Display tasks
    for idx, task in filtered_df.iterrows():
        with st.expander(f"📋 {task['task']} ({task['priority']})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("⏰ Time Information")
                st.write(f"Start: {task['start_time']}")
                st.write(f"End: {task['end_time']}")
                st.write(f"Duration: {task['duration_hours']} hours")
                
                st.write("👥 People Involved")
                st.write(task['people'])
                
            with col2:
                st.write("🔧 Tools & Resources")
                st.write(task['tools'])
                st.write(task['resources'])
            
            if task['roadblocks']:
                st.warning(f"🚧 Roadblocks: {task['roadblocks']}")
            
            if task['accomplishments']:
                st.success(f"✅ Accomplishments: {task['accomplishments']}")

def analyze_tasks():
    """Task analysis and visualization dashboard"""
    if not st.session_state['tasks']:
        st.info("No data available for analysis. Start by adding some tasks!")
        return

    df = pd.DataFrame(st.session_state['tasks'])
    
    # Time analysis
    st.subheader("📊 Time Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Priority distribution
        fig_priority = px.pie(df, 
                            names='priority', 
                            title='Task Distribution by Priority')
        st.plotly_chart(fig_priority)
        
    with col2:
        # Time spent per day
        daily_hours = df.groupby('date')['duration_hours'].sum().reset_index()
        fig_daily = px.bar(daily_hours, 
                          x='date', 
                          y='duration_hours',
                          title='Daily Time Spent (Hours)')
        st.plotly_chart(fig_daily)

    # Task completion trends
    st.subheader("📈 Task Completion Trends")
    df['date'] = pd.to_datetime(df['date'])
    tasks_per_day = df.groupby('date').size().reset_index(name='count')
    fig_trend = px.line(tasks_per_day, 
                       x='date', 
                       y='count',
                       title='Tasks Completed Over Time')
    st.plotly_chart(fig_trend)

    # Export options
    st.subheader("📤 Export Data")
    if st.button("Download Task Data as CSV"):
        csv = df.to_csv(index=False).encode()
        b64 = base64.b64encode(csv).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="task_data.csv">Download CSV File</a>'
        st.markdown(href, unsafe_allow_html=True)

def main():
    st.title("⏰ Advanced Time Management Dashboard")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select Page", 
                           ["Add Task", "View Tasks", "Analytics"])
    
    # Display current date and time
    st.sidebar.write(f"Current Date: {datetime.now().strftime('%Y-%m-%d')}")
    st.sidebar.write(f"Current Time: {datetime.now().strftime('%H:%M')}")
    
    # Page routing
    if page == "Add Task":
        add_task()
    elif page == "View Tasks":
        view_tasks()
    else:
        analyze_tasks()

if __name__ == "__main__":
    main()
