import configparser
import openai
import hashlib

from PyQt5.QtGui import QTextCursor
from tinydb import TinyDB, Query
from typing import Union, List, Dict
from pydantic import BaseModel, BaseConfig, Extra
# from third_party.revChatGPT.V1 import Chatbot, Error
from third_party.revChatGPT.V3 import Chatbot
import os
import time

from third_party.chatbot.chatgpt import ChatGPTBrowserChatbot


class OpenAIAuthBase(BaseModel):
    mode: str = "browserless"
    """OpenAI 的登录模式，可选的值：browserless - 无浏览器登录 browser - 浏览器登录"""
    proxy: Union[str, None] = None
    """可选的代理地址"""
    driver_exec_path: Union[str, None] = None
    """可选的 Chromedriver 路径"""
    browser_exec_path: Union[str, None] = None
    """可选的 Chrome 浏览器路径"""
    conversation: Union[str, None] = None
    """初始化对话所使用的UUID"""
    paid: bool = False
    """使用 ChatGPT Plus"""
    verbose: bool = False
    """启用详尽日志模式"""
    title_pattern: str = ""
    """自动修改标题，为空则不修改"""
    auto_remove_old_conversations: bool = False
    """自动删除旧的对话"""

    class Config(BaseConfig):
        extra = Extra.allow


class OpenAIEmailAuth(OpenAIAuthBase):
    email: str
    """OpenAI 注册邮箱"""
    password: str
    """OpenAI 密码"""
    isMicrosoftLogin: bool = False
    """是否通过 Microsoft 登录"""


def loading_strip(_ui):
    for count in range(11):
        time.sleep(0.1)
        _ui.LogBox.clear()
        _ui.LogBox.append("OpenAI 服务器登录中……")
        _ui.LogBox.append("\r登录中: {0} {1}%".format("▇" * count, (count * 10)))


def get_user_account():
    config = configparser.ConfigParser()  # 创建config对象
    config.read("config.cfg", encoding='utf-8')  # 读取配置
    openai_email = (config.items("OPENAI_ACCOUNT")[0][1]).strip("'").strip('"')
    openai_password = (config.items("OPENAI_ACCOUNT")[1][1]).strip("'").strip('"')
    openai_paid = (config.items("OPENAI_ACCOUNT")[2][1]).strip("'").strip('"')
    openai_session_token = (config.items("OPENAI_ACCOUNT")[3][1]).strip("'").strip('"')
    return openai_email, openai_password, openai_paid, openai_session_token


# def openai_account_login_v1():
#     def __save_login_cache(account: OpenAIAuthBase, cache: dict):
#         """保存登录缓存"""
#         account_sha = hashlib.sha256(account.json().encode('utf8')).hexdigest()
#         q = Query()
#         cache_db.upsert({'account': account_sha, 'cache': cache}, q.account == account_sha)
#
#     def get_access_token():
#         return bot.session.headers.get('Authorization').removeprefix('Bearer ')
#
#     def __V1_check_auth() -> bool:
#         try:
#             bot.get_conversations(0, 1)
#             return True
#         except (Error, KeyError) as e:
#             return False
#
#     config = {"email": (get_user_account())[0], "password": (get_user_account())[1], "paid": (get_user_account())[2],
#               "session_token": (get_user_account())[3]}
#     cache_db = TinyDB('data/login_caches.json')
#     account = OpenAIEmailAuth(email=config["email"], password=config["password"])
#
#     try:
#         os.mkdir('data')
#         print("警告：未检测到 data 目录，如果你通过 Docker 部署，请挂载此目录以实现登录缓存，否则可忽略此消息。")
#     except:
#         pass
#
#     try:
#         print()
#         print("OpenAI 服务器登录中……")
#         print("尝试使用 email + password 登录中...")
#         bot = Chatbot(config=config)
#         bot.account = account
#         __save_login_cache(account=account, cache={
#             "session_token": config['session_token'],
#             "access_token": get_access_token(),
#         })
#         if __V1_check_auth():
#             loading_strip()
#             print("\nOpenAI 服务器登录成功")
#             print()
#             return ChatGPTBrowserChatbot(bot, account.mode)
#     except:
#         loading_strip()
#         print("\nOpenAI 服务器登录失败！")
#         print()
#         exit(-1)

def openai_account_login_v3(_ui):
    config = configparser.ConfigParser()  # 创建config对象
    config.read("config.cfg", encoding='utf-8')  # 读取配置
    api_key = (config.items("OPENAI_API_KEY")[0][1]).strip("'").strip('"')

    try:
        print()
        _ui.LogBox.append("OpenAI 服务器登录中……")
        bot = Chatbot(api_key)

        loading_strip(_ui)
        _ui.LogBox.append("\nOpenAI 服务器登录成功")
        _ui.LogBox.append("\n")
        return bot
    except:
        loading_strip(_ui)
        _ui.LogBox.append("\nOpenAI 服务器登录失败！")
        _ui.LogBox.append("\n")
        exit(-1)


def chatgptweb_send_message_v3(_bot, _prompt, _temperature, _model):
    text = ""
    _bot.engine = _model
    for data in _bot.ask(_prompt, temperature=_temperature, engine=_model):
        text += data
    return text


def send_request_api(_text, _temperature):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=_text,
        temperature=_temperature,
        max_tokens=1500,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )
    return response["choices"][0]["text"].strip()


def send_message_api(_message, _temperature=0.0, end_tag=""):  # 向chatgpt发送内容

    # API Key
    config = configparser.ConfigParser()  # 创建config对象
    config.read("config.cfg", encoding='utf-8')  # 读取配置
    openai.api_key = str(config.items("OPENAI_API_KEY")[0][1]).strip("'").strip('"')  # 获取key

    # 文本内容
    text = _message
    response_text = ""
    response_text += send_request_api(text, _temperature)
    while end_tag not in response_text:
        response_text += send_request_api(text, _temperature)
    return response_text


if __name__ == "__main__":
    bot = openai_account_login_v3()
    print(chatgptweb_send_message_v3(bot, "你好"))
