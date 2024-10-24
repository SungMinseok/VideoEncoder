

from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import VideoFileClip
from moviepy.video.VideoClip import TextClip
from tqdm import tqdm
#from moviepy.video.tools.drawing import color_to_rgb

def compress_video(input_file, output_file, start_time=None, end_time=None, bitrate="1500k"):
    """
    Compresses a video file while minimizing quality loss.
    :param input_file: The path to the input video file.
    :param output_file: The path to the output video file.
    :param start_time: The start time of the segment to be extracted (in seconds). Optional.
    :param end_time: The end time of the segment to be extracted (in seconds). Optional.
    :param bitrate: The target bitrate of the output video (in kbps). Default is 1500k.
    """
    # Load the video clip
    video_clip = VideoFileClip(input_file)
    video_clip = video_clip.without_audio()

    if end_time == None :
        duration = video_clip.duration
    else : 
        duration = end_time

    # Extract the specified segment if start_time and end_time are provided
    if start_time is not None and end_time is not None:
        video_clip = video_clip.subclip(start_time, duration)

    # Compress the video
    video_clip.write_videofile(output_file, bitrate=bitrate)

def get_videoinfo(input_file):
    class VideoInfo():
        def __init__(self) :
            self.name = ""
            self.duration = ""

    
    video_info = VideoInfo()
    video_clip = VideoFileClip(input_file)
    
    video_info.duration = video_clip.duration

    return video_info

import cv2

def add_text_to_video(video_path, tag, output_path):
    # 비디오 파일 열기
    print("시작")
    cap = cv2.VideoCapture(video_path)
    
    # 비디오 속성 가져오기
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    
    # 출력 비디오 설정
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, fps, frame_size)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # 태그 텍스트 추가
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        font_color = (255, 255, 255)  # 흰색
        tag_position = (20, 40)  # 좌측 상단 위치
        cv2.putText(frame, tag, tag_position, font, font_scale, font_color, 2, cv2.LINE_AA)
        
        # 수정된 프레임을 출력 비디오에 쓰기
        out.write(frame)
        
        # 'q' 키로 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # 자원 해제
    cap.release()
    out.release()
    cv2.destroyAllWindows()

    print("끝")

# # 사용 예시
# video_path = '입력_비디오_파일.mp4'
# tag = 'rev.33043'
# output_path = '출력_비디오_파일.mp4'
# add_text_to_video(video_path, tag, output_path)

import cv2

def add_text_to_video(input_video_path, output_video_path, text):
    # Open the video file
    cap = cv2.VideoCapture(input_video_path)
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    
    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, frame_size)
    
    while tqdm(cap.isOpened()):
        ret, frame = cap.read()
        if not ret:
            break
        
        # Add text to the frame
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        font_color = (255, 255, 255)  # White color
        text_position = (50, 50)  # Position of the text
        cv2.putText(frame, text, text_position, font, font_scale, font_color, 2, cv2.LINE_AA)
        
        # Write the modified frame to the output video
        out.write(frame)
        
        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release resources
    cap.release()
    out.release()
    cv2.destroyAllWindows()

# # Usage example
# input_video_path = 'A.mp4'
# output_video_path = 'B.mp4'
# text_to_add = 'Your Text Here'
# add_text_to_video(input_video_path, output_video_path, text_to_add)
