import logging
import urllib.parse
import time
import pymysql
from typing import Any, Dict, Tuple
import PIL 
from io import BytesIO
from .models import TableEntry, ImageProperties

class ImageStorer:

    def __init__(self, rds_configs, rds_client, s3_client, logger):
        self.rds_configs = rds_configs
        self.rds_client = rds_client
        self.s3_client = s3_client
        self.logger = logger

    def _parse_event(self, event: Any) -> Tuple[str, str]: 
        try:
            bucket = event['Records'][0]['s3']['bucket']['name']
            key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
        except Exception as e:
            self.logger.exception('Error Parsing Request.')
            raise 
        self.logger.info("Processing Image {} in s3 bucket {}".format(key, bucket))
        return bucket, key

    def _get_s3_object(self, bucket: str, key: str) -> Any:
        try:
            s3_object = self.s3_client.getObject(Bucket=bucket, Key=key)
        except Exception as e:
            self.logger.exception('Error getting object %s from bucket %s.', key, bucket)
            raise
        self.logger.info("Loaded S3 object {}".format(key))
        return s3_object

    def _extract_image_properties(self, s3_key: str, s3_object: Any) -> ImageProperties:
        try:
            file = BytesIO(s3_object['Body'].read())
            image = PIL.Image.open(file)
        except Exception as e:
            self.logger.exception('Unable to Open file %s as Image', s3_key)
            raise
        self.logger.info("Opened image {} locally".format(s3_key) )

        image_properties = ImageProperties(
            name=s3_key.split("/")[-1],
            size= s3_object['ContentLength'],
            mime= s3_object['ContentType'],
            width=image.size[0],
            height=image.size[1])

        self.logger.info(str(image_properties))
        return image_properties

    def _create_table_entry(self, id: str, image: ImageProperties) -> TableEntry:
        table_entry = TableEntry(
            image_id = id,
            file_name = image.name,
            file_size = image.size,
            file_type = image.mime,
            image_width = image.width,
            image_height = image.height,
            timestamp = str(time.time()))

        self.logger.info(str(table_entry))
        return table_entry

    def _write_insert_statement(self, table_entry: TableEntry, table_name: str) -> str:
        sql = '''INSERT INTO {} VALUES({}, {}, {}, {}, {}, {}, {})'''.format(
            table_name,
            table_entry.image_id,
            table_entry.file_name,
            table_entry.file_size,
            table_entry.file_type,
            table_entry.image_width,
            table_entry.image_height,
            table_entry.timestamp
        )
        self.logger.info("Created MySQL insert query: \n{}".format(sql))
        return sql

    def _establish_rds_connection(self):
        self.logger.info("Creating rds connection with configs: {}".format(str(self.rds_configs)))
        token = self.rds_client.generate_db_auth_token(
            DBHostname=self.rds_configs["proxy_host_name"],
            Port=self.rds_configs["port"],
            DBUsername=self.rds_configs["db_user_name"],
            Region=self.rds_configs["aws_region"],
        )
        try:
            connection = pymysql.connect(
                host=self.rds_configs["proxy_host_name"],
                user=self.rds_configs["db_user_name"],
                password=token,
                db=self.rds_configs["db_name"],
                port=self.rds_configs["port"],
                #ssl={'ca': 'Amazon RDS'} 
            )
            self.logger.info("Connected to {}".format(self.rds_configs["db_name"]))
            return connection
        except Exception as e:
            self.logger.exception('Unable to Establish Database Connection')
            raise

    def _execute_insert_statement(self, connection: Any, statement: str) -> None:
        cursor = connection.cursor()
        try:
            cursor.execute(statement)
            connection.commit()
            self.logger.warning("%d rows inserted", cursor.rowcount)
        except Exception as e:
            self.logger.exception("failed to insert values")
        finally:
            cursor.close()

    def handle(self, event):
        bucket, key = self._parse_event(event)
        s3_object = self._get_s3_object(bucket, key)
        image = self._extract_image_properties(key, s3_object)
        table_entry =self. _create_table_entry(bucket + '/' + key, image)
        insert_statement = self._write_insert_statement(table_entry, self.rds_configs['table_name'])
        connection = self._establish_rds_connection()
        self._execute_insert_statement(connection, insert_statement)
