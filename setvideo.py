

from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import VideoFileClip
from moviepy.video.VideoClip import TextClip
from tqdm import tqdm
#from moviepy.video.tools.drawing import color_to_rgb
import subprocess
import os

def quote(path):
    return f'"{path}"'

def compress_video2(input_file, output_file, start_time=None, end_time=None, bitrate="1500k"):
    duration = end_time - start_time if start_time is not None and end_time is not None else None

    input_file_quoted = quote(input_file)
    output_file_quoted = quote(output_file)

    cmd = ["ffmpeg", "-y"]

    if start_time is not None:
        cmd += ["-ss", str(start_time)]

    cmd += ["-i", input_file_quoted]

    if duration is not None:
        cmd += ["-t", str(duration)]

    cmd += [
        "-an",
        "-c:v", "libx264",
        "-preset", "fast",
        "-b:v", f"{bitrate}k" if "k" not in bitrate else bitrate,
        "-movflags", "+faststart",
        output_file_quoted
    ]

    # 문자열로 만들어서 shell=True 로 실행
    command_str = " ".join(cmd)
    print("실행 명령어:", command_str)
    subprocess.run(command_str, shell=True, check=True)

def escape_drawtext_text(text):
    # ffmpeg drawtext용 특수문자 escape
    return text.replace("\\", "\\\\").replace(":", r'\:').replace("'", r"\'").replace(",", r"\,").replace(" ", r'\ ')

def compress_video2_with_text(input_file, output_file, start_time=None, end_time=None, bitrate="1500k", text=""):
    duration = end_time - start_time if start_time is not None and end_time is not None else None

    input_file_quoted = quote(input_file)
    output_file_quoted = quote(output_file)

    # 텍스트 오버레이 필터 구성
    drawtext_filter = ""
    if text:
        escaped_text = escape_drawtext_text(text)
        drawtext_filter = (
            f"drawtext=fontfile=/Windows/Fonts/arial.ttf:"
            f"text='{escaped_text}':"
            f"fontcolor=red:fontsize=60:borderw=1:x=(w-text_w)/2:y=h-line_h-10"
        )

    cmd = ["ffmpeg", "-y"]

    if start_time is not None:
        cmd += ["-ss", str(start_time)]

    cmd += ["-i", input_file_quoted]

    if duration is not None:
        cmd += ["-t", str(duration)]

    cmd += [
        "-r", "30",
        "-an",
        "-c:v", "libx264",
        "-preset", "fast",
        "-b:v", f"{bitrate}k" if "k" not in bitrate else bitrate,
    ]

    if text:
        cmd += ["-vf", f'"{drawtext_filter}"']  # 전체 filter string을 따옴표로 감쌈

    cmd += ["-movflags", "+faststart", output_file_quoted]

    print("실행 명령어:", " ".join(cmd))
    subprocess.run(" ".join(cmd), shell=True, check=True)

def compress_video3_with_segments(
    input_file,
    output_file,
    overlays=[],
    start_time=None,
    end_time=None,
    bitrate="1500k",
    style_str=""
):
    duration = end_time - start_time if start_time is not None and end_time is not None else None

    def quote(path):
        return f'"{path}"'

    input_file_quoted = quote(input_file)
    output_file_quoted = quote(output_file)

    # 🔧 drawtext 조합
    vf_filters = []
    for overlay in overlays:
        escaped_text = escape_drawtext_text(overlay['text'])
        start = overlay['start']
        end = overlay['end']
        
        # drawtext: 반드시 text= 와 enable= 가 먼저, style은 뒤에 붙이기
        drawtext = (
            f"drawtext=text='{escaped_text}':"
            f"enable='between(t,{start},{end})':"
            f"{style_str}"
        )
        vf_filters.append(drawtext)

    filter_str = ",".join(vf_filters) if vf_filters else "null"

    # ffmpeg 명령어 구성
    cmd = ["ffmpeg", "-y"]
    if start_time is not None:
        cmd += ["-ss", str(start_time)]
    cmd += ["-i", input_file_quoted]
    if duration is not None:
        cmd += ["-t", str(duration)]

    cmd += [
        "-r", "30",
        "-an",
        "-c:v", "libx264",
        "-preset", "fast",
        "-b:v", f"{bitrate}k" if "k" not in bitrate else bitrate,
        "-vf", f'"{filter_str}"',
        "-movflags", "+faststart",
        output_file_quoted
    ]

    print("실행 명령어:", " ".join(cmd))
    subprocess.run(" ".join(cmd), shell=True, check=True)

def compress_video2_with_segments(input_file, output_file, overlays=[], start_time=None, end_time=None, bitrate="1500k", style_str = ""):
    duration = end_time - start_time if start_time is not None and end_time is not None else None

    input_file_quoted = quote(input_file)
    output_file_quoted = quote(output_file)

    # drawtext 필터들 조합
    vf_filters = []
    for overlay in overlays:
        text = escape_drawtext_text(overlay['text'])
        start = overlay['start']
        end = overlay['end']
        vf = (
            f"drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':"
            f"text='{text}':"
            f"enable='between(t,{start},{end})':"
            f"fontcolor=yellow:"
            f"fontsize=70:"
            f"borderw=2:"
            f"bordercolor=black:"
            f"x=(w-text_w)/2:"
            f"y=h-line_h-10"
        )

        vf_filters.append(vf)

    filter_str = ",".join(vf_filters) if vf_filters else "null"

    cmd = ["ffmpeg", "-y"]
    if start_time is not None:
        cmd += ["-ss", str(start_time)]
    cmd += ["-i", input_file_quoted]
    if duration is not None:
        cmd += ["-t", str(duration)]

    cmd += [
        "-r", "30",
        "-an",
        "-c:v", "libx264",
        "-preset", "fast",
        "-b:v", f"{bitrate}k" if "k" not in bitrate else bitrate,
        "-vf", f'"{filter_str}"',
        "-movflags", "+faststart",
        output_file_quoted
    ]

    print("실행 명령어:", " ".join(cmd))
    subprocess.run(" ".join(cmd), shell=True, check=True)

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
