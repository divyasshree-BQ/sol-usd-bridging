# This code displays latest trades on Solana 

import uuid
import base58
from confluent_kafka import Consumer, KafkaError, KafkaException
from google.protobuf.message import DecodeError
from google.protobuf.descriptor import FieldDescriptor
from solana import parsed_idl_block_message_pb2
from solana import dex_block_message_pb2
import config
from bridge import bridge_trade_prices
from convert import convert_bytes
# This script consumes messages from a Bitquery Kafka topic and prints the contents of the messages in a human-readable format.
# Kafka consumer configuration

group_id_suffix = uuid.uuid4().hex
print(f"Group ID Suffix: {group_id_suffix}")
conf = {
    'bootstrap.servers': 'rpk0.bitquery.io:9092,rpk1.bitquery.io:9092,rpk2.bitquery.io:9092',
    'group.id': f'solana_105-group-{group_id_suffix}',  
    'session.timeout.ms': 30000,
    'security.protocol': 'SASL_PLAINTEXT',
    'ssl.endpoint.identification.algorithm': 'none',
    'sasl.mechanisms': 'SCRAM-SHA-512',
    'sasl.username': config.solana_username,
    'sasl.password': config.solana_password,
    'auto.offset.reset': 'latest',
}

consumer = Consumer(conf)
topic = 'solana.dextrades.proto'
consumer.subscribe([topic])

# ---  recursive traversal and print --- #



def print_protobuf_message(msg, indent=0, encoding='base58'):
    prefix = ' ' * indent
    for field in msg.DESCRIPTOR.fields:
        value = getattr(msg, field.name)

        if field.label == FieldDescriptor.LABEL_REPEATED: # The field is a repeated (i.e. array/list) field.
            if not value:
                continue
            print(f"{prefix}{field.name} (repeated):")
            for idx, item in enumerate(value):
                if field.type == FieldDescriptor.TYPE_MESSAGE: # The field is a nested protobuf message.
                    print(f"{prefix}  [{idx}]:")
                    print_protobuf_message(item, indent + 4, encoding)
                elif field.type == FieldDescriptor.TYPE_BYTES:
                    print(f"{prefix}  [{idx}]: {convert_bytes(item, encoding)}")
                else:
                    print(f"{prefix}  [{idx}]: {item}")

        elif field.type == FieldDescriptor.TYPE_MESSAGE:
            if msg.HasField(field.name):
                print(f"{prefix}{field.name}:")
                print_protobuf_message(value, indent + 4, encoding)

        elif field.type == FieldDescriptor.TYPE_BYTES:
            print(f"{prefix}{field.name}: {convert_bytes(value, encoding)}")

        elif field.containing_oneof:
            if msg.WhichOneof(field.containing_oneof.name) == field.name:
                print(f"{prefix}{field.name} (oneof): {value}")

        else:
            print(f"{prefix}{field.name}: {value}")

# --- Process messages from Kafka --- #

def process_message(message):
    try:
        buffer = message.value()
        tx_block = dex_block_message_pb2.DexParsedBlockMessage()
        tx_block.ParseFromString(buffer)

        print("\nNew DexParsedBlockMessage received:\n")
        # print_protobuf_message(tx_block, encoding='base58')
        # Bridging logic
        bridge_trade_prices(tx_block)


    except DecodeError as err:
        print(f"Protobuf decoding error: {err}")
    except Exception as err:
        print(f"Error processing message: {err}")

# --- Polling loop --- #

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                raise KafkaException(msg.error())
        process_message(msg)

except KeyboardInterrupt:
    print("Stopping consumer...")

finally:
    consumer.close()