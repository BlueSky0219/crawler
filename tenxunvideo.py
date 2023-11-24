import json
import re

import pprint
from bs4 import BeautifulSoup
from tqdm import tqdm
import requests

cookies = {
    'RK': 'Kn+Ewr8NOG',
    'ptcz': '9519100e6351065648f3e3cef5f183528942c6f1e099bb4b5e3f9737a8717e31',
    '_qpsvr_localtk': '0.4004973382367907',
    'uin': 'o1255067427',
    'skey': '@asReY9jds',
    'pac_uid': '1_1255067427',
    'iip': '0',
    '_qimei_uuid42': '17b0b110a251001b6af9019cceea51d81db376b7b3',
    '_qimei_fingerprint': 'd618505bcea63dd91fa3ee781a735809',
    '_qimei_q36': '',
    '_qimei_h38': 'fded401c6af9019cceea51d802000000b17b0b',
    'o_minduid': 'AGQdiUR3hXJ3ECTRcxYgz230SLCUuKpv',
    'appuser': 'BCF0966839C989C1',
    'qq_domain_video_guid_verify': '5020b578e44ca9c5',
    'pgv_info': 'ssid=s4207741584',
    'pgv_pvid': '390148540',
    'o_cookie': '1255067427',
    'vversion_name': '8.2.95',
    'video_omgid': '5020b578e44ca9c5',
    'ad_session_id': 'w3mckrfydvbtc',
    'LPPBturn': '464',
    'full_screen_cid_pause_times': '9',
    'full_screen_pause_times': '9',
    'LPDFturn': '666',
    'LZCturn': '694',
    'LPSJturn': '553',
    'LBSturn': '795',
    'LVINturn': '301',
    'LPHLSturn': '758',
    'LZTturn': '451',
    'Lturn': '424',
    'LKBturn': '860',
    'LPVLturn': '311',
    'LPLFturn': '337',
    'LDERturn': '395',
}

headers = {
    'authority': 'vd6.l.qq.com',
    'accept': '*/*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'content-type': 'text/plain;charset=UTF-8',
    # Requests sorts cookies= alphabetically
    # 'cookie': 'RK=Kn+Ewr8NOG; ptcz=9519100e6351065648f3e3cef5f183528942c6f1e099bb4b5e3f9737a8717e31; _qpsvr_localtk=0.4004973382367907; uin=o1255067427; skey=@asReY9jds; pac_uid=1_1255067427; iip=0; _qimei_uuid42=17b0b110a251001b6af9019cceea51d81db376b7b3; _qimei_fingerprint=d618505bcea63dd91fa3ee781a735809; _qimei_q36=; _qimei_h38=fded401c6af9019cceea51d802000000b17b0b; o_minduid=AGQdiUR3hXJ3ECTRcxYgz230SLCUuKpv; appuser=BCF0966839C989C1; qq_domain_video_guid_verify=5020b578e44ca9c5; pgv_info=ssid=s4207741584; pgv_pvid=390148540; o_cookie=1255067427; vversion_name=8.2.95; video_omgid=5020b578e44ca9c5; ad_session_id=w3mckrfydvbtc; LPPBturn=464; full_screen_cid_pause_times=9; full_screen_pause_times=9; LPDFturn=666; LZCturn=694; LPSJturn=553; LBSturn=795; LVINturn=301; LPHLSturn=758; LZTturn=451; Lturn=424; LKBturn=860; LPVLturn=311; LPLFturn=337; LDERturn=395',
    'origin': 'https://v.qq.com',
    'referer': 'https://v.qq.com/',
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
}

data = '{"buid":"vinfoad","vinfoparam":"charge=0&otype=ojson&defnpayver=3&spau=1&spaudio=0&spwm=1&sphls=2&host=v.qq.com&refer=https%3A%2F%2Fv.qq.com%2Fx%2Fcover%2Fr5trbf8xs5uwok1%2Fp0018ha4w9j.html&ehost=https%3A%2F%2Fv.qq.com%2Fx%2Fcover%2Fr5trbf8xs5uwok1%2Fp0018ha4w9j.html&sphttps=1&encryptVer=9.2&cKey=bu7HecrM7_a1281Orq2-LnCjnpb8Ocr0cPTclKiOzEul_f4uOWcpW2JPR8Go77I8NQtSggMGzGraCp7VHCeQghpmp7rG5tiHjLv_PnnatnPaZezYhZnT8dfAi7su4Iue2F3x_IML6Zk3FjOj-NmZhE-NjjawCzIdF66cdsFdzz5jk70UOmynTHDptaxqIemxrSlkg-M_BbDaBoWwiX7uSsBkDK_qlv9BvC71CgXl1BaviS_BpuKq82bQx2On2AOQ35yHG6e0-dJ37Szr2rFp56lxzzDtPFKhwYCtsQcaQ5txIefj4bzawfy6lqn9rJ4fb4QhgKJtspPVSaSl29Zyy7900ICoeOJZY6b_P75Em4nh9wpcKyMc2-ZSG3QOk0hnCuc2Zr8bNdIi0MIn9qwngqj9OoLKuMvn8wyJy5AjxN0GmZunIA2U2-O4sSS-7vVWSPDZ13KeJMtTRgtk9G7IyRZN9fa59w9DHdG4G92rZNGPW_C1nc2-D8gzDmLQQXQVXUHzMj7UqNg4kSFRoFT2OuwjL5u6BCcuA7kSMIQ0mduNKdI3CdBvBIK_5gUFBQUFFdqsqQ&clip=4&guid=5020b578e44ca9c5&flowid=50ac2dd3c9a42d8aad938b528e95eee2&platform=10201&sdtfrom=v1010&appVer=1.29.1&unid=&auth_from=&auth_ext=&vid=p0018ha4w9j&defn=fhd&fhdswitch=0&dtype=3&spsrt=2&tm=1699767644&lang_code=0&logintoken=%7B%22access_token%22%3A%22B0647B0CBD234DBEBC4C6B6F570C23C4%22%2C%22appid%22%3A%22101483052%22%2C%22vusession%22%3A%22hL7gZ-2Curhg3lyBn0xLsw.M%22%2C%22openid%22%3A%22D94ACE51D4BA9DF1E25E3679C4C4FB75%22%2C%22vuserid%22%3A%22474921986%22%2C%22video_guid%22%3A%225020b578e44ca9c5%22%2C%22main_login%22%3A%22qq%22%7D&spvvpay=1&spadseg=3&spav1=15&hevclv=28&spsfrhdr=0&spvideo=0&spm3u8tag=67&spmasterm3u8=3&drm=40","sspAdParam":"{\\"ad_scene\\":1,\\"pre_ad_params\\":{\\"ad_scene\\":1,\\"user_type\\":-1,\\"video\\":{\\"base\\":{\\"vid\\":\\"p0018ha4w9j\\",\\"cid\\":\\"r5trbf8xs5uwok1\\"},\\"is_live\\":false,\\"type_id\\":0,\\"referer\\":\\"https://v.qq.com/channel/movie/list?filter_params=itype%3D100012&page_id=channel_list_second_page\\",\\"url\\":\\"https://v.qq.com/x/cover/r5trbf8xs5uwok1/p0018ha4w9j.html\\",\\"flow_id\\":\\"50ac2dd3c9a42d8aad938b528e95eee2\\",\\"refresh_id\\":\\"\\",\\"fmt\\":\\"fhd\\"},\\"platform\\":{\\"guid\\":\\"5020b578e44ca9c5\\",\\"channel_id\\":0,\\"site\\":\\"web\\",\\"platform\\":\\"in\\",\\"from\\":0,\\"device\\":\\"pc\\",\\"play_platform\\":10201,\\"pv_tag\\":\\"www_baidu_com|channel\\",\\"support_click_scan_integration\\":true},\\"player\\":{\\"version\\":\\"1.29.0\\",\\"plugin\\":\\"3.4.22\\",\\"switch\\":1,\\"play_type\\":\\"0\\"},\\"token\\":{\\"type\\":1,\\"vuid\\":474921986,\\"vuser_session\\":\\"hL7gZ-2Curhg3lyBn0xLsw.M\\",\\"app_id\\":\\"101483052\\",\\"open_id\\":\\"D94ACE51D4BA9DF1E25E3679C4C4FB75\\",\\"access_token\\":\\"B0647B0CBD234DBEBC4C6B6F570C23C4\\"}}}","adparam":"adType=preAd&vid=p0018ha4w9j&sspKey=wuer","lcAdCookie":"o_minduid=AGQdiUR3hXJ3ECTRcxYgz230SLCUuKpv; appuser=BCF0966839C989C1; ad_session_id=w3mckrfydvbtc; LPPBturn=464; full_screen_cid_pause_times=9; full_screen_pause_times=9; LPDFturn=666; LZCturn=694; LPSJturn=553; LBSturn=795; LVINturn=301; LPHLSturn=758; LZTturn=451; Lturn=424; LKBturn=860; LPVLturn=311; LPLFturn=337; LDERturn=395"}'

response = requests.post('https://vd6.l.qq.com/proxyhttp', cookies=cookies, headers=headers, data=data)

html_data = response.json()['vinfo']
jsondata = json.loads(html_data)
# result = re.findall('url(.*?),', html_data)
# soup = BeautifulSoup(html, 'html-parser')
# print(jsondata)
# m3u8_text = jsondata['vl']['vi'][0]['ul']['m3u8']
text = jsondata['vl']['vi'][0]['ul']['ui'][0]['hls']['pt']
url = jsondata['vl']['vi'][0]['ul']['ui'][0]['url']
m3u8_text = requests.get(url + text).text
m3u8_text = re.sub('#E.*', '', m3u8_text)
print(m3u8_text)
ts_list = m3u8_text.split()
ts_list.pop(0)

for ts in tqdm(ts_list):
    # ts_url = 'https://bcaeb3bfea6a04a379aad5ef117ef3182e5b1245d842aa52.v.smtcdns.com/vipts.tc.qq.com/AP4CLEdJiIJV7y3HsuKXZt-IVZjXDYpQfhJYbzfzCEZM/B_efeEBb4uHJ8TOTkZIB0oookwti3PhoTDayKgKkebH16WLrV2nmKr4n1h38b9doHK/svp_50112/QX_iP0u7kcx2BnXKlgOf1KCwjnYYQy3Zt8-24505ZebBbrVIWbESGcDyES3KQm7mQes6TCvEBeP3ru1VjMaIWOlQvG1L9MC7J5vZPFFcp95Eb8QluWJYki2XVJUHWdXMjUpRzkxbt56Q5gE8CQRmgma77hXq1Sm50JQanqCCMU1ohw99yG5xL5mMePfd4R-IrKjXYIR9_TEd2Ojc8VP2S6hz72XeDu6w9OowtzKH9RmvGIrRSBtGbA/' + ts
    ts_url = url + ts
    ts_data = requests.get(ts_url).content
    # mode='ab' 追加写入 mode='wb' 覆盖写入
    open('末日之战.mp4', mode='ab').write(ts_data)
