from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers='localhost:9092')
filename = '/home/training/Documents/A4document.pdf'

with open(filename, 'rb') as file:
    file_data = file.read()

producer.send('pdf-topic', value=file_data)
producer.flush()
print('PDF sent successfully')
