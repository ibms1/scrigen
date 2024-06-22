import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

# Set the title of the application
st.title('YouTube Transcript Extractor')

# Input field for YouTube video URL
url = st.text_input('Enter YouTube video URL')

# List of available languages
available_languages = []

# Button to start extracting the transcript
if st.button('Start Extracting'):
    if url:
        try:
            # Display a loading message
            with st.spinner('Extracting transcript...'):
                # Extract video ID from the URL
                video_id = url.replace('https://www.youtube.com/watch?v=', '')

                # Get available transcripts
                transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
                
                # Get the available languages
                available_languages = [t.language_code for t in transcripts]

                # Get transcript in the selected language
                selected_language = st.selectbox('Select Transcript Language', available_languages, index=available_languages.index('en') if 'en' in available_languages else 0)
                
                transcript = transcripts.find_transcript([selected_language]).fetch()

                # Format the extracted transcript
                formatter = TextFormatter()
                output = formatter.format_transcript(transcript)

                # Display the formatted transcript
                st.text_area('Extracted Transcript', output, height=300)
        except Exception as e:
            st.error(f"Please Enter a Valid YouTube Video Link")


# CSS مخصص لإخفاء الروابط عند تمرير الفأرة
hide_links_style = """
    <style>
    a {
        text-decoration: none;
        color: inherit;
        pointer-events: none;
    }
    a:hover {
        text-decoration: none;
        color: inherit;
        cursor: default;
    }
    </style>
    """
st.markdown(hide_links_style, unsafe_allow_html=True)