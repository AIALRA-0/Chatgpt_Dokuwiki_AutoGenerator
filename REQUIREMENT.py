import sys  # 系统控件

from dotenv import load_dotenv  # 参数读取控件


def check_version() -> None:
    import pkg_resources  # 加载包资源
    import third_party.log  # 加载log库

    load_dotenv()  # 加载参数列表
    logger = third_party.log.setup_logger(__name__)

    # 阅读requirements.txt文件，并将每一行添加到列表中
    with open('requirements.txt') as f:
        required = f.read().splitlines()

    # 对于requirements.txt中列出的每个库，检查是否安装了相应的版本
    for package in required:
        # 使用pkg_resources库获取有关该库已安装版本的信息
        package_name, package_verion = package.split('~=')
        installed = pkg_resources.get_distribution(package_name)
        # 提取库名称和版本号
        name, version = installed.project_name, installed.version
        # 比较版本号，看看它是否与requirements.txt中的版本号相匹配
        if package != f'{name}=={version}':
            logger.error(f'{name} | 版本号 {version} 已安装但与要求的版本不匹配')
            sys.exit();
