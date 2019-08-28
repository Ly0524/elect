from fdfs_client.client import Fdfs_client

client = Fdfs_client(r'F:\PyCharm 2018.1.4\elect_web\venv\Lib\fdfs_client\client.conf')
ret = client.upload_by_filename(r'D:\goods.jpg')
