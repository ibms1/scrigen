import streamlit as st
import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

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

# حقل إدخال رابط فيديو YouTube
url = st.text_input('Enter YouTube video URL')

# ملاحظة بالإنجليزية لتوضيح أنه يجب تشغيل الفيديو
st.markdown("""
    **Note:** The video must be played first in order to extract the transcript.
    The transcript will not be available unless the video is playing.
""")

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

# زر لبدء استخراج النص
if st.button('Start Extracting'):
    if not url:
        st.error("Please enter a YouTube video URL")
    else:
        try:
            # استخراج معرف الفيديو
            video_id = extract_video_id(url)
            
            if not video_id:
                st.error("Invalid YouTube URL format. Please check the URL and try again.")
            else:
                # تضمين الفيديو باستخدام iframe مع التشغيل التلقائي
                video_url = f"https://www.youtube.com/embed/{video_id}?autoplay=1"
                st.markdown(f'<iframe width="560" height="315" src="{video_url}" frameborder="0" allowfullscreen></iframe>', unsafe_allow_html=True)
                
                try:
                    # استخراج النصوص المتاحة
                    transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
                    
                    # الحصول على اللغات المتاحة
                    available_languages = [(t.language_code, t.language) for t in transcripts]
                    
                    # تحويل القائمة إلى قاموس للعرض بشكل أفضل
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
                    if "Subtitles are disabled for this video" in str(e):
                        st.error("This video doesn't have any subtitles/transcripts available.")
                    else:
                        st.error(f"Error accessing transcript: {str(e)}")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
