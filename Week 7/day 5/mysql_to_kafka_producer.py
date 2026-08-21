import mysql.connector
from kafka import KafkaProducer
import json

conn = mysql.connector.connect(
    host='localhost',
    user='training',
    password='training',
    database='marvel_db',
    charset='utf8'
)

cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT * FROM characters")
rows = cursor.fetchall()

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

for row in rows:
    producer.send('mysql-topic', value=row)

producer.flush()
print("Datos de Marvel Rivals enviados a Kafka.")

