import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import seaborn as sns

st.sidebar.title("Hello...!")

# File uploader widget
uploaded_file = st.sidebar.file_uploader("Choose a file")

# Reset button to clear everything and restart the app
if st.sidebar.button("Reset App"):
    st.session_state.clear()  # Clears all session state variables
    st.experimental_rerun()  # Refreshes the app

if uploaded_file is not None:
    try:
        # Read file as bytes
        bytes_data = uploaded_file.read()
        # Decode bytes to string
        data = bytes_data.decode("utf-8")
        df = preprocessor.preprocess(data)
    except UnicodeDecodeError as e:
        st.error(f"Decode Error: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

    user_list = df['Sender'].unique().tolist()
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis for", user_list)

    if st.sidebar.button("Show analysis"):
        # Display the stats
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
            
            # Show emojis in a better way on the page
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
        
        # Most busy user in group chat
        if selected_user == "Overall":
            st.header("Most busiest user")
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
        
        # Wordcloud
        st.title("Wordcloud")
        fig, ax = plt.subplots()
        wc_img = helper.create_wordcloud(selected_user, df)
        ax.imshow(wc_img)
        st.pyplot(fig)
        
        # Most frequent words
        st.title("Most frequent words")
        freq_words = helper.most_freq_words(selected_user, df)
        fig,
