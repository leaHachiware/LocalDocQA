import os
from flask import Flask
from app.views import main_bp  # 如果你注册了蓝图

def create_app():
    # 设置模板目录和静态文件目录
    base_dir = os.path.dirname(os.path.dirname(__file__))
    template_path = os.path.join(base_dir, 'templates')
    static_path = os.path.join(base_dir, 'static')

    app = Flask(__name__, template_folder=template_path, static_folder=static_path)

    app.config['UPLOAD_FOLDER'] = 'docs'
    app.register_blueprint(main_bp)

    return app

