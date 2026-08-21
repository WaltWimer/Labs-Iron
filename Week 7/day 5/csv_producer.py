from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers='localhost:9092')
filename = '/home/training/Documents/orders.csv'

with open(filename, 'rb') as file:
    file_data = file.read()

producer.send('csv-topic', value=file_data)
producer.flush()
print('CSV sent successfully')
