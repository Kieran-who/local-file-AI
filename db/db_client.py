from config import AZURE_OPENAI_KEY, AZURE_STORAGE_CONNECTION_STRING, AZURE_CONTAINER_NAME, INDEX_MACHINE
import weaviate
from weaviate.embedded import EmbeddedOptions
from .backup import restore_backup
from .classes import weav_classes
import time
import copy
import logging

# Get the logger for the module
logger = logging.getLogger('weaviate')

# Set the level to ERROR
logger.setLevel(logging.ERROR)

weav_classes_to_check = copy.deepcopy(weav_classes)


async def add_prop(client, class_name, prop):
    # Add any new properties to the schema
    client.schema.property.create(class_name, prop)

# check if all defined properties in the schema are in the db classes


async def check_properties(client):
    weav_classes_test = weav_classes["classes"]
    test_classes = client.schema.get()["classes"]
    # Create dictionaries for weav_classes and test_classes
    weav_dict = {
        weav_class['class']: {
            prop['name']: prop for prop in weav_class.get('properties', [])
        } for weav_class in weav_classes_test
    }
    test_dict = {
        test_class['class']: set(prop['name'] for prop in test_class.get('properties', [])) for test_class in test_classes
    }
    for weav_class, weav_props in weav_dict.items():
        for weav_prop_name, weav_prop in weav_props.items():
            if weav_class not in test_dict or weav_prop_name not in test_dict[weav_class]:
                await add_prop(client, weav_class, weav_prop)


async def setup_classes(client):
    test_classes = client.schema.get()["classes"]
    for class_obj in weav_classes_to_check["classes"]:
        class_name = class_obj["class"]
        if not any(obj["class"] == class_name for obj in test_classes):
            # delete the cross-ref properties on first run to remove errors from cross referencing non-established classes
            if not test_classes:
                for propertie in class_obj["properties"]:
                    if propertie["dataType"][0] in [obj["class"] for obj in weav_classes_to_check["classes"]]:
                        class_obj["properties"].remove(propertie)
            client.schema.create_class(class_obj)
    # ensures all schema properties are up to date
    await check_properties(client)
    return


async def client_start():
    client = weaviate.Client(
        embedded_options=EmbeddedOptions(
            persistence_data_path="./db/data",
            additional_env_vars={
                "ENABLE_MODULES": "backup-azure",
                "BACKUP_AZURE_CONTAINER": AZURE_CONTAINER_NAME,
                "AZURE_STORAGE_CONNECTION_STRING": AZURE_STORAGE_CONNECTION_STRING,
                "AZURE_APIKEY": AZURE_OPENAI_KEY,
                "LOG_FORMAT": "text"
            }

        )
    )
    # Creates the schema if it doesn't exist
    await setup_classes(client)

    return client


async def weav_setup():
    client = await client_start()
    if not INDEX_MACHINE:
        print("Ensuring all data is up to date")
        await restore_backup(client)
        print("All data is now up to date")
    return client
