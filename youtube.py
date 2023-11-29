import os
from yt_dlp import YoutubeDL


class DownloadYoutubeResource:
    def __init__(self, url):
        self.url = url
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/119.0.0.0 Safari/537.36'
        }

        self.title = self.get_video_title()
        url_id = url.split('?')[1].split('=')[1].split('&')[0]
        self.image_url = f'https://i.ytimg.com/vi/{url_id}/hqdefault.jpg'

        print("正在解析中...")

    def get_video_title(self):
        ydl = YoutubeDL({'quiet': True})

        with ydl:
            result = ydl.extract_info(self.url, download=False)
            title = result.get('title', 'Title not available')
            return title

    def getImage(self):
        output_path = 'F:/store/resource/media/images/'
        ydl_opts = {'outtmpl': output_path + '/%(title)s',
                    'format': 'best',
                    'writethumbnail': True,
                    'skip_download': True}

        with YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(self.url, download=True)

    def processSubtitles(self, mode=1):
        suffer = 'en'
        if mode == 2:
            suffer = 'zh-Hans'
        output_path = 'f:/store/resource/media/subtitles/'
        vtt_to_srt = f'ffmpeg -i {output_path}temp.{suffer}.vtt {output_path}temp.{suffer}.srt'
        os.system(vtt_to_srt)
        old_name = f'{output_path}temp.{suffer}.srt'
        new_name = f'{output_path}{self.title}.{suffer}.srt'
        os.rename(old_name, new_name)
        os.remove(f'{output_path}temp.{suffer}.vtt')

    def getSubtitles(self):
        if self.check_subtitles('en', 1):
            self.download_subtitles('en', 1)
        elif self.check_subtitles('en', 2):
            self.download_subtitles('en', 2)
        if self.check_subtitles('zh-Hans', 1):
            self.download_subtitles('zh-Hans', 1)
        elif self.check_subtitles('zh-Hans', 2):
            self.download_subtitles('zh-Hans', 2)

        self.processSubtitles(1)
        self.processSubtitles(2)

    def check_subtitles(self, language='en', mode=1):
        # mode为1检查外挂字幕
        sub = 'subtitles'
        # mode为2检查自动生成字幕
        if mode == 2:
            sub = 'automatic_captions'

        ydl_opts = {
            'skip_download': True,
            'quiet': True,
            'convertSubs': 'srt',
        }

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(self.url, download=False)
            subtitles = info_dict.get(sub, {})

            if language in subtitles:
                return True
            else:
                return False

    def download_subtitles(self, language='en', mode=1):
        output_path = 'F:/store/resource/media/subtitles/'
        # mode为1下载外挂字幕
        sub_flag = True
        sub_autp_flag = False
        # mode为2下载自动生成字幕
        if mode == 2:
            sub_flag = False
            sub_autp_flag = True

        ydl_opts = {
            'outtmpl': output_path + '/temp',
            'writesubtitles': sub_flag,
            'writeautomaticsub': sub_autp_flag,
            'subtitleslangs': [language],
            'skip_download': True,
            'quiet': True,
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

    def processFile(self):
        output_path = 'f:/store/resource/media/videos/'
        webm_to_mp4 = f'ffmpeg -i {output_path}temp.webm {output_path}temp.mp4'
        os.system(webm_to_mp4)
        old_name = f'{output_path}temp.mp4'
        new_name = f'{output_path}{self.title}.mp4'
        os.rename(old_name, new_name)
        os.remove(f'{output_path}temp.webm')

    def download_video(self, quality='best'):
        output_path = 'f:/store/resource/media/videos/'
        yt_format = f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/bestvideo[ext=mp4]+bestaudio/best[ext=m4a]/best[ext=webm]'
        if quality == 'best':
            yt_format = 'bestvideo+bestaudio/best[ext=mp4]+bestaudio/best[ext=m4a]/best[ext=webm]'
        options = {
            'format': yt_format,
            'outtmpl': f'{output_path}/temp.%(ext)s',
        }

        with YoutubeDL(options) as ydl:
            ydl.download([self.url])

        print('视频格式转换中...')
        self.processFile()


def ui():
    print('Welcome to YouTubeSky v1.0')
    # https://www.youtube.com/watch?v=2b7GY4BSUmU
    url = input('请输入下载地址: ')
    # url = 'https://www.youtube.com/watch?v=sVPLeZ_Vpw8'
    resource = DownloadYoutubeResource(url)
    print('请选择需要下载的内容(回车默认最高清晰度完整下载)')
    mode = input('1: 完整下载 2: 选择下载: \n')
    if mode == '':
        print('下载视频中...')
        resource.download_video('best')
        print('下载中英文字幕中...')
        resource.getSubtitles()
        resource.getImage()
    elif mode == '1':
        index = 1
        quality_list = resource.getQualityList()
        print('请选择清晰度')
        for quality in quality_list:
            print(f'{index}: {quality}p', end='  ')
            index += 1
        print()
        quality = int(input())
        if -1 < quality <= len(quality_list):
            print('下载视频中...')
            resource.download_video(quality_list[quality - 1])
        else:
            print('输入错误，请重新运行！')
            return
        print('下载中英文字幕中...')
        resource.getSubtitles()
        print('下载封面中...')
        resource.getImage()
    elif mode == '2':
        print('请选择需要下载的内容')
        num = input('1: 视频  2: 字幕  3: 封面')
        print()
        if num == '1':
            index = 1
            quality_list = resource.getQualityList()
            print('请选择清晰度')
            for quality in quality_list:
                print(f'{index}: {quality}p', end='  ')
                index += 1
            print()
            quality = int(input())
            if -1 < quality <= len(quality_list):
                print('下载视频中...')
                resource.download_video(quality_list[quality - 1])
            else:
                print('输入错误，请重新运行！')
                return
        elif num == '2':
            print('下载中英文字幕中...')
            resource.getSubtitles()
        elif num == '3':
            print('下载封面中...')
            resource.getImage()
    else:
        print('输入错误，请重新运行！')
        return


if __name__ == '__main__':
    ui()
