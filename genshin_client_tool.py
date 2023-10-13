import json
import hashlib
import os
import webbrowser

import requests
from tqdm import tqdm

VERSION = '1.1.1'
API_VERSIONCHECK = 'https://api.github.com/repos/orilights/genshin-client-tool/releases/latest'
URL_RELEASE = 'https://github.com/orilights/genshin-client-tool/releases/latest'

clients = {
    'Yuanshen.exe': 'GENSHIN_CN',
    'GenShinImpact.exe': 'GENSHIN_OS',
}

apis = {
    'CLIENTINFO': {
        'GENSHIN_CN': {
            'base': 'https://sdk-static.mihoyo.com/hk4e_cn/mdk/launcher/api/resource',
            'querys': {
                'launcher_id': '18',
                'key': 'eYd89JmJ',
            }
        },
        'GENSHIN_OS': {
            'base': 'https://sdk-os-static.mihoyo.com/hk4e_global/mdk/launcher/api/resource',
            'querys': {
                'launcher_id': '10',
                'key': 'gcStgarh',
            }
        },
        'STARRAIL_CN': {
            'base': 'https://api-launcher-static.mihoyo.com/hkrpg_cn/mdk/launcher/api/resource',
            'querys': {
                'launcher_id': '33',
                'key': '6KcVuOkbcqjJomjZ',
            }
        },
        'STARRAIL_OS': {
            'base': 'https://hkrpg-launcher-static.hoyoverse.com/hkrpg_global/mdk/launcher/api/resource',
            'querys': {
                'launcher_id': '35',
                'key': 'vplOVX8Vn7cwG8yb',
            }
        }
    }
}

pkg_list = [{
    'name': '游戏文件',
    'type': 'game',
    'pkg_version': 'pkg_version',
}, {
    'name': '中文语音文件',
    'type': 'audio',
    'pkg_version': 'Audio_Chinese_pkg_version',
}, {
    'name': '日语语音文件',
    'type': 'audio',
    'pkg_version': 'Audio_Japanese_pkg_version',
}, {
    'name': '英语语音文件',
    'type': 'audio',
    'pkg_version': 'Audio_English(US)_pkg_version',
}, {
    'name': '韩语语音文件',
    'type': 'audio',
    'pkg_version': 'Audio_Korean_pkg_version',
}]

menu = [{
    'name': '输出游戏文件信息',
    'func': 'print_gameinfo',
    'id': '1',
}, {
    'name': '校验游戏文件',
    'func': 'verify_gameclient',
    'id': '2',
}, {
    'name': '修复游戏客户端',
    'func': 'fix_gameclient',
    'id': '3',
}, {
    'name': '清理游戏客户端',
    'func': 'clean_gameclient',
    'id': '4',
}, {
    'name': '更新游戏包信息文件',
    'func': 'update_gameclient_pkginfo',
    'id': '5',
}, {
    'name': '退出程序',
    'func': 'exit',
    'id': '0',
}]

latest_version = None
gameclient_info = None


def get_latest_version():
    try:
        r = requests.get(API_VERSIONCHECK, timeout=5)
        return r.json()['tag_name']
    except:
        return '0.0.0'


def get_gameclient_info():
    try:
        r = requests.get(get_api('CLIENTINFO'), timeout=5)
        data = r.json()['data']
        return {
            'version': data['game']['latest']['version'],
            'decompressed_path': data['game']['latest']['decompressed_path'],
        }
    except:
        return None


def get_pkgs():
    pkgs = []
    for pkg in pkg_list:
        if os.path.exists(pkg['pkg_version']):
            pkgs.append(pkg)
    return pkgs


def get_gameclient_channel():
    for key, value in clients.items():
        if os.path.exists(key):
            return value
    return None


def get_deletelist(filelist: list):
    deletelist = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file in [item['pkg_version'] for item in pkg_list]:
                continue
            if file.endswith('.exe'):
                continue
            if file.endswith('.py'):
                continue
            if file.endswith('.zip'):
                continue
            if file == 'config.ini':
                continue
            if root.count('ScreenShot') >= 1:
                continue
            filename = format_path(os.path.join(root, file))
            if filename not in filelist:
                deletelist.append(filename)
    return deletelist


def get_api(api_name: str):
    return get_req_url(apis[api_name][get_gameclient_channel()]['base'],
                       apis[api_name][get_gameclient_channel()]['querys'])


def get_req_url(base_url: str, querys: dict):
    if len(querys.keys()) == 0:
        return base_url
    query_list = []
    for key, value in querys.items():
        query_list.append(f'{key}={value}')
    return f'{base_url}?{"&".join(query_list)}'


def format_btyes(size: int):
    u_list = ['B', 'KB', 'MB', 'GB', 'TB']
    u_index = 0
    while size >= 1024:
        size /= 1024
        u_index += 1
    return f'{size:.2f}{u_list[u_index]}'


def format_path(path: str):
    return path.replace('\\', '/').removeprefix('./')


def parse_data(filename):
    f = open(filename, 'r')
    result = []
    for line in f.readlines():
        result.append(json.loads(line))
    return result


def parse_version(version: str):
    return tuple(map(int, version.split('.')))


def verify_file(filename, md5):
    if not os.path.exists(filename):
        return None
    with open(filename, 'rb') as f:
        md5_obj = hashlib.md5()
        md5_obj.update(f.read())

    if md5_obj.hexdigest() == md5:
        return True
    else:
        return False


def verify_data(data: list):
    failed_list = []
    for item in tqdm(data):
        verify_result = verify_file(item['remoteName'], item['md5'])
        if verify_result is None:
            failed_list.append(f'文件 {item["remoteName"]} 不存在')
            continue
        if not verify_result:
            failed_list.append(f'文件 {item["remoteName"]} 校验失败')
    if len(failed_list) == 0:
        print('所有文件检验通过')
    else:
        print('检验完毕，发现以下错误：')
        for item in failed_list:
            print(item)


def press_anykey():
    os.system('pause')


def draw_line():
    print('-' * 30)


def confirm(msg: str):
    input_confirm = input(f'{msg} [y/n]: ')
    if input_confirm.lower() not in ['y', 'yes', '是', '确认']:
        print('操作已取消')
        press_anykey()
        return False
    return True


def show_info(data: list):
    total_size = 0
    for item in data:
        total_size += item['fileSize']
    print(f'共 {len(data)} 个文件，总大小: {format_btyes(total_size)}')


def print_gameinfo():
    os.system('cls')
    draw_line()

    pkgs = get_pkgs()
    if len(pkgs) == 0:
        print('未找到游戏包信息文件')
        press_anykey()
        return

    print('查找到以下游戏包信息文件:')
    for pkg in pkgs:
        print(pkg['name'], end=' ')
    print()
    draw_line()

    for index, pkg in enumerate(pkgs):
        print(f'[{index+1}/{len(pkgs)}] {pkg["name"]}信息:')
        pkg_data = parse_data(pkg['pkg_version'])
        show_info(pkg_data)

    draw_line()
    press_anykey()


def verify_gameclient():
    os.system('cls')
    draw_line()

    pkgs = get_pkgs()
    if len(pkgs) == 0:
        print('未找到游戏包信息文件')
        press_anykey()
        return

    print('开始校验游戏文件')
    draw_line()

    for index, pkg in enumerate(pkgs):
        print(f'[{index+1}/{len(pkgs)}] 校验{pkg["name"]}:')
        pkg_data = parse_data(pkg['pkg_version'])
        verify_data(pkg_data)
    draw_line()

    print('校验完毕')

    draw_line()
    press_anykey()


def fix_gameclient():
    global gameclient_info

    os.system('cls')
    draw_line()

    pkgs = get_pkgs()
    if len(pkgs) == 0:
        print('未找到游戏包信息文件')
        press_anykey()
        return

    gameclient_info = get_gameclient_info()
    if gameclient_info is None:
        print('获取游戏版本信息失败')
        press_anykey()
        return

    print(f'游戏最新版本：{gameclient_info["version"]}')
    draw_line()

    print('查找到以下游戏包信息文件:')
    for pkg in pkgs:
        print(pkg['name'], end=' ')
    print()
    draw_line()

    fix_list = []

    for pkg in pkgs:
        print(f'校验{pkg["name"]}')
        pkg_data = parse_data(pkg['pkg_version'])
        for item in tqdm(pkg_data):
            verify_result = verify_file(item['remoteName'], item['md5'])
            if verify_result is None:
                fix_list.append(item)
                continue
            if not verify_result:
                fix_list.append(item)
    draw_line()

    if len(fix_list) == 0:
        print('所有文件检验通过，无需修复')
        press_anykey()
        return

    total_size = sum([item['fileSize'] for item in fix_list])
    print(f'检验完毕，{len(fix_list)} 个文件需要修复，总大小: {format_btyes(total_size)}')
    draw_line()
    if not confirm('是否确认开始下载？'):
        return
    draw_line()

    progress_total = tqdm(
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
        total=total_size,
        desc='下载进度',
    )

    downloaded_size = 0
    for item in fix_list:
        progress = tqdm(unit='B',
                        unit_scale=True,
                        unit_divisor=1024,
                        total=item['fileSize'],
                        desc=item['remoteName'].split('/')[-1],
                        leave=False)

        r = requests.get(f'{gameclient_info["decompressed_path"]}/{item["remoteName"]}', stream=True)
        os.makedirs(os.path.dirname(item['remoteName']), exist_ok=True)
        with open(item['remoteName'], 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    progress.update(len(chunk))
                    progress_total.update(len(chunk))
        progress.close()
        downloaded_size += item['fileSize']
    progress_total.close()
    draw_line()

    print('修复完毕')

    draw_line()
    press_anykey()


def clean_gameclient():
    os.system('cls')
    draw_line()

    pkgs = get_pkgs()
    if len(pkgs) == 0:
        print('未找到游戏包信息文件')
        press_anykey()
        return

    print('查找到以下游戏包信息文件:')
    for pkg in pkgs:
        print(pkg['name'], end=' ')
    print()
    draw_line()

    print('请注意，如继续操作，将会删除不存在于上述游戏包信息中的文件')
    draw_line()
    if not confirm('是否确认继续？'):
        return
    draw_line()

    print('使用注意:')
    print('1. 本操作将会删除任何不存在于游戏包信息中的文件')
    print('2. 理论上将会跳过规范保存的游戏截图(ScreenShot文件夹)、预下载文件、可执行程序，但保险起见建议备份截图文件')
    print('3. 请不要在清理过程中运行游戏程序')
    print('4. 清理结束后，第一次运行游戏时将会需要重新下载热更新文件并完整校验游戏文件')
    draw_line()
    if not confirm('是否确认开始查找可清理文件？'):
        return
    draw_line()

    filelist = []
    for pkg in pkgs:
        pkg_data = parse_data(pkg['pkg_version'])
        for item in pkg_data:
            item['remoteName'] = format_path(item['remoteName'])
        filelist.extend([item['remoteName'] for item in pkg_data])
    deletelist = get_deletelist(filelist)
    if len(deletelist) == 0:
        print('没有找到可清理的文件')
        press_anykey()
        return
    for file in deletelist:
        print(f'{file}')
    draw_line()
    print(f'将删除以上 {len(deletelist)} 个文件，总大小:  {format_btyes(sum([os.path.getsize(item) for item in deletelist]))}')
    if not confirm('是否确认开始清理？'):
        return
    draw_line()

    for file in deletelist:
        print(f'删除文件 {file}')
        try:
            os.remove(file)
        except:
            print(f'删除文件 {file} 失败, 尝试强制删除')
            os.system('del /f ' + file.replace('/', '\\'))

    print('清理完毕')

    draw_line()
    press_anykey()


def update_gameclient_pkginfo():
    global gameclient_info

    os.system('cls')
    draw_line()

    gameclient_info = get_gameclient_info()
    if gameclient_info is None:
        print('获取游戏版本信息失败')
        press_anykey()
        return

    print(f'游戏最新版本：{gameclient_info["version"]}')

    pkgs = get_pkgs()
    if len(pkgs) == 0:
        if confirm('未找到游戏包信息文件，是否下载？'):
            draw_line()
            for pkg in pkg_list:
                if pkg['type'] == 'audio':
                    if not confirm(f'是否下载 {pkg["name"]} 信息文件？'):
                        continue
                print(f'下载 {pkg["name"]} 信息文件')
                r = requests.get(f'{gameclient_info["decompressed_path"]}/{pkg["pkg_version"]}')
                with open(pkg['pkg_version'], 'wb') as f:
                    f.write(r.content)
            draw_line()
            print('下载完毕')
            press_anykey()
        return

    print('查找到以下游戏包信息文件:')
    for pkg in pkgs:
        print(pkg['name'], end=' ')
    print()
    draw_line()

    print('请注意，如继续操作，将会覆盖已有的游戏包信息文件')
    draw_line()
    if not confirm('是否确认继续？'):
        return
    draw_line()

    for pkg in pkgs:
        print(f'更新 {pkg["name"]} 信息文件')
        r = requests.get(f'{gameclient_info["decompressed_path"]}/{pkg["pkg_version"]}')
        with open(pkg['pkg_version'], 'wb') as f:
            f.write(r.content)

    draw_line()
    print('更新完毕')

    draw_line()
    press_anykey()


def loop_mainmenu():
    global latest_version
    os.system('cls')
    draw_line()
    print('原神客户端工具')
    draw_line()
    print(f'版本：{VERSION}')
    if latest_version is None:
        latest_version = get_latest_version()
        if latest_version == '0.0.0':
            print('获取版本信息失败')
        else:
            print(f'最新版本：{latest_version}')
        if parse_version(VERSION) < parse_version(latest_version):
            if confirm(f'发现新版本 {latest_version}，是否前往下载？'):
                webbrowser.open(URL_RELEASE)
                press_anykey()
                return
    print('作者：OriLight')
    print('仓库: https://github.com/orilights/genshin-client-tool')
    draw_line()
    print('请注意')
    print('如出现 31-4302 数据异常无法进入游戏，将本程序从游戏根目录下删除或移动至别处即可解决')
    draw_line()
    if get_gameclient_channel() is None:
        print('请将本工具放置于游戏根目录下运行（Yuanshen.exe/GenshinImpact.exe同级目录）')
        draw_line()
        press_anykey()
        exit(0)

    for item in menu:
        print(f'[{item["id"]}] {item["name"]}')
    draw_line()
    input_num = input('输入数字进行对应的操作: ')
    for item in menu:
        if input_num == item['id']:
            eval(item['func'])()
            return
    print('未知的输入')
    draw_line()
    press_anykey()


if __name__ == '__main__':
    while True:
        loop_mainmenu()
