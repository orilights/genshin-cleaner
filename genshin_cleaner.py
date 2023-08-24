import json
import hashlib
import os

from tqdm import tqdm

VERSION = '1.0.2'

pkg_list = [{
    'name': '游戏文件',
    'pkg_version': 'pkg_version',
}, {
    'name': '中文语音文件',
    'pkg_version': 'Audio_Chinese_pkg_version',
}, {
    'name': '日语语音文件',
    'pkg_version': 'Audio_Japanese_pkg_version',
}, {
    'name': '英语语音文件',
    'pkg_version': 'Audio_English(US)_pkg_version',
}, {
    'name': '韩语语音文件',
    'pkg_version': 'Audio_Korean_pkg_version',
}]


def get_pkgs():
    pkgs = []
    for pkg in pkg_list:
        if os.path.exists(pkg['pkg_version']):
            pkgs.append(pkg)
    return pkgs


def format_btyes(size: int):
    u_list = ['B', 'KB', 'MB', 'GB', 'TB']
    u_index = 0
    while size >= 1024:
        size /= 1024
        u_index += 1
    return f'{size:.2f}{u_list[u_index]}'


def parse_data(filename):
    f = open(filename, 'r')
    result = []
    for line in f.readlines():
        result.append(json.loads(line))
    return result


def verify_file(filename, md5):
    if not os.path.exists(filename):
        return None
    f = open(filename, 'rb')
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
        if not verify_result:
            failed_list.append(f'文件 {item["remoteName"]} 校验失败')
    if len(failed_list) == 0:
        print('所有文件检验通过')
    else:
        print('检验完毕，发现以下错误：')
        for item in failed_list:
            print(item)
        press_anykey()


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
            filename = os.path.join(root, file).replace('\\', '/').removeprefix('./')
            if filename not in filelist:
                deletelist.append(filename)
    return deletelist


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


def verify_game():
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
    print('1. 本工具将会删除任何不存在于游戏包信息中的文件')
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
        filelist.extend([item['remoteName'] for item in pkg_data])
    deletelist = get_deletelist(filelist)
    for file in deletelist:
        print(f'{file}')
    draw_line()
    if len(deletelist) == 0:
        print('没有找到可清理的文件')
        press_anykey()
        return
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


def loop_mainmenu():
    os.system('cls')
    draw_line()
    print('原神客户端清理工具')
    draw_line()
    print(f'版本：{VERSION}')
    print('作者：OriLight')
    print('仓库: https://github.com/orilights/genshin-cleaner')
    draw_line()
    if not os.path.exists('Yuanshen.exe') and not os.path.exists('GenshinImpact.exe'):
        print('请将本工具放置于游戏根目录下运行（Yuanshen.exe/GenshinImpact.exe同级目录）')
        press_anykey()
        exit(1)
    print('[1] 输出游戏文件信息')
    print('[2] 校验游戏文件')
    print('[3] 清理游戏客户端')
    print('[0] 退出程序')
    draw_line()
    input_num = input('输入数字进行对应的操作: ')
    if input_num == '0':
        exit(0)
    elif input_num == '1':
        print_gameinfo()
    elif input_num == '2':
        verify_game()
    elif input_num == '3':
        clean_gameclient()
    else:
        print('未知的输入')
        press_anykey()


if __name__ == '__main__':
    while True:
        loop_mainmenu()
