from kafka import KafkaConsumer
consumer = KafkaConsumer(
    'images',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest'
)
for message in consumer:
    with open('received_image.jpg', 'wb') as file:
        file.write(message.value)
    print('Image received successfully')
    break



