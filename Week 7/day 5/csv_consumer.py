from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'csv-topic',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True
)

for message in consumer:
    with open('/home/training/Desktop/received_orders.csv', 'wb') as file:
        file.write(message.value)
    print('CSV received and saved successfully')
    break
