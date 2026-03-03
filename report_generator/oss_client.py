# !/usr/bin/env python
# -*- coding:utf-8 -*-
import boto3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError

from config import config

from utils.logger_util import get_logger

logger = get_logger()



class S3Client:
    _s3_instance = None

    @staticmethod
    def _instance():
        """获取S3客户端单例"""
        if S3Client._s3_instance is None:
            # 配置验证
            if config.S3_ENDPOINT is None:
                raise Exception(f"请配置[{config.ENVIRONMENT}]环境的SDOSS信息")

            if (config.S3_ENDPOINT is None
                    or config.S3_BUCKET is None
                    or config.S3_ACCESS_KEY is None
                    or config.S3_SECRET_KEY is None):
                raise Exception(f"请配置SDOSS参数: endpoint、access_key、secret_key和bucket")

            # SDOSS超时配置
            boto_config = BotoConfig(
                retries={
                    "max_attempts": 10,
                    "mode": "standard"
                },
                connect_timeout=5,
                read_timeout=15
            )

            # 创建s3client
            S3Client._s3_instance = boto3.client(
                's3',
                endpoint_url=config.S3_ENDPOINT,
                aws_access_key_id=config.S3_ACCESS_KEY,
                aws_secret_access_key=config.S3_SECRET_KEY,
                config=boto_config
            )

            logger.info(f"S3客户端初始化成功 | 环境:{config.ENVIRONMENT} | Bucket:{config.S3_BUCKET}")

        return S3Client._s3_instance

    @staticmethod
    def upload_file(local_file_path, s3_file_path, days=10):
        """
        上传本地文件

        Args:
            local_file_path: 本地文件路径
            s3_file_path: S3文件路径
            days: 过期天数
        """
        try:
            s3 = S3Client._instance()
            bucket_name = config.S3_BUCKET
            expiry_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

            # 设置过期时间
            s3.upload_file(
                local_file_path,
                bucket_name,
                s3_file_path,
                ExtraArgs={
                    "Tagging": f"ExpiryDate={expiry_date}&ExpiryDays={days}"
                }
            )
            logger.info(f"[上传成功] {s3_file_path}")

        except FileNotFoundError:
            raise Exception(f"本地文件不存在: {local_file_path}")
        except Exception as e:
            logger.error(f"[上传失败] {s3_file_path} | {e}")
            raise Exception(f"S3上传文件失败: {type(e).__name__} - {str(e)}")

    @staticmethod
    def download_file(filename):
        """
        生成预签名下载URL

        Args:
            filename: 文件名

        Returns:
            预签名URL
        """
        try:
            s3 = S3Client._instance()
            bucket_name = config.S3_BUCKET

            url = s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": filename},
                ExpiresIn=3600
            )

            # 生产环境域名替换
            if config.ENVIRONMENT == "prd":
                url = str(url).replace("s3sdoss.smb956101.com", "10.10.50.137")

            return url

        except Exception as e:
            logger.error(f"[生成URL失败] {filename} | {e}")
            raise Exception(f"S3生成URL失败: {type(e).__name__} - {str(e)}")

    @staticmethod
    def download_to_file(obj_key, save_path):
        """
        下载文件到本地

        Args:
            obj_key: S3对象键
            save_path: 本地保存路径
        """
        try:
            s3 = S3Client._instance()
            bucket_name = config.S3_BUCKET

            s3.download_file(bucket_name, obj_key, save_path)
            logger.info(f"[下载成功] {obj_key} -> {save_path}")

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey' or error_code == '404':
                raise Exception(f"文件不存在: {obj_key}")
            else:
                logger.error(f"[下载失败] {obj_key} | {e}")
                raise Exception(f"S3下载文件失败: {error_code} - {str(e)}")

    @staticmethod
    def upload_bytes(file_content: bytes, object_name: str) -> str:
        """
        上传字节内容

        Args:
            file_content: 文件内容（字节）
            object_name: 对象键（路径）

        Returns:
            object_name
        """
        try:
            s3 = S3Client._instance()
            bucket_name = config.S3_BUCKET

            s3.put_object(
                Bucket=bucket_name,
                Key=object_name,
                Body=file_content
            )
            logger.info(f"[上传成功] {object_name}")
            return object_name

        except ClientError as e:
            logger.error(f"[上传失败] {object_name} | {e}")
            raise Exception(f"S3上传失败: {type(e).__name__} - {str(e)}")

    @staticmethod
    def download_bytes(object_name: str) -> bytes:
        """
        下载文件为字节

        Args:
            object_name: 对象键（路径）

        Returns:
            文件内容（字节）
        """
        try:
            s3 = S3Client._instance()
            bucket_name = config.S3_BUCKET

            response = s3.get_object(Bucket=bucket_name, Key=object_name)
            content = response['Body'].read()
            logger.info(f"[下载成功] {object_name} | {len(content)} 字节")
            return content

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                raise Exception(f"文件不存在: {object_name}")
            else:
                logger.error(f"[下载失败] {object_name} | {e}")
                raise Exception(f"S3下载失败: {error_code} - {str(e)}")

    @staticmethod
    def delete_file(object_name: str) -> bool:
        """
        删除文件

        Args:
            object_name: 对象键（路径）

        Returns:
            是否删除成功
        """
        try:
            s3 = S3Client._instance()
            bucket_name = config.S3_BUCKET

            s3.delete_object(Bucket=bucket_name, Key=object_name)
            logger.info(f"[删除成功] {object_name}")
            return True

        except ClientError as e:
            logger.error(f"[删除失败] {object_name} | {e}")
            raise Exception(f"S3删除失败: {type(e).__name__} - {str(e)}")

    @staticmethod
    def file_exists(object_name: str) -> bool:
        """
        检查文件是否存在

        Args:
            object_name: 对象键（路径）

        Returns:
            文件是否存在
        """
        try:
            s3 = S3Client._instance()
            bucket_name = config.S3_BUCKET

            s3.head_object(Bucket=bucket_name, Key=object_name)
            return True

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404' or error_code == 'NoSuchKey':
                return False
            else:
                logger.warning(f"[检查文件存在时出错] {object_name} | {e}")
                return False

    @staticmethod
    def list_files(prefix: str = "", max_keys: int = 1000) -> List[Dict]:
        """
        列出文件

        Args:
            prefix: 路径前缀（用于过滤）
            max_keys: 最大返回数量

        Returns:
            文件信息列表，每个元素包含 key, size, last_modified
        """
        try:
            s3 = S3Client._instance()
            bucket_name = config.S3_BUCKET

            response = s3.list_objects_v2(
                Bucket=bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )

            if 'Contents' not in response:
                return []

            return [
                {
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat()
                }
                for obj in response['Contents']
            ]

        except ClientError as e:
            logger.error(f"[列表失败] prefix={prefix} | {e}")
            raise Exception(f"S3列表失败: {type(e).__name__} - {str(e)}")

    @staticmethod
    def get_file_info(object_name: str) -> Optional[Dict]:
        """
        获取文件元数据

        Args:
            object_name: 对象键（路径）

        Returns:
            文件信息字典，包含 size, content_type, last_modified 等
        """
        try:
            s3 = S3Client._instance()
            bucket_name = config.S3_BUCKET

            response = s3.head_object(Bucket=bucket_name, Key=object_name)
            return {
                'key': object_name,
                'size': response['ContentLength'],
                'content_type': response.get('ContentType', ''),
                'last_modified': response['LastModified'].isoformat()
            }
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404' or error_code == 'NoSuchKey':
                logger.info(f"[文件不存在] {object_name}")
                return None
            else:
                logger.error(f"[获取信息失败] {object_name} | {e}")
                return None


# 创建全局实例引用（保持向后兼容）
def get_s3_client():
    """获取S3客户端实例"""
    return S3Client._instance()


if __name__ == "__main__":
    print(f"当前环境: {config.ENVIRONMENT}")
    print(f"S3端点: {config.S3_ENDPOINT}")
    print(f"S3桶名: {config.S3_BUCKET}")

    # =============================================== 测试S3连接
    if True:
        print("\n" + "=" * 60)
        print("测试S3连接")
        print("=" * 60)
        try:
            files = S3Client.list_files(prefix="", max_keys=1)
            print("[成功] S3连接正常")
        except Exception as e:
            print(f"[失败] {e}")

    # =============================================== 测试上传字节
    if True:
        print("\n" + "=" * 60)
        print("测试上传字节")
        print("=" * 60)
        try:
            test_key = "test/s3_test.txt"
            test_content = b"This is a test file"
            s3_id = S3Client.upload_bytes(test_content, test_key)
            print(f"[成功] {s3_id}")
        except Exception as e:
            print(f"[失败] {e}")

    # =============================================== 测试文件是否存在
    if True:
        print("\n" + "=" * 60)
        print("测试文件存在")
        print("=" * 60)
        try:
            test_key = "test/s3_test.txt"
            exists = S3Client.file_exists(test_key)
            print(f"[结果] 文件存在: {exists}")
        except Exception as e:
            print(f"[失败] {e}")

    # =============================================== 测试获取文件信息
    if True:
        print("\n" + "=" * 60)
        print("测试获取文件信息")
        print("=" * 60)
        try:
            test_key = "test/s3_test.txt"
            info = S3Client.get_file_info(test_key)
            if info:
                print(f"键名: {info['key']}")
                print(f"大小: {info['size']} 字节")
                print(f"类型: {info['content_type']}")
                print(f"时间: {info['last_modified']}")
            else:
                print("[提示] 文件不存在")
        except Exception as e:
            print(f"[失败] {e}")

    # =============================================== 测试下载预签名URL
    if True:
        print("\n" + "=" * 60)
        print("测试下载预签名URL")
        print("=" * 60)
        try:
            test_key = "test/s3_test.txt"
            url = S3Client.download_file(test_key)
            print(f"[成功] URL已生成")
            print(f"URL: {url[:100]}...")
        except Exception as e:
            print(f"[失败] {e}")

    # =============================================== 测试下载字节
    if False:
        print("\n" + "=" * 60)
        print("测试下载字节")
        print("=" * 60)
        try:
            test_key = "test/s3_test.txt"
            content = S3Client.download_bytes(test_key)
            print(f"[成功] {len(content)} 字节")
            print(f"内容: {content.decode('utf-8')}")
        except Exception as e:
            print(f"[失败] {e}")

    # =============================================== 测试列表
    if True:
        print("\n" + "=" * 60)
        print("测试列表")
        print("=" * 60)
        try:
            files = S3Client.list_files(prefix="test/", max_keys=10)
            print(f"找到 {len(files)} 个文件:")
            for f in files[:5]:  # 只显示前5个
                print(f"  - {f['key']} ({f['size']} 字节)")
        except Exception as e:
            print(f"[失败] {e}")

    # =============================================== 测试删除
    if True:
        print("\n" + "=" * 60)
        print("测试删除")
        print("=" * 60)
        try:
            test_key = "test/s3_test.txt"
            success = S3Client.delete_file(test_key)
            print(f"[成功] {test_key} 已删除")
        except Exception as e:
            print(f"[失败] {e}")

    # =============================================== 再次检查文件是否存在
    if True:
        print("\n" + "=" * 60)
        print("验证删除")
        print("=" * 60)
        try:
            test_key = "test/s3_test.txt"
            exists = S3Client.file_exists(test_key)
            print(f"[结果] 文件存在: {exists} (应该是 False)")
        except Exception as e:
            print(f"[失败] {e}")

    print("\n测试完成\n")