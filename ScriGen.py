import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.formatters import TextFormatter
import re

# إخفاء العناصر غير المرغوب فيها
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .stDeployButton {display:none;}
            #stStreamlitLogo {display: none;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# عنوان التطبيق
st.title('YouTube Transcript Extractor')

def extract_video_id(url):
    """استخراج معرف الفيديو من روابط YouTube المختلفة"""
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&\s]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^\s]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^\s]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_available_transcripts(video_id):
    """الحصول على النصوص المتاحة مع معالجة الأخطاء المحسنة"""
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        languages = []
        for transcript in transcript_list:
            languages.append({
                'code': transcript.language_code,
                'name': transcript.language
            })
        return languages, None
    except TranscriptsDisabled:
        return None, "Transcripts are disabled for this video."
    except NoTranscriptFound:
        return None, "No transcripts were found for this video."
    except Exception as e:
        return None, f"Error accessing transcripts: {str(e)}"

# حقل إدخال رابط فيديو YouTube
url = st.text_input('Enter YouTube video URL')

if url:
    video_id = extract_video_id(url)
    
    if not video_id:
        st.error("Please enter a valid YouTube URL")
    else:
        try:
            # محاولة الحصول على النصوص المتاحة
            languages, error = get_available_transcripts(video_id)
            
            if languages:
                # إنشاء قائمة اللغات للاختيار
                language_options = {
                    f"{lang['name']} ({lang['code']})": lang['code']
                    for lang in languages
                }
                
                selected_language_display = st.selectbox(
                    'Select Transcript Language',
                    options=list(language_options.keys())
                )
                
                if st.button('Extract Transcript'):
                    try:
                        with st.spinner('Extracting transcript...'):
                            selected_language_code = language_options[selected_language_display]
                            
                            # محاولة الحصول على النص
                            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[selected_language_code])
                            
                            # تنسيق النص
                            formatter = TextFormatter()
                            formatted_transcript = formatter.format_transcript(transcript)
                            
                            # عرض النص
                            st.text_area('Extracted Transcript', formatted_transcript, height=300)
                            
                            # زر التحميل
                            st.download_button(
                                label="Download Transcript",
                                data=formatted_transcript,
                                file_name=f"transcript_{video_id}.txt",
                                mime="text/plain"
                            )
                    except Exception as e:
                        st.error(f"Error extracting transcript: {str(e)}")
            else:
                st.error(error)
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")