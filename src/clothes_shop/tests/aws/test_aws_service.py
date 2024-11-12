import unittest
from io import BytesIO
from unittest.mock import MagicMock, patch

from rest_framework.test import APITestCase

from clothes_shop.services.aws_service import AWS_Service


class AWSServiceTests(APITestCase):

    def setUp(self):
        self.aws_service = AWS_Service()
        self.mock_file = MagicMock()
        self.mock_file.name = "test_image.jpg"
        self.mock_file.content = BytesIO(b"Test content")

    def test_hash_filename(self):
        hashed_name = self.aws_service.hash_filename(self.mock_file.name)
        self.assertTrue(
            hashed_name.endswith(".jpg"), "Hashed filename should retain original file extension"
        )
        self.assertEqual(
            len(hashed_name.split(".")[0]), 64, "Hashed name should be 64 characters long"
        )

    def test_is_valid_image_extension_valid(self):
        self.assertTrue(self.aws_service.is_valid_image_extension(self.mock_file))

    def test_is_valid_image_extension_invalid(self):
        self.mock_file.name = "test_image.txt"
        self.assertFalse(
            self.aws_service.is_valid_image_extension(self.mock_file),
        )

    @patch("clothes_shop.services.aws_service.boto3.client")
    def test_upload_to_s3_success(self, mock_s3_client):
        # S3クライアントのモックを設定し、upload_fileobjが正常に動作するようにする
        s3_instance = mock_s3_client.return_value
        s3_instance.upload_fileobj.return_value = None  # 成功時はNoneを返す

        # aws_service = AWS_Service()

        # ダミーのファイルを作成してアップロードをテスト
        with open("dummy.jpg", "wb") as file:
            file.write(b"dummy data")
        with open("dummy.jpg", "rb") as file:
            result = self.aws_service.upload_to_s3(file)

        # テスト結果を検証
        self.assertIsNotNone(result)  # S3 URLが返されていることを確認

    @patch("clothes_shop.services.aws_service.boto3.client")
    def test_upload_to_s3_failure(self, mock_s3_client):
        s3_instance = mock_s3_client.return_value
        s3_instance.upload_fileobj.side_effect = Exception("Mocked upload error")

        s3_url = self.aws_service.upload_to_s3(self.mock_file)
        self.assertIsNone(s3_url)
