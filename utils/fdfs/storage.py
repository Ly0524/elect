from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings

class FDFSStorage(Storage):
    """fastdfs 文件存储类"""

    def _open(self, name, mode='rb'):
        # 打开文件时使用
        pass

    def _save(self,name,content):
        """保存文件时使用
        # name: 保存文件名字
        # content: 包含上  传文件内容的File对象"""
        client = Fdfs_client(self.client_conf)

        # 上传文件到fastdfs系统中
        res = client.upload_by_buffer(content.read())

        # res 返回 dict
        # {
        #     'Group name': group_name,
        #     'Remote file_id': remote_file_id,
        #     'Status': 'Upload successed.',
        #     'Local file name': local_file_name,
        #     'Uploaded size': upload_size,
        #     'Storage IP': storage_ip
        # }
        if res.get('Status') != 'Upload successed.':
            raise Exception('上传文件到FastDFS失败')

        # 获取返回的文件ID
        filename = res.get('Remote file_id')

        return filename

    def exists(self, name):
        """Django判断文件名是否可用"""
        return False

    def url(self, name):
        """返回访问文件url路径"""
        return self.base_url + name




