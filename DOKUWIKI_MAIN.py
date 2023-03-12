from third_party import dokuwiki
import configparser


# 获取用户信息
def get_user_config():
    config = configparser.ConfigParser()  # 创建config对象
    config.read("config.cfg", encoding='utf-8')  # 读取配置
    url = str(config.items("DOKUWIKI")[0][1]).strip("'").strip('"')
    user = str(config.items("DOKUWIKI")[1][1]).strip("'").strip('"')
    password = str(config.items("DOKUWIKI")[2][1]).strip("'").strip('"')
    return url, user, password


def get_requirements():
    config = configparser.ConfigParser()  # 创建config对象
    config.read("config.cfg", encoding='utf-8')  # 读取配置
    requirements = str(config.items("REQUIREMENTS")[0][1]).strip("'").strip('"')
    return requirements


# 连接到 DokuWiki 的 XML-RPC API
def connect_dokuwiki():
    _url, _user, _password = get_user_config()
    try:
        wiki = dokuwiki.DokuWiki(_url, _user, _password)
    except (dokuwiki.DokuWikiError, Exception) as err:
        print('链接失败: %s' % err)
        return
    print("链接成功，登录用户: {0}".format(_user))
    return wiki


def create_page(_wiki, _type, _word, _text):
    # 分类 页面和标题
    _page_name = _type + ":" + _word[0] + " " + _word[1]
    title = "====== " + _word[0] + " (" + _word[1] + ") ======\n"
    _text = title + _text
    # 请求 xmlrpc api
    _wiki.pages.set(_page_name, _text)
    return _page_name
