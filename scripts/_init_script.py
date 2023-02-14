import os
import sys
import django

"""离线脚本模拟启动django项目用来离线添加数据"""
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backstage.settings.dev")
django.setup()
