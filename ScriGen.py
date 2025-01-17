import gradio as gr
from youtube_transcript_api import YouTubeTranscriptApi
import re

def extract_video_id(url):
    """
    استخراج معرف الفيديو من روابط YouTube المختلفة.
    """
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

def get_transcript(url):
    """
    استخراج نصوص الفيديو باستخدام مكتبة YouTubeTranscriptApi.
    """
    video_id = extract_video_id(url)
    if not video_id:
        return "Invalid YouTube URL", ""
    
    try:
        # المحاولة أولاً باللغة الإنجليزية
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        formatted_transcript = "\n".join([entry['text'] for entry in transcript])
        return "Transcript successfully extracted (English)!", formatted_transcript
    except:
        try:
            # المحاولة باللغة العربية إذا لم تتوفر النصوص الإنجليزية
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ar'])
            formatted_transcript = "\n".join([entry['text'] for entry in transcript])
            return "Transcript successfully extracted (Arabic)!", formatted_transcript
        except Exception as e:
            return "Error", str(e)

# إعداد واجهة Gradio
interface = gr.Interface(
    fn=get_transcript,
    inputs=gr.Textbox(label="Enter YouTube video URL"),
    outputs=[
        gr.Textbox(label="Status"),
        gr.Textbox(label="Transcript", lines=10, placeholder="Transcript will appear here...")
    ],
    title="YouTube Transcript Extractor",
    description="Extract transcripts from YouTube videos by entering their URL. Supports English and Arabic."
)

if __name__ == "__main__":
    # تشغيل التطبيق
    interface.launch(share=True)
