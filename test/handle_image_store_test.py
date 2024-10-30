import unittest
from PIL import Image
from unittest.mock import Mock, patch
from test_constants import TEST_RDS_CONFIG, TEST_EVENT, TEST_BAD_EVENT, TEST_SUCCESSFUL_QUERY
from lambda_s3_store_to_rds.src.lambda_s3_store_to_rds.handle_image_store import ImageStorer

class HandleImageStoreTest(unittest.TestCase):

    def setUp(self):
        self.mock_s3 = Mock()
        self.mock_rds = Mock()
        self.test_rds_config = TEST_RDS_CONFIG
        self.mock_logger = Mock()

        self.test_storer = ImageStorer(
            self.test_rds_config, 
            self.mock_rds, 
            self.mock_s3,
            self.mock_logger)

        self.patcher_image = patch("PIL.Image.open")
        self.mock_image_open = self.patcher_image.start()
        self.addCleanup(self.patcher_image.stop)
        self.patcher_sql = patch("pymysql.connect")
        self.mock_connect = self.patcher_sql.start()
        self.addCleanup(self.patcher_sql.stop)
        self.patcher_time = patch("time.time")
        self.mock_time = self.patcher_time.start()
        self.addCleanup(self.patcher_time.stop)

        #Happy Path Given

        #S3
        self.mock_s3_body = Mock()
        self.mock_s3_object = {"Body": self.mock_s3_body,
                          "ContentLength": 0,
                          "ContentType": 'png'}
        self.mock_s3.getObject.return_value = self.mock_s3_object

        #Image
        self.mock_s3_body.read.return_value = bytes(0)
        self.mock_image_file = Mock()
        self.mock_image_open.return_value = self.mock_image_file
        self.mock_image_file.size = (0,1)
        self.mock_time.return_value = 1700000000.00

        #DB
        self.mock_rds.generate_db_auth_token.return_value = "xyz"
        self.mock_cursor = Mock()
        self.mock_connection = Mock()
        self.mock_connect.return_value = self.mock_connection
        self.mock_connection.cursor.return_value = self.mock_cursor
        self.mock_cursor.rowcount = 1
    
    def test_happy_case(self):
        #Given
        #Created in Setup

        #When
        self.test_storer.handle(TEST_EVENT)

        #Then
        self.mock_cursor.execute.assert_called_with(TEST_SUCCESSFUL_QUERY)
        self.mock_logger.exception.assert_not_called

    def test_bad_event_throws_exception(self):
        #Gieven
        #Happy path Create in Setup

        #When & Then
        with self.assertRaises(Exception):
            self.test_storer.handle(TEST_BAD_EVENT)
        self.mock_logger
        self.mock_cursor.execute.assert_not_called
        self.mock_logger.exception.assert_called

    def test_bad_s3_connection(self):
        #Given
        self.mock_s3.getObject.side_effect = RuntimeError

        #When & Then
        with self.assertRaises(Exception):
            self.test_storer.handle(TEST_EVENT)
        self.mock_cursor.execute.assert_not_called
        self.mock_logger.exception.assert_called

    def test_bad_image(self):
        #Given
        self.mock_image_open.side_effect = ValueError

        #When & Then
        with self.assertRaises(Exception):
            self.test_storer.handle(TEST_EVENT)
        self.mock_cursor.execute.assert_not_called
        self.mock_logger.exception.assert_called

    def test_db_connection(self):
        #Given
        self.mock_connect.side_effect = ConnectionRefusedError

        #When & Then
        with self.assertRaises(Exception):
            self.test_storer.handle(TEST_EVENT)
        self.mock_cursor.execute.assert_not_called
        self.mock_logger.exception.assert_called

if __name__ == '__main__':
    unittest.main()