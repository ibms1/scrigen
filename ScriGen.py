import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import httpx
import re
import json
from urllib.parse import urlparse, parse_qs

# إخفاء العناصر غير المرغوب فيها
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            .stDeployButton {display:none;}
            #stStreamlitLogo {display: none;}
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
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# عنوان التطبيق
st.title('YouTube Transcript Extractor')

def extract_video_id(url):
    """استخراج معرف الفيديو من روابط YouTube المختلفة"""
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&\s]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^\s]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^\s]+)',
        r'([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_transcript_alternative(video_id):
    """محاولة الحصول على النص باستخدام طريقة بديلة"""
    try:
        # استخدام httpx للحصول على بيانات الفيديو
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        with httpx.Client(headers=headers, timeout=30.0) as client:
            # محاولة الحصول على معلومات الفيديو
            response = client.get(f'https://www.youtube.com/watch?v={video_id}')
            response.raise_for_status()
            
            # البحث عن بيانات النص في صفحة الفيديو
            data_match = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});', response.text)
            if data_match:
                data = json.loads(data_match.group(1))
                captions_data = data.get('captions', {}).get('playerCaptionsTracklistRenderer', {})
                
                if captions_data:
                    return True
            
            return False
    except Exception as e:
        st.error(f"Alternative method failed: {str(e)}")
        return False

# حقل إدخال رابط فيديو YouTube
url = st.text_input('Enter YouTube video URL')

# زر لبدء استخراج النص
if st.button('Start Extracting'):
    if not url:
        st.error("Please enter a YouTube video URL")
    else:
        try:
            # عرض رسالة التحميل
            with st.spinner('Extracting transcript...'):
                # استخراج معرف الفيديو
                video_id = extract_video_id(url)
                
                if not video_id:
                    st.error("Invalid YouTube URL format. Please check the URL and try again.")
                else:
                    try:
                        # محاولة الحصول على النصوص باستخدام الطريقة الأساسية
                        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
                        
                        # الحصول على اللغات المتاحة
                        available_languages = [(t.language_code, t.language) for t in transcripts]
                        language_options = {f"{lang[1]} ({lang[0]})": lang[0] for lang in available_languages}
                        
                        # اختيار اللغة
                        selected_language_display = st.selectbox(
                            'Select Transcript Language',
                            options=list(language_options.keys()),
                            index=0
                        )
                        
                        # الحصول على رمز اللغة المحدد
                        selected_language_code = language_options[selected_language_display]
                        
                        # جلب النص
                        transcript = transcripts.find_transcript([selected_language_code]).fetch()
                        
                        # تنسيق النص المستخرج
                        formatter = TextFormatter()
                        output = formatter.format_transcript(transcript)
                        
                        # عرض النص المنسق
                        st.text_area('Extracted Transcript', output, height=300)
                        
                        # إضافة زر للتحميل
                        st.download_button(
                            label="Download Transcript",
                            data=output,
                            file_name=f"transcript_{video_id}.txt",
                            mime="text/plain"
                        )
                        
                    except Exception as e:
                        error_message = str(e)
                        if "Subtitles are disabled for this video" in error_message:
                            # محاولة الطريقة البديلة
                            if get_transcript_alternative(video_id):
                                st.warning("""
                                Transcripts exist for this video but cannot be accessed directly. 
                                This might be due to:
                                1. Region restrictions
                                2. Age restrictions
                                3. Private video settings
                                
                                Try accessing the video directly on YouTube while signed in.
                                """)
                            else:
                                st.error("This video doesn't have any subtitles/transcripts available.")
                        else:
                            st.error(f"Error accessing transcript: {error_message}")
                            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")