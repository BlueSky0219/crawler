import requests
import re
import json
import os
from yt_dlp import YoutubeDL
import webvtt


class DownloadYoutubeResource:
    def __init__(self, url):
        self.url = url
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/119.0.0.0 Safari/537.36'
        }

        url_id = url.split('?')[1].split('=')[1].split('&')[0]
        self.image_url = f'https://i.ytimg.com/vi/{url_id}/hqdefault.jpg'

        print("正在解析中...")

        html_data = requests.get(url=url, headers=self.headers).text
        json_str = re.findall('var ytInitialPlayerResponse = (.*?);var', html_data)[0]
        json_dict = json.loads(json_str)
        title = json_dict['videoDetails']['title']

        self.captions = json_dict['captions']['playerCaptionsTracklistRenderer']['captionTracks']

        ffmpeg_title = re.sub('[/:*?"<>|\\n]', '', title)
        ffmpeg_title = ffmpeg_title.replace(' ', '')

        self.video_audio_dict = json_dict['streamingData']['adaptiveFormats']
        # self.json_dict = json_dict
        self.title = title
        self.ffmpeg_title = ffmpeg_title

    def getImage(self):
        output_path = 'E:/store/resource/media/videos/'
        ydl_opts = {'outtmpl': output_path + '/%(title)s',
                    'format': 'best',
                    'writethumbnail': True,
                    'skip_download': True}

        with YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(self.url, download=True)

    def extract_subtitles(self, name):
        path = 'E:/store/resource/media/videos/' + name
        subtitles = []
        try:
            captions = webvtt.read(path)
            for caption in captions:
                subtitles.append(caption.text.strip())
        except Exception as e:
            print(f"Error reading subtitles: {e}")

        return subtitles

    def check_subtitles(self, language='en', mode=1):
        # mode为1检查外挂字幕
        sub = 'subtitles'
        # mode为2检查自动生成字幕
        if mode == 2:
            sub = 'automatic_captions'

        ydl_opts = {
            'listsubtitles': True,
            'skip_download': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(self.url, download=False)
            subtitles = info_dict.get(sub, {})

            if language in subtitles:
                return True
            else:
                return False

    def download_subtitles(self, language='en', mode=1):
        output_path = 'E:/store/resource/media/videos/'
        # mode为1下载外挂字幕
        sub_flag = True
        sub_autp_flag = False
        # mode为2下载自动生成字幕
        if mode == 2:
            sub_flag = False
            sub_autp_flag = True

        ydl_opts = {
            'outtmpl': output_path + '/%(title)s',
            'writesubtitles': sub_flag,
            'writeautomaticsub': sub_autp_flag,
            'subtitleslangs': [language],
            'skip_download': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])

    def download_best(self):
        output_path = 'E:/store/resource/media/videos/'
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': f'{output_path}/%(title)s.mp4',
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])

    def getQualityList(self):
        options = {
            'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/bestvideo[height<=720]+bestaudio/best[height<=720]/bestvideo[height<=360]+bestaudio/best[height<=360]/bestvideo[height<=240]+bestaudio/best[height<=240]/bestvideo[height<=144]+bestaudio/best[height<=144]',
        }
        with YoutubeDL(options) as ydl:
            info_dict = ydl.extract_info(self.url, download=False)
            formats = info_dict.get('formats', [])
            target_formats = []
            for fmt in formats:
                resolution = fmt.get('height')
                if resolution == 1080:
                    target_formats.append(resolution)
                elif resolution == 720:
                    target_formats.append(resolution)
                elif resolution == 480:
                    target_formats.append(resolution)
                elif resolution == 360:
                    target_formats.append(resolution)
                elif resolution == 240:
                    target_formats.append(resolution)
                elif resolution == 144:
                    target_formats.append(resolution)

            return sorted(set(target_formats), reverse=True)

    def download_video(self, quality='best'):
        output_path = 'E:/store/resource/media/videos/'
        options = {
            'format': f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]',
            'outtmpl': f'{output_path}/%(title)s.mp4',
        }

        with YoutubeDL(options) as ydl:
            ydl.download([self.url])


def ui():
    video_suffix = '.mp4'
    audio_suffix = '.mp3'
    print('Welcome to YouTubeSky v1.0')
    # https://www.youtube.com/watch?v=2b7GY4BSUmU
    # url = input('请输入下载地址: ')
    url = 'https://www.youtube.com/watch?v=sVPLeZ_Vpw8'
    resource = DownloadYoutubeResource(url)
    print('请选择需要下载的内容(回车默认最高清晰度完整下载)')
    mode = input('1: 完整下载 2: 选择下载: \n')
    if mode == '':
        resource.download_best()
        resource.getEnglishCaption()
        resource.getImage()
    elif mode == '1':
        # index = 1
        # quality_list = resource.getQualityList()
        # print('请选择清晰度')
        # for quality in quality_list:
        #     print(f'{index}: {quality}p', end='  ')
        #     index += 1
        # print()
        # quality = int(input())
        # if -1 < quality <= len(quality_list):
        #     print('下载视频中...')
        #     resource.download_video(quality_list[quality - 1])
        # else:
        #     print('输入错误，请重新运行！')
        #     return
        #
        # print('下载中英文字幕中...')
        # if resource.check_subtitles('en', 1):
        #     resource.download_subtitles('en', 1)
        # elif resource.check_subtitles('en', 2):
        #     resource.download_subtitles('en', 2)
        # if resource.check_subtitles('zh-Hans', 1):
        #     resource.download_subtitles('zh-Hans', 1)
        # elif resource.check_subtitles('zh-Hans', 2):
        #     resource.download_subtitles('zh-Hans', 2)

        print(resource.extract_subtitles('1.vtt'))

        # print('下载封面中...')
        # resource.getImage()
    elif mode == '2':
        print('请选择需要下载的内容')
        num = input('1: 视频  2: 字幕  3: 封面')
        print()
        if num == '1':
            print('请选择视频清晰度')
            index = 1
            for quality in quality_list:
                print(f'{index}: {quality}p', end='  ')
                index += 1
            print()
            quality = int(input())
            if -1 < quality < len(url_list):
                video_url = url_list[quality - 1]
                resource.getVideoOrAudio(video_url, video_suffix)
        elif num == '2':
            print('请选择音频质量')
            quality = input('1: 高质量  2: 低质量')
            if quality == '1':
                audio_url = url_list[-2]
                resource.getVideoOrAudio(audio_url, audio_suffix)
            elif quality == '2':
                audio_url = url_list[-1]
                resource.getVideoOrAudio(audio_url, audio_suffix)
        elif num == '3':
            resource.getEnglishCaption()
        elif num == '4':
            resource.getImage()
        elif num == '5':
            resource.processFile()

    else:
        print('输入错误！')


if __name__ == '__main__':
    ui()

    # 下载封面 yt-dlp --write-thumbnail url
    # 下载视频 yt-dlp url
    # 下载字幕 yt-dlp --write-auto-subs --sub-format best --sub-lang en --skip-download url
    # yt-dlp -o "/your/output/path/%(title)s.%(ext)s" "https://www.youtube.com/watch?v=your_video_id"
