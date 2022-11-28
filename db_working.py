import os
import datetime
from xml.dom import minidom
import xml.etree.ElementTree as xml

from config import db_users, files, name_global




def get_database(user_id: int, only_root: bool = False, booling_return: bool = True) -> tuple:
    root = xml.parse(db_users).getroot()
    if only_root: return root

    db = root.findall(f"./User[ID='{str(user_id)}']")[0]
    PersonDir = db.findall("./PersonDir")[0]
    FileSpace = db.findall("./FileSpace")[0]
    VisibleFiles = db.findall("./VisibleFiles")[0]
    AdminRights = db.findall("./AdminRights")[0]
    FavoritesDir = db.findall("./FavoritesDir")[0]

    if booling_return:
        if FileSpace.text == 'local': FileSpace = True
        else: FileSpace = False
        if VisibleFiles.text == 'yes': VisibleFiles = True
        else: VisibleFiles = False
        if AdminRights.text == 'yes': AdminRights = True
        else: AdminRights = False

    return root, PersonDir, FileSpace, VisibleFiles, AdminRights, FavoritesDir

def check_db():
    try:
        get_database(0, only_root=True)
    except:
        root = xml.Element("dataroot")
        save_db(root)

def save_db (root):
    xmlstr = minidom.parseString(bytes(str(xml.tostring(root))[2:-1].replace('\\t', '').replace('\\n', ''), encoding='utf-8')).toprettyxml()
    with open(db_users, mode='w', encoding='utf-8') as file:
        file.write(xmlstr)

def new_user(message):
    root = get_database(message.from_user.id, only_root=True)
    if len(root.findall(f"./User[ID='{str(message.from_user.id)}']")) == 1:
        return None

    tabcode = xml.SubElement(root, 'User')

    item = xml.SubElement(tabcode, 'ID')
    item.text = str(message.from_user.id)

    item = xml.SubElement(tabcode, 'NickName')
    item.text = str(message.from_user.username)

    item = xml.SubElement(tabcode, 'FirstName')
    item.text = str(message.from_user.first_name)

    item = xml.SubElement(tabcode, 'LastName')
    item.text = str(message.from_user.last_name)

    dt = datetime.datetime.now()
    item = xml.SubElement(tabcode, 'DateAdd')
    item.text = dt.strftime('%d.%m.%Y %H:%M:%S')

    item = xml.SubElement(tabcode, 'PersonDir')
    item.text = '/'

    item = xml.SubElement(tabcode, 'FileSpace')
    item.text = 'local'

    item = xml.SubElement(tabcode, 'FavoritesDir')

    item = xml.SubElement(tabcode, 'VisibleFiles')
    item.text = 'yes'

    item = xml.SubElement(tabcode, 'AdminRights') # админ-доступ даёт право редактировать названия папок и ещё некоторые возможности
    item.text = 'no'
        
    save_db(root)

    try:
        os.mkdir(f'{files}/{str(message.from_user.id)}')
    except:
        ...

# check_db()