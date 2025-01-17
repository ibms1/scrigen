import streamlit as st
import json
import re
import urllib.request
import urllib.parse

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

def get_transcript(video_id):
    """الحصول على النص باستخدام innertube API"""
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req)
        html = response.read().decode('utf-8')
        
        # استخراج بيانات التكوين
        client_config = re.search(r'"INNERTUBE_CLIENT_VERSION":"([\d\.]+)"', html)
        api_key = re.search(r'"INNERTUBE_API_KEY":"([^"]+)"', html)
        
        if not client_config or not api_key:
            return None, "Could not extract required configuration"
        
        client_version = client_config.group(1)
        api_key = api_key.group(1)
        
        # بناء طلب الحصول على النصوص
        transcript_url = f"https://www.youtube.com/youtubei/v1/get_transcript?key={api_key}"
        
        data = {
            "context": {
                "client": {
                    "clientName": "WEB",
                    "clientVersion": client_version,
                },
            },
            "videoId": video_id
        }
        
        data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(transcript_url, data=data, headers={
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        response = urllib.request.urlopen(req)
        transcript_data = json.loads(response.read().decode('utf-8'))
        
        # استخراج النصوص المتاحة
        if 'actions' in transcript_data:
            transcripts = transcript_data['actions'][0]['updateEngagementPanelAction']['content']['transcriptRenderer']['body']['transcriptBodyRenderer']['cueGroups']
            
            formatted_transcript = []
            for cue in transcripts:
                text = cue['transcriptCueGroupRenderer']['cues'][0]['transcriptCueRenderer']['cue']['simpleText']
                formatted_transcript.append(text)
            
            return '\n'.join(formatted_transcript), None
            
        return None, "No transcripts available"
        
    except urllib.error.HTTPError as e:
        return None, f"HTTP Error: {str(e)}"
    except Exception as e:
        return None, f"Error: {str(e)}"

# حقل إدخال رابط فيديو YouTube
url = st.text_input('Enter YouTube video URL')

if url:
    video_id = extract_video_id(url)
    
    if not video_id:
        st.error("Please enter a valid YouTube URL")
    else:
        if st.button('Extract Transcript'):
            with st.spinner('Extracting transcript...'):
                transcript, error = get_transcript(video_id)
                
                if transcript:
                    # عرض النص
                    st.text_area('Extracted Transcript', transcript, height=300)
                    
                    # زر التحميل
                    st.download_button(
                        label="Download Transcript",
                        data=transcript,
                        file_name=f"transcript_{video_id}.txt",
                        mime="text/plain"
                    )
                else:
                    st.error(error)