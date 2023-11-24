import requests
import re
from tqdm import tqdm
import json
import os
import shutil


class DownloadYoutubeResource:
    def __init__(self, url):
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

    def getEnglishCaption(self):
        path = 'F:/store/resource/media/caption/'
        for item in self.captions:
            vss_id = item.get('vssId')
            if vss_id.startswith('.en'):
                url = item.get('baseUrl').encode('utf-8').decode(
                    'utf-8') + ('&fmt=json3&xorb=2&xobt=3&xovt=3&cbr=Chrome&cbrver=119.0.0.0&c=WEB&cver=2.20231117.01'
                                '.04&cplayer=UNIPLAYER&cos=Windows&cosver=10.0&cplatform=DESKTOP')

                text = requests.get(url).text
                events = json.loads(text)['events']
                for event in events:
                    captions = event.get('segs')[0].get('utf8')
                    with open(f'{path}{self.title}.txt', 'a', encoding='utf-8') as file:
                        file.write(captions + '\n\n')

                print('英语字幕下载成功！')
                return

        print('暂无字幕！')
        return

    def getImage(self):
        response = requests.get(url=self.image_url, headers=self.headers)
        if response.status_code == 200:
            path = 'F:/store/resource/media/image/'
            with open(f'{path}{self.title}.jpg', 'wb') as file:
                file.write(response.content)
            print(f"封面下载成功！ {self.title}")
        else:
            print(f"封面下载失败: {response.status_code}")

    def getBestVideoAudioByContentLength(self, res):
        result = float('inf')
        for item in res:
            content_length = int(item.get('contentLength'))
            if content_length < result:
                result = content_length

        for item in res:
            content_length = int(item.get('contentLength'))
            if content_length == result:
                url = item.get('url')
                return url

    def setQualityList(self):
        quality_list = []
        url_list = []
        if self.video_1080p:
            quality_list.append('1080p')
            url = self.getBestVideoAudioByContentLength(self.video_1080p)
            url_list.append(url)
        if self.video_720p:
            quality_list.append('720p')
            url = self.getBestVideoAudioByContentLength(self.video_720p)
            url_list.append(url)
        if self.video_480p:
            quality_list.append('480p')
            url = self.getBestVideoAudioByContentLength(self.video_480p)
            url_list.append(url)
        if self.video_360p:
            quality_list.append('360p')
            url = self.getBestVideoAudioByContentLength(self.video_360p)
            url_list.append(url)
        if self.video_240p:
            quality_list.append('240p')
            url = self.getBestVideoAudioByContentLength(self.video_240p)
            url_list.append(url)
        if self.video_144p:
            quality_list.append('144p')
            url = self.getBestVideoAudioByContentLength(self.video_144p)
            url_list.append(url)

            url = self.getBestVideoAudioByContentLength(self.audio_medium)
            url_list.append(url)

            url = self.getBestVideoAudioByContentLength(self.audio_low)
            url_list.append(url)

        return quality_list, url_list

    def setVideoAudioByQuality(self):
        for item in self.video_audio_dict:
            mime_type = item.get('mimeType')
            if mime_type.startswith('video'):
                quality_label = item.get('qualityLabel')
                if quality_label.startswith('1080p'):
                    self.video_1080p.append(item)
                elif quality_label.startswith('720p'):
                    self.video_720p.append(item)
                elif quality_label.startswith('480p'):
                    self.video_480p.append(item)
                elif quality_label.startswith('360p'):
                    self.video_360p.append(item)
                elif quality_label.startswith('240p'):
                    self.video_240p.append(item)
                elif quality_label.startswith('144p'):
                    self.video_144p.append(item)
            elif mime_type.startswith('audio'):
                audio_quality = item.get('audioQuality')
                if audio_quality.startswith('AUDIO_QUALITY_MEDIUM'):
                    self.audio_medium.append(item)
                elif audio_quality.startswith('AUDIO_QUALITY_LOW'):
                    self.audio_low.append(item)

        quality_list, url_list = self.setQualityList()
        return quality_list, url_list

    def getVideoOrAudio(self, url, suffix):
        name = ''
        if suffix == '.mp4':
            name = 'video'
        elif suffix == '.mp3':
            name = 'audio'
        audio = requests.get(url, stream=True)
        file_size = int(audio.headers.get('Content-Length'))
        progress = tqdm(total=file_size)
        with open(f'{name}{suffix}', mode='ab') as f:
            for audio_chunk in audio.iter_content():
                f.write(audio_chunk)
                if suffix == '.mp4':
                    progress.set_description('正在下载视频中...')
                elif suffix == '.mp3':
                    progress.set_description('正在下载音频中...')
                progress.update()
            if suffix == '.mp4':
                progress.set_description("视频下载完成！")
            elif suffix == '.mp3':
                progress.set_description("音频下载完成！")
            progress.close()

    def processFile(self):
        ffmpeg = 'ffmpeg -i ' + 'video.mp4 -i ' + 'audio.mp3 ' + 'name.mp4'
        os.system(ffmpeg)

        old_name = 'name.mp4'
        new_name = f'{self.title}.mp4'
        os.rename(old_name, new_name)
        path = "F:/store/resource/media/video/"
        shutil.move(new_name, path)

        os.remove('video.mp4')
        os.remove('audio.mp3')


def ui():
    video_suffix = '.mp4'
    audio_suffix = '.mp3'
    print('Welcome to YouTubeHunter v1.0')
    # https://www.youtube.com/watch?v=2b7GY4BSUmU&list=PLsIk0qF0R1j4Y2QxGw33vYu3t70CAPV7X
    url = input('请输入下载地址: ')
    resource = DownloadYoutubeResource(url)
    print('请选择需要下载的内容(回车默认最高清晰度完整下载)')
    mode = input('1: 完整下载 2: 选择下载: \n')
    quality_list, url_list = resource.setVideoAudioByQuality()
    if mode == '':
        video_url = url_list[0]
        resource.getVideoOrAudio(video_url, video_suffix)
        audio_url = url_list[-2]
        resource.getVideoOrAudio(audio_url, audio_suffix)
        resource.processFile()
        resource.getEnglishCaption()
        resource.getImage()
    elif mode == '1':
        print('请选择清晰度')
        index = 1
        for quality in quality_list:
            print(f'{index}: {quality}', end='  ')
            index += 1
        print()
        quality = int(input())
        if -1 < quality < len(url_list):
            video_url = url_list[quality - 1]
            resource.getVideoOrAudio(video_url, video_suffix)
            if quality_list[quality - 1] in ['1080p', '720p', '480p']:
                audio_url = url_list[-2]
                resource.getVideoOrAudio(audio_url, audio_suffix)
            elif quality_list[quality - 1] in ['360p', '240p', '144p']:
                audio_url = url_list[-1]
                resource.getVideoOrAudio(audio_url, audio_suffix)

            resource.processFile()
            resource.getEnglishCaption()
            resource.getImage()
    elif mode == '2':
        print('请选择需要下载的内容')
        num = input('1: 视频  2: 音频  3: 字幕  4: 封面  5: 处理视频')
        print()
        if num == '1':
            print('请选择视频清晰度')
            index = 1
            for quality in quality_list:
                print(f'{index}: {quality}', end='  ')
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
