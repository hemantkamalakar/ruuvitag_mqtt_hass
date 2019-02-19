import time
import sys
import os
from datetime import datetime
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import json
from ruuvitag_sensor.ruuvi import RuuviTagSensor
import logging.config
import yaml
import json

logger = logging.getLogger(__name__)

update_frequency_seconds = 60

def time_milliseconds():
    return int(time.time() * 1000)


def now():
    return int(time.time())

def config(config_file=None):
    # Get config from file; if no config_file is passed in as argument  default to "config.sample.yaml" in script dir
    if config_file is None:
        script_base_dir = os.path.dirname(os.path.realpath(sys.argv[0])) + "/"
        config_file = script_base_dir + "config.sample.yaml"
    with open(config_file, 'r') as stream:
        return yaml.load(stream)



payload = []
timeout_in_sec = 5


if __name__ == "__main__":
    """main"""
   
    try:
        config = config(config_file=sys.argv[1])
    except IndexError:
        config = config()

    if "home_assistant" in config:
        update_frequency_seconds = config["home_assistant"]["update_frequency_seconds"]
        mqtt_broker = config["home_assistant"]["mqtt_broker"]
        mqtt_broker_port = config["home_assistant"]["mqtt_broker_port"]

        user = config["home_assistant"]["user"]
        password = config["home_assistant"]["password"]
        topic = config["home_assistant"]["topic"]
    if "tags" in config:
        tags = config["tags"]

    if "logging" in config:
        log_config = config["logging"]
        logging.config.dictConfig(log_config)
        logger.info('Starting RuuviTag gateway.')



stamp = now()
client = mqtt.Client()
client.username_pw_set(username=user, password=password)
client.connect(mqtt_broker, mqtt_broker_port, 600)
logger.info('Connected to MQTT broker ')
while True:
    try:
        if now() - stamp > update_frequency_seconds:
            tag_data = RuuviTagSensor.get_data_for_sensors(tags.values(), timeout_in_sec)
            timestamp = time_milliseconds()
            if tag_data:
                for key, value in tag_data.items():
                    pub_topic = topic + str(key)
                    value_str = 'T: '+ str(value['temperature']) + ' H: ' + str(value['humidity']) + ' P: ' + str(value['pressure']) + ' B: ' + str(value['battery']/1000)
                    logger.info("Topic {topic} : {value}".format(topic=pub_topic, value=value_str))  
                    client.publish(pub_topic, json.dumps(value))
                time.sleep(update_frequency_seconds)
    except KeyboardInterrupt:
        print('Exit')
        break

