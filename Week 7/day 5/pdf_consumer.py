from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'pdf-topic',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True
)

for message in consumer:
    with open('/home/training/Desktop/received_document.pdf', 'wb') as file:
        file.write(message.value)
    print('PDF received and saved successfully')
    break
