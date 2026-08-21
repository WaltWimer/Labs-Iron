from kafka import KafkaConsumer
from hdfs import InsecureClient
import json

hdfs_client = InsecureClient('http://localhost:50070', user='training')

consumer = KafkaConsumer(
    'mysql-topic',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    group_id='marvel-hdfs-group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

hdfs_path = '/user/training/marvel_rivals_data.json'

with hdfs_client.write(hdfs_path, encoding='utf-8', overwrite=True) as writer:
    for message in consumer:
        json_record = json.dumps(message.value)
        writer.write(json_record + '\n')
        
print("Datos de Marvel Rivals guardados en HDFS.")
