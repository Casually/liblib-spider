# 这里修改为自己的token，通过浏览器获取
# 读取 YAML 配置文件
import yaml
import os

class file_util:

    def __init__(self):
        self.path = os.path.dirname(os.path.abspath(__file__))

    def read_yml(file_path='conf/conf.yml'):
        with open(file_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config