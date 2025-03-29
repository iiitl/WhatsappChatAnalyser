import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns
import io
import csv

st.sidebar.title("Hello ...!")

# Function to reset session state
def reset_app():
    st.session_state.clear()  # Clear all session state variables

# Sidebar for file upload using a key to store it in session state
uploaded_file = st.sidebar.file_uploader("Choose a file", key="uploaded_file")

# Reset button to clear uploaded file, selection, and data
if st.sidebar.button("Reset App"):
    reset_app()
    st.rerun()  # Force Streamlit to refresh the app

if uploaded_file is not None:
    if uploaded_file.size == 0:
        st.error("The uploaded file is empty. Please upload a valid WhatsApp chat export.")
        st.stop()
    else:
        try:
            # Read file as bytes and decode to string
            bytes_data = uploaded_file.read()
            data = bytes_data.decode("utf-8")
            df = preprocessor.preprocess(data)
            st.session_state.dataframe = df  # Store dataframe in session state
        except UnicodeDecodeError as e:
            st.error(f"Decode Error: {e}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    
    # Build user list from the dataframe
    user_list = df['Sender'].unique().tolist()
    user_list.sort()
    user_list.insert(0, "Overall")
    
    # Store selected user in session state if not already set
    if "selected_user" not in st.session_state:
        st.session_state.selected_user = "Overall"
    selected_user = st.sidebar.selectbox("Show analysis for", user_list, key="selected_user")
    
    # (Optionally) Pre-fetch stats before showing analysis
    helper.fetch_stats(selected_user, df)
    
    if st.sidebar.button("Show analysis"):
        # -------------------------
        # Display Basic Stats
        # -------------------------
        st.title("Top Stats")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.header("Total Messages")
            num_messages = helper.fetch_stats(selected_user, df)
            st.title(num_messages)
        
        with col2:
            st.header("Total Words")
            num_words = helper.fetch_words(selected_user, df)
            st.title(num_words)
        
        with col3:
            st.header("Total Emojis")
            num_emojis, emojis = helper.fetch_emojis(selected_user, df)
            st.title(num_emojis)
            st.text("Frequently used")
            emoji_html = " ".join([f"<span>{emoji}</span>" for emoji in emojis])
            st.markdown(f"<p style='font-size: 30px;'>{emoji_html}</p>", unsafe_allow_html=True)
        
        with col4:
            st.header("Total Media")
            media = helper.media_shared(selected_user, df)
            st.title(media)
        
        with col5:
            st.header("Total Links")
            urls = helper.links_shared(selected_user, df)
            st.title(urls)
        
        # Display the most busiest user (only applicable for overall/group chats)
        if selected_user == "Overall":
            st.header("Most Busy Users")
            x, percent_data = helper.most_busy_user(df)
            names = x.index.tolist()
            counts = x.values.tolist()
            
            col1, col2 = st.columns(2)
            with col1:
                fig, ax = plt.subplots()
                sns.barplot(x=names, y=counts, ax=ax, color='orange')
                plt.xticks(rotation=90)
                for i, count in enumerate(counts):
                    ax.text(i, count + 0.05, str(count), ha='center', va='bottom')
                ax.set_xlabel('Sender')
                ax.set_ylabel('Message Count')
                ax.set_title('Top Senders')
                st.pyplot(fig)
            
            with col2:
                st.header("Percentage of messages per user")
                st.table(percent_data)
        
        # Display the wordcloud
        st.title("Wordcloud")
        fig, ax = plt.subplots()
        wc_img = helper.create_wordcloud(selected_user, df)
        ax.imshow(wc_img)
        st.pyplot(fig)
        
        # Display the most frequent words
        st.title("Most Frequent words")
        freq_words = helper.most_freq_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(freq_words['Word'], freq_words['count'])
        plt.xticks(rotation=90)
        st.pyplot(fig)
        
        # Display the timeline of messages
        st.title("Monthly Timeline of Messages")
        monthly_timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(monthly_timeline['time'], monthly_timeline['Message'], marker='o', color='r', linestyle='-', linewidth=2, markersize=6)
        plt.xticks(rotation='vertical')
        plt.xlabel("Time")
        plt.ylabel("Number of messages")
        st.pyplot(fig)
        
        st.title("Daily Timeline of Messages")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.plot(daily_timeline['Date'], daily_timeline['Message'], color='b', linestyle='-')
        plt.xticks(rotation='vertical')
        plt.xlabel("Time")
        plt.ylabel("Number of messages")
        st.pyplot(fig)
         
        #Display the Activity Map 
        st.title("Activity Map")
        col1, col2 = st.columns(2)
        with col1:
            st.header("Most Active Days")
            active_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            sns.barplot(x=active_day.index, y=active_day.values, ax=ax, color='purple')
            plt.xticks(rotation=90)
            st.pyplot(fig)
        
        with col2:
            st.header("Most Active Month")
            active_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            sns.barplot(x=active_month.index, y=active_month.values, ax=ax, color='green')
            plt.xticks(rotation=90)
            st.pyplot(fig)
        
        #Display the Heatmap
        st.title("Activity Heatmap")
        fig, ax = plt.subplots(figsize=(18, 10))
        heatmap_data = helper.activity_heatmap(selected_user, df)
        ax = sns.heatmap(heatmap_data.pivot_table(index='Day_name', columns='Interval', values='Message', aggfunc='count').fillna(0), ax=ax)
        st.pyplot(fig)
        
        # -------------------------
        # GENERATE CSV REPORT
        # -------------------------
        
        # Create a list to hold CSV rows
        report_rows = []
        
        # Section: Basic Stats
        report_rows.append(["Basic Stats"])
        report_rows.append(["Total Messages", num_messages])
        report_rows.append(["Total Words", num_words])
        report_rows.append(["Total Emojis", num_emojis])
        report_rows.append(["Frequently Used Emojis", ", ".join(emojis)])
        report_rows.append(["Total Media", media])
        report_rows.append(["Total Links", urls])
        
        # Section: Most Busy Users (only if overall)
        if selected_user == "Overall":
            report_rows.append([])
            report_rows.append(["Most Busy Users"])
            report_rows.append(["Sender", "Message Count"])
            for name, count in zip(names, counts):
                report_rows.append([name, count])
            
        # Check and format the percentage column if it exists
        if not percent_data.empty:
            report_rows.append([])
            report_rows.append(["Percentage of Messages per User"])
            
            # Reset index to get sender names in a column
            percent_df = percent_data.reset_index()
            
            # Format the percentage column if it exists (assuming the column is named 'Percentage')
            if 'Percentage' in percent_df.columns:
                percent_df['Percentage'] = percent_df['Percentage'].apply(lambda x: f"{x:.2%}")
            
            # Add header row (based on DataFrame columns)
            report_rows.append(list(percent_df.columns))
            
            # Append each row's data
            for _, row in percent_df.iterrows():
                report_rows.append(list(row))

        
        # Section: Most Frequent Words
        report_rows.append([])
        report_rows.append(["Most Frequent Words"])
        report_rows.append(["Word", "Count"])
        for _, row in freq_words.iterrows():
            report_rows.append([row['Word'], row['count']])
        
        # Section: Monthly Timeline
        report_rows.append([])
        report_rows.append(["Monthly Timeline"])
        report_rows.append(["Time", "Number of Messages"])
        for _, row in monthly_timeline.iterrows():
            report_rows.append([row['time'], row['Message']])
        
        # Section: Daily Timeline
        report_rows.append([])
        report_rows.append(["Daily Timeline"])
        report_rows.append(["Date", "Number of Messages"])
        for _, row in daily_timeline.iterrows():
            report_rows.append([row['Date'], row['Message']])
        
        # Section: Activity Map - Most Active Days
        report_rows.append([])
        report_rows.append(["Most Active Days"])
        report_rows.append(["Day", "Message Count"])
        for day, count in active_day.items():
            report_rows.append([day, count])
        
        # Section: Activity Map - Most Active Month
        report_rows.append([])
        report_rows.append(["Most Active Month"])
        report_rows.append(["Month", "Message Count"])
        for month, count in active_month.items():
            report_rows.append([month, count])
        
        # Write the report rows into an in-memory CSV file
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerows(report_rows)
        csv_bytes = csv_buffer.getvalue().encode("utf-8")

        csv_bytes = csv_buffer.getvalue().encode("utf-8-sig")
        
        # Download button for the CSV file
        st.sidebar.download_button(
            label="Download Report as CSV",
            data=csv_bytes,
            file_name="whatsapp_detailed_report.csv",
            mime="text/csv",
            on_click="ignore"
        )
