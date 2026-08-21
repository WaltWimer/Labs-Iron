from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers='localhost:9092')
filename = '33.jpg'
with open(filename, 'rb') as file:
    image_data = file.read()
producer.send('images', value=image_data)
producer.flush()
print('Image sent successfully')
