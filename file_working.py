import os

from config import files, name_global

def normpath(path: str) -> str:
    return os.path.normpath(path).replace('\\', '/')

def getfiles (dir: str) -> tuple:
    lstfi = []
    lstdi = []
    if os.path.isdir(dir):
        lstdir = os.listdir(dir)
        for i in range(len(lstdir)):
            if os.path.isdir(normpath(dir + '/' + str(lstdir[i]))):
                lstdi.append('📁 ' + str(lstdir[i]))
            else:
                lstfi.append(str(lstdir[i]))
    return lstdi, lstfi

def get_path_to_file (path: str, local_or_global: bool, user_id: int) -> str:
    if local_or_global:
        return os.path.realpath(normpath(f'{files}/{str(user_id)}{path}'))
    return os.path.realpath(normpath(f'{files}/{name_global}{path}'))

def repeat_name_file(path: str, count: int = 0) -> str:
    # print(1)
    # print(path)
    tmp_name, format_name = os.path.splitext(os.path.basename(path))
    # print(tmp_name)
    # print(format_name)
    if (count != 0):
        tmp_name += f' ({str(count)})'
    tmp_name += format_name
    # print(tmp_name)
    if os.path.isfile(f'{os.path.dirname(path)}/{tmp_name}'):
        return repeat_name_file(f'{os.path.dirname(path)}/{os.path.basename(path)}', count + 1)
    return f'{os.path.dirname(path)}/{tmp_name}', tmp_name