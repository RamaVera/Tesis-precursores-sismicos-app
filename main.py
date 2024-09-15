import paho.mqtt.client as mqtt
import dearpygui.dearpygui as dpg
from screeninfo import get_monitors
from datetime import datetime, timedelta
import traceback
import struct
import re
import ssl
import time
import shutil
from paho.mqtt import client as mqtt_client
import os

# Definir constantes para los tags de los widgets
TAG_YEAR_INPUT_START = "year_input_start"
TAG_MONTH_INPUT_START = "month_input_start"
TAG_DAY_INPUT_START = "day_input_start"
TAG_HOUR_INPUT_START = "hour_input_start"
TAG_MINUTE_INPUT_START = "minute_input_start"

TAG_YEAR_INPUT_END = "year_input_end"
TAG_MONTH_INPUT_END = "month_input_end"
TAG_DAY_INPUT_END = "day_input_end"
TAG_HOUR_INPUT_END = "hour_input_end"
TAG_MINUTE_INPUT_END = "minute_input_end"

TAG_DURATION_HOUR_INPUT = "duration_hour_input"
TAG_DURATION_MINUTE_INPUT = "duration_minute_input"

TAG_YEAR_INPUT_START_DUR = "year_input_start_dur"
TAG_MONTH_INPUT_START_DUR = "month_input_start_dur"
TAG_DAY_INPUT_START_DUR = "day_input_start_dur"
TAG_HOUR_INPUT_START_DUR = "hour_input_start_dur"
TAG_MINUTE_INPUT_START_DUR = "minute_input_start_dur"

TAG_MQTT_BROKER = "mqtt_broker"
TAG_MQTT_PORT = "mqtt_port"
TAG_MQTT_USER = "mqtt_user"
TAG_MQTT_PASS = "mqtt_pass"

TAG_SD_PATH = "sd_path"

TAG_ESP_SD_WIFI = "esp_sd_wifi"
TAG_ESP_SD_WIFI_PASS = "esp_sd_wifi_pass"
TAG_ESP_SD_MQTT_BROKER = "esp_sd_mqtt_broker"
TAG_ESP_SD_MQTT_PORT = "esp_sd_mqtt_port"
TAG_ESP_SD_MQTT_USER = "esp_sd_mqtt_user"
TAG_ESP_SD_MQTT_PASSWORD = "esp_sd_mqtt_password"
TAG_ESP_SD_OFFLINE_YEAR = "esp_sd_offline_year"
TAG_ESP_SD_OFFLINE_MONTH = "esp_sd_offline_month"
TAG_ESP_SD_OFFLINE_DAY = "esp_sd_offline_day"

TAG_ESP_SD_SAME_BROKER = "esp32_same_broker"

# Identificadores de los inputs
year_input_start, month_input_start, day_input_start, hour_input_start, minute_input_start = "", "", "", "", ""
year_input_end, month_input_end, day_input_end, hour_input_end, minute_input_end = "", "", "", "", ""
duration_hour_input, duration_minute_input = "", ""
broker_state_label, commands_table, config_state, config_table= "", "", "", ""
mqtt_broker, mqtt_port, mqtt_user, mqtt_pass = "", "", "", ""
sd_path = ""
esp32_wifi_name, esp32_wifi_pass, esp32_broker, esp32_port, esp32_usr, esp32_pass, esp32_year_offline, esp32_month_offline, esp32_day_offline = "", "", "", "", "", "", "", "", ""

# Configuración del broker MQTT
# MQTT_BROKER = "broker.emqx.io"
# MQTT_PORT = 1883
default_mqtt_broker = "7456a1a52e1e4483b09a0fd1fd8e7ead.s1.eu.hivemq.cloud"
default_mqtt_port = 8883
default_mqtt_user = "Ramiro"
default_mqtt_password = "Ramiro99"
default_sd_path = "E:\\"


# Temas MQTT
TOPIC_COMMAND = "tesis/commands"
TOPIC_RESPONSE = "tesis/data"

# Cliente MQTT
mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id="myPy", protocol=mqtt.MQTTv5)

def main():
    global year_input_start, month_input_start, day_input_start, hour_input_start, minute_input_start
    global year_input_end, month_input_end, day_input_end, hour_input_end, minute_input_end
    global duration_hour_input, duration_minute_input
    global broker_state_label, commands_table, config_state, config_table
    global mqtt_broker, mqtt_port, mqtt_user, mqtt_pass
    global sd_path
    global esp32_wifi_name, esp32_wifi_pass, esp32_broker, esp32_port, esp32_usr, esp32_pass, esp32_year_offline, esp32_month_offline, esp32_day_offline

    # Obtener el tamaño de la pantalla
    monitor = get_monitors()[0]
    screen_width, screen_height = monitor.width, monitor.height

    # Tamaño de la ventana
    window_width, window_height = 900, 600

    # Calcular la posición para centrar la ventana
    pos_x = int((screen_width - window_width) / 2)
    pos_y = int((screen_height - window_height) / 2)

    dpg.create_context()

    with dpg.window(label="Tesis Precursores Sismicos", width=window_width + 20, height=window_height + 60):
        dpg.add_tab_bar()
        with dpg.tab_bar():
            with dpg.tab(label="Configurar SD"):
                # Widget para ingresar fechas (ARRIBA IZQUIERDA)
                with dpg.child_window(width=window_width // 1 - 10, height=window_height // 4 - 10):
                    dpg.add_text("Conexion al SD")
                    with dpg.group(horizontal=True):
                        dpg.add_text("Ruta SD")
                        sd_path = dpg.add_input_text(width=400, hint=default_sd_path, tag=TAG_SD_PATH)

                    dpg.add_button(label="Conectar", callback=connect_to_sd)
                    config_state = dpg.add_text("Desconectado", color=[0, 0, 255])

                # Tabla para comandos ingresados (ABAJO IZQUIERDA)
                with dpg.child_window(width=window_width // 1 - 10, height=window_height // 3 - 10):
                    dpg.add_text("Configuracion activas")
                    with dpg.table(header_row=True, resizable=True, policy=dpg.mvTable_SizingFixedFit) as config_table:
                        create_sd_config_table()

                with dpg.child_window(width=window_width // 1 - 10, height=window_height // 3 - 10):
                    dpg.add_text("Crear nueva configuracion")
                    with dpg.group(horizontal=True):
                        with dpg.group():
                            with dpg.group(horizontal=True):
                                dpg.add_text("Wifi Red")
                                esp32_wifi_name = dpg.add_input_text(label="", width=75, hint="", tag=TAG_ESP_SD_WIFI)
                            with dpg.group(horizontal=True):
                                dpg.add_text("Wifi Password")
                                esp32_wifi_pass = dpg.add_input_text(label="", width=75, hint="", tag=TAG_ESP_SD_WIFI_PASS)
                            dpg.add_text("")
                            with dpg.group(horizontal=True):
                                dpg.add_text("Offline Year")
                                esp32_year_offline = dpg.add_input_text(label="", width=25, hint="", tag=TAG_ESP_SD_OFFLINE_YEAR)
                            with dpg.group(horizontal=True):
                                dpg.add_text("Offline Month")
                                esp32_month_offline = dpg.add_input_text(label="", width=25, hint="", tag=TAG_ESP_SD_OFFLINE_MONTH)
                            with dpg.group(horizontal=True):
                                dpg.add_text("Offline Day")
                                esp32_day_offline = dpg.add_input_text(label="", width=25, hint="", tag=TAG_ESP_SD_OFFLINE_DAY)

                        with dpg.group():
                            with dpg.group(horizontal=True):
                                dpg.add_text("MQTT Broker")
                                esp32_broker = dpg.add_input_text(label="", width=200, hint=default_mqtt_broker, tag=TAG_ESP_SD_MQTT_BROKER)
                            with dpg.group(horizontal=True):
                                dpg.add_text("MQTT User")
                                esp32_usr = dpg.add_input_text(label="", width=200, hint=default_mqtt_user, tag=TAG_ESP_SD_MQTT_USER)
                            with dpg.group(horizontal=True):
                                dpg.add_text("MQTT Password")
                                esp32_pass = dpg.add_input_text(label="", width=200, hint=default_mqtt_password, tag=TAG_ESP_SD_MQTT_PASSWORD)
                            with dpg.group(horizontal=True):
                                dpg.add_text("MQTT Port")
                                esp32_port = dpg.add_input_text(label="", width=200, hint=str(default_mqtt_port), tag=TAG_ESP_SD_MQTT_PORT)
                            dpg.add_text("Usar misma configuracion del broker")
                            with dpg.group(horizontal=True):
                                dpg.add_text("(requiere conexion previa)")
                                dpg.add_checkbox(label="", default_value=False, callback=same_as_broker, tag=TAG_ESP_SD_SAME_BROKER)

                        with dpg.group():
                            dpg.add_button(label="Guardar configuracion", callback=save_config)


            with dpg.tab(label="Configuracion Broker"):
                # Configurar el layout de la ventana de conexión
                with dpg.child_window(width=window_width // 1 - 10, height=window_height // 1 - 10):
                    dpg.add_text("Conexion al Broker")
                    with dpg.group(horizontal=True):
                        dpg.add_text("Broker")
                        mqtt_broker = dpg.add_input_text(width=400, hint=default_mqtt_broker, tag=TAG_MQTT_BROKER)

                        dpg.add_text("- Puerto")
                        mqtt_port = dpg.add_input_text(width=50, hint=str(default_mqtt_port), tag=TAG_MQTT_PORT)

                    with dpg.group(horizontal=True):
                        dpg.add_text("Usuario")
                        mqtt_user = dpg.add_input_text(width=100, hint=default_mqtt_user , tag=TAG_MQTT_USER)

                    with dpg.group(horizontal=True):
                        dpg.add_text("Contraseña")
                        mqtt_pass = dpg.add_input_text(width=100, hint= default_mqtt_password, tag=TAG_MQTT_PASS)

                    dpg.add_button(label="Conectar", callback=connect_to_broker)
                    broker_state_label = dpg.add_text("Desconectado", color=[0, 0, 255])

            with dpg.tab(label="Comandos"):
                # Configurar el layout de la ventana de comandos
                with dpg.group(horizontal=True):
                    with dpg.group():
                        # Widget para ingresar fechas (ARRIBA IZQUIERDA)
                        with dpg.child_window(width=window_width // 2 - 10, height=window_height // 2 - 10):
                            dpg.add_text("Ingrese Fecha para obtener datos")
                            dpg.add_tab_bar()
                            with dpg.tab_bar():
                                with dpg.tab(label="Inicio y Fin"):
                                    dpg.add_text("Fecha y hora Inicio:")
                                    with dpg.group(horizontal=True):
                                        year_input_start = dpg.add_input_text(label="-", width=35, hint="YYYY", tag=TAG_YEAR_INPUT_START)
                                        month_input_start = dpg.add_input_text(label="-", width=25, hint="MM", tag=TAG_MONTH_INPUT_START)
                                        day_input_start = dpg.add_input_text(label="-", width=25, hint="DD", tag=TAG_DAY_INPUT_START)
                                        hour_input_start = dpg.add_input_text(label=":", width=25, hint="HH", tag=TAG_HOUR_INPUT_START)
                                        minute_input_start = dpg.add_input_text(label="", width=25, hint="MM", tag=TAG_MINUTE_INPUT_START)

                                    dpg.add_text("Fecha y hora Fin:")
                                    with dpg.group(horizontal=True):
                                        year_input_end = dpg.add_input_text(label="-", width=35, hint="YYYY", tag=TAG_YEAR_INPUT_END)
                                        month_input_end = dpg.add_input_text(label="-", width=25, hint="MM", tag=TAG_MONTH_INPUT_END)
                                        day_input_end = dpg.add_input_text(label="-", width=25, hint="DD", tag=TAG_DAY_INPUT_END)
                                        hour_input_end = dpg.add_input_text(label=":", width=25, hint="HH", tag=TAG_HOUR_INPUT_END)
                                        minute_input_end = dpg.add_input_text(label="", width=25, hint="MM", tag=TAG_MINUTE_INPUT_END)

                                    dpg.add_button(label="Enviar", callback=send_command_by_init_end)

                                with dpg.tab(label="Inicio y Duración"):
                                    dpg.add_text("Fecha y hora Inicio:")
                                    with dpg.group(horizontal=True):
                                        year_input_start = dpg.add_input_text(label="-", width=35, hint="YYYY", tag=TAG_YEAR_INPUT_START_DUR)
                                        month_input_start = dpg.add_input_text(label="-", width=25, hint="MM", tag=TAG_MONTH_INPUT_START_DUR)
                                        day_input_start = dpg.add_input_text(label="-", width=25, hint="DD", tag=TAG_DAY_INPUT_START_DUR)
                                        hour_input_start = dpg.add_input_text(label=":", width=25, hint="HH", tag=TAG_HOUR_INPUT_START_DUR)
                                        minute_input_start = dpg.add_input_text(label="", width=25, hint="MM", tag=TAG_MINUTE_INPUT_START_DUR)

                                    dpg.add_text("Duracion:")
                                    with dpg.group(horizontal=True):
                                        duration_hour_input = dpg.add_input_text(label=":", width=25, hint="HH", tag=TAG_DURATION_HOUR_INPUT)
                                        duration_minute_input = dpg.add_input_text(label="", width=25, hint="MM", tag=TAG_DURATION_MINUTE_INPUT)

                                    dpg.add_button(label="Enviar", callback=send_command_by_init_duration)

                        # Tabla para comandos ingresados (ABAJO IZQUIERDA)
                        with dpg.child_window(width=window_width // 2 - 10, height=window_height // 2 - 10):
                            dpg.add_text("Comandos Ingresados")
                            with dpg.table(header_row=True, resizable=True, policy=dpg.mvTable_SizingFixedFit) as commands_table:
                                dpg.add_table_column(label="Fecha y Hora", width_fixed=False, init_width_or_weight=130)
                                dpg.add_table_column(label="Fecha Inicio",width_fixed=True, init_width_or_weight=110)
                                dpg.add_table_column(label="Fecha Fin", width_fixed=True, init_width_or_weight=110)

                    with dpg.group():
                        # Gráfico vacío (ARRIBA DERECHA)
                        with dpg.child_window(width=window_width // 2 - 10, height=window_height // 3 - 10):
                            dpg.add_text("Gráfico de Broker")
                            dpg.add_plot(label="Datos del Broker eje x", height=-1)

                        # Gráfico vacío (ARRIBA DERECHA)
                        with dpg.child_window(width=window_width // 2 - 10, height=window_height // 3 - 10):
                            dpg.add_text("Gráfico de Broker")
                            dpg.add_plot(label="Datos del Broker eje y", height=-1)

                        # Gráfico vacío (ARRIBA DERECHA)
                        with dpg.child_window(width=window_width // 2 - 10, height=window_height // 3 - 10):
                            dpg.add_text("Gráfico de Broker")
                            dpg.add_plot(label="Datos del Broker eje z", height=-1)



    dpg.create_viewport(title='Tesis Precursores Sismicos', width=window_width + 35, height=window_height + 100)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_viewport_pos([pos_x, pos_y - 50])
    dpg.start_dearpygui()
    dpg.destroy_context()


def create_sd_config_table():
    dpg.add_table_column(label="Estado", width_fixed=False, init_width_or_weight=65)
    dpg.add_table_column(label="Wifi Red", width_fixed=False, init_width_or_weight=65)
    dpg.add_table_column(label="Wifi Pass", width_fixed=True, init_width_or_weight=65)
    dpg.add_table_column(label="MQTT Broker", width_fixed=True, init_width_or_weight=80)
    dpg.add_table_column(label="MQTT User", width_fixed=True, init_width_or_weight=65)
    dpg.add_table_column(label="MQTT Pass", width_fixed=True, init_width_or_weight=65)
    dpg.add_table_column(label="MQTT Port", width_fixed=True, init_width_or_weight=65)
    dpg.add_table_column(label="Año Offline", width_fixed=True, init_width_or_weight=80)
    dpg.add_table_column(label="Mes Offline", width_fixed=True, init_width_or_weight=80)
    dpg.add_table_column(label="Dia Offline", width_fixed=True, init_width_or_weight=80)


# Función para ejecutar el comando y registrar en la tabla
def send_command_by_init_end(sender, app_data, user_data):
    try:
        start_datetime = user_input_to_datetime(TAG_YEAR_INPUT_START, TAG_MONTH_INPUT_START, TAG_DAY_INPUT_START, TAG_HOUR_INPUT_START, TAG_MINUTE_INPUT_START)
        end_datetime = user_input_to_datetime(TAG_YEAR_INPUT_END, TAG_MONTH_INPUT_END, TAG_DAY_INPUT_END, TAG_HOUR_INPUT_END, TAG_MINUTE_INPUT_END)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_date = start_datetime.strftime("%Y-%m-%d %H:%M:%S")
        end_date = end_datetime.strftime("%Y-%m-%d %H:%M:%S")

        # Agregar el comando a la tabla
        with dpg.table_row(parent=commands_table):
            dpg.add_text(now)
            dpg.add_text(start_date)
            dpg.add_text(end_date)

        print(f"Comando ejecutado: Fecha Inicio: {start_date}, Fecha Fin: {end_date}")
        publish_command(TOPIC_COMMAND, to_command(end_datetime, start_datetime))
    except ValueError as ve:
        print(f"Error: {ve}")
        print(traceback.format_exc())
    except Exception as e:
        print(f"Se produjo un error: {e}")
        print(traceback.format_exc())

def send_command_by_init_duration(sender, app_data, user_data):
    try:
        start_datetime = user_input_to_datetime(TAG_YEAR_INPUT_START_DUR, TAG_MONTH_INPUT_START_DUR, TAG_DAY_INPUT_START_DUR, TAG_HOUR_INPUT_START_DUR, TAG_MINUTE_INPUT_START_DUR)

        duration_hours = dpg.get_value(TAG_DURATION_HOUR_INPUT)
        duration_minutes = dpg.get_value(TAG_DURATION_MINUTE_INPUT)

        if not duration_hours or not duration_minutes:
            raise ValueError("Todos los campos de duración deben estar completos.")

        duration_hours = int(duration_hours)
        duration_minutes = int(duration_minutes)

        # Sumar la duración al datetime de inicio
        end_datetime = start_datetime + timedelta(hours=duration_hours, minutes=duration_minutes)

        start_date = start_datetime.strftime("%Y-%m-%d %H:%M:%S")
        end_date = end_datetime.strftime("%Y-%m-%d %H:%M:%S")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Agregar el comando a la tabla
        with dpg.table_row(parent=commands_table):
            dpg.add_text(now)
            dpg.add_text(start_date)
            dpg.add_text(end_date)

        print(f"Comando ejecutado: Fecha Inicio: {start_datetime}, Fecha Fin: {end_date}")
        publish_command(TOPIC_COMMAND, to_command(end_datetime, start_datetime))
    except ValueError as ve:
        print(f"Error: {ve}")
        print(traceback.format_exc())
    except Exception as e:
        print(f"Se produjo un error: {e}")
        print(traceback.format_exc())

def user_input_to_datetime(year_input, month_input, day_input, hour_input, minute_input):
    year = dpg.get_value(year_input)
    month = dpg.get_value(month_input)
    day = dpg.get_value(day_input)
    hour = dpg.get_value(hour_input)
    minute = dpg.get_value(minute_input)
    print(f"Valores obtenidos: year={year}, month={month}, day={day}, hour={hour}, minute={minute}")
    if not year or not month or not day or not hour or not minute:
        raise ValueError("Todos los campos de fecha y hora deben estar completos para la fecha de inicio.")
    year = int(year)
    month = int(month)
    day = int(day)
    hour = int(hour)
    minute = int(minute)
    start_datetime = datetime(year, month, day, hour, minute)
    return start_datetime

def to_command(end_datetime, start_datetime):
    command_to_send = f"R {start_datetime.year}-{start_datetime.month}-{start_datetime.day}-{start_datetime.hour}-{start_datetime.minute}-{end_datetime.year}-{end_datetime.month}-{end_datetime.day}-{end_datetime.hour}-{end_datetime.minute}"
    return command_to_send

def publish_command(topic, message):
    from paho.mqtt.properties import Properties
    from paho.mqtt.packettypes import PacketTypes
    properties = Properties(PacketTypes.PUBLISH)
    properties.MessageExpiryInterval = 30  # in seconds

    mqtt_client.publish(topic, message, 0, properties=properties);

def connect_to_sd(sender, app_data, user_data):
    sd = dpg.get_value(TAG_SD_PATH)
    if sd == "":
        sd = default_sd_path

    try:
        config_files = [f for f in os.listdir(sd) if f.endswith('.txt')]
        for file in config_files:
            with open(os.path.join(sd, file), 'r') as f:
                dpg.set_value(config_state, "SD encontrada")
                dpg.configure_item(config_state, color=[0, 255, 0])
                line = f.readline().strip()
                data = line.split(' | ')
                with dpg.table_row(parent=config_table):
                    # Determinar el estado del archivo y agregarlo como el primer elemento en la fila
                    file_status = "Inactive" if file.endswith('.old.txt') else "Active"
                    dpg.add_text(file_status)
                    for item in data:
                        dpg.add_text(item)

    except Exception as e:
        dpg.set_value(config_state, "SD no encontrada")
        dpg.configure_item(config_state, color=[255, 0, 0])
        print(f"Se produjo un error al conectar: {e}")
        print(traceback.format_exc())
        print(f"SD: {sd}")

def same_as_broker(sender, app_data, user_data):
    if dpg.get_value(TAG_ESP_SD_SAME_BROKER):
        dpg.set_value(TAG_ESP_SD_MQTT_BROKER, dpg.get_value(TAG_MQTT_BROKER))
        dpg.set_value(TAG_ESP_SD_MQTT_USER, dpg.get_value(TAG_MQTT_USER))
        dpg.set_value(TAG_ESP_SD_MQTT_PASSWORD, dpg.get_value(TAG_MQTT_PASS))
        dpg.set_value(TAG_ESP_SD_MQTT_PORT, dpg.get_value(TAG_MQTT_PORT))

def save_config(sender, app_data, user_data):
    global config_table
    sd = dpg.get_value(TAG_SD_PATH)
    if sd == "":
        sd = default_sd_path

    try:
        # Obtén la fecha de creación del archivo
        if os.path.exists(os.path.join(sd, "config.txt")):
            creation_time = os.path.getctime(os.path.join(sd, 'config.txt'))
            creation_date = time.strftime('%Y-%m-%d', time.localtime(creation_time))

            # Renombra el archivo
            old_file_name = f"config-{creation_date}.old.txt"
            # if exist old file, add a number to the end of date
            if os.path.exists(os.path.join(sd, old_file_name)):
                i = 1
                while os.path.exists(os.path.join(sd, f"config-{creation_date}-{i}.old.txt")):
                    i += 1
                old_file_name = f"config-{creation_date}-{i}.old.txt"

            shutil.move(os.path.join(sd, 'config.txt'), os.path.join(sd, old_file_name))

        same_as_broker(sender, app_data, user_data)

        # Crea un nuevo archivo con nuevos parámetros
        new_params = f"{dpg.get_value(TAG_ESP_SD_WIFI)} | " \
                     f"{dpg.get_value(TAG_ESP_SD_WIFI_PASS)} | " \
                     f"{dpg.get_value(TAG_ESP_SD_MQTT_BROKER)} | " \
                     f"{dpg.get_value(TAG_ESP_SD_MQTT_USER)} | " \
                     f"{dpg.get_value(TAG_ESP_SD_MQTT_PASSWORD)} | " \
                     f"{dpg.get_value(TAG_ESP_SD_MQTT_PORT)} | " \
                     f"{dpg.get_value(TAG_ESP_SD_OFFLINE_YEAR)} | " \
                     f"{dpg.get_value(TAG_ESP_SD_OFFLINE_MONTH)} | " \
                     f"{dpg.get_value(TAG_ESP_SD_OFFLINE_DAY)}"

        with open(os.path.join(sd, 'config.txt'), 'w') as f:
            f.write(new_params)

        # Almacena el ID del contenedor padre
        parent_id = dpg.get_item_parent(config_table)

        # Primero, elimina la tabla
        dpg.delete_item(config_table)
        # Luego, vuelve a crear la tabla en el mismo contenedor padre
        with dpg.table(header_row=True, resizable=True, policy=dpg.mvTable_SizingFixedFit, parent=parent_id) as config_table:
            create_sd_config_table()
        connect_to_sd(sender, app_data, user_data)

    except Exception as e:
        dpg.set_value(config_state, "SD no encontrada")
        dpg.configure_item(config_state, color=[255, 0, 0])
        print(f"Se produjo un error al conectar: {e}")
        print(traceback.format_exc())
        print(f"SD: {sd}")

def connect_to_broker(sender, app_data, user_data):
    usr = dpg.get_value(TAG_MQTT_USER)
    if usr == "":
        usr = default_mqtt_user
        dpg.set_value(TAG_MQTT_USER, usr)
    password = dpg.get_value(TAG_MQTT_PASS)
    if password == "":
        password = default_mqtt_password
        dpg.set_value(TAG_MQTT_PASS, password)
    broker = dpg.get_value(TAG_MQTT_BROKER)
    if broker == "":
        broker = default_mqtt_broker
        dpg.set_value(TAG_MQTT_BROKER, broker)
    port = dpg.get_value(TAG_MQTT_PORT)
    if port == "":
        port = default_mqtt_port
        dpg.set_value(TAG_MQTT_PORT, port)

    try:
        mqtt_client.on_message = on_message
        mqtt_client.on_connect = on_connect
        mqtt_client.on_subscribe = on_subscribe

        from paho.mqtt.properties import Properties
        from paho.mqtt.packettypes import PacketTypes
        properties = Properties(PacketTypes.CONNECT)
        properties.SessionExpiryInterval = 30 * 60  # in seconds

        # enable TLS for secure connection
        mqtt_client.tls_set(tls_version=ssl.PROTOCOL_TLS)        # set username and password
        mqtt_client.username_pw_set(usr, password)
        mqtt_client.connect(broker,
                            port,
                            clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY,
                            properties=properties,
                            keepalive=60)

        mqtt_client.loop_start()

    except Exception as e:
        print(f"Se produjo un error al conectar: {e}")
        print(traceback.format_exc())
        print(f"Broker: {broker}")
        print(f"Port: {port}")
        print(f"User: {usr}")
        print(f"Password: {password}")

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Conexión con reason: {reason_code} - flags: {flags} y properties: {properties}")
    if reason_code == "Success":
        # Configurar la interfaz de usuario para indicar la conexión exitosa
        dpg.set_value(broker_state_label, "Conectado")
        dpg.configure_item(broker_state_label, color=[0, 255, 0])

        print("Conexión exitosa")
        mqtt_client.subscribe(TOPIC_RESPONSE)
    else:
        # Configurar la interfaz de usuario para indicar la conexión exitosa
        dpg.set_value(broker_state_label, "Error al conectarse")
        dpg.configure_item(broker_state_label, color=[255, 0, 0])
        print(f"Error al conectar: {reason_code}")

def on_message(client, userdata, message):
    msg = message.payload.decode("utf-8")
    decode_message(msg)

def decode_message(messages):
    if "error" in messages:
        print("Se detectó un error de lectura.")
    else:
        match = re.search(r'(\d{2}):(\d{2})', messages)
        if match:
            hour, minute = map(int, match.groups())
            print(f"Hora: {hour}, Minuto: {minute}")
        else:
            # Abre el archivo en modo de escritura
            with open('sensor_data.txt', 'a') as file:
                # Supongamos que 'messages' es una lista de tus mensajes
                sensor_data = messages.split("\n")
                for msg in sensor_data:
                    # Verifica si el mensaje contiene el carácter "|"
                    if "|" in msg:
                        # Divide el mensaje en el número de muestra y los datos del sensor
                        sample_number, sensor_data = msg.split("|")

                        # Convierte la cadena hexadecimal en bytes
                        data_bytes = bytes.fromhex(sensor_data.strip())

                        # Desempaqueta los datos
                        mpu_accelX, mpu_accelY, mpu_accelZ, adc_adcX, adc_adcY, adc_adcZ = struct.unpack('HHHHHH', data_bytes)

                        # Ahora puedes usar estos valores para recrear tus estructuras
                        mpu_data = {'accelX': mpu_accelX, 'accelY': mpu_accelY, 'accelZ': mpu_accelZ}
                        adc_data = {'adcX': adc_adcX, 'adcY': adc_adcY, 'adcZ': adc_adcZ}
                        sd_data = {'mpuData': mpu_data, 'adcData': adc_data}

                        # Escribe los datos en el archivo
                        file.write(f"Sample {sample_number}: {sd_data}\n")

def on_subscribe(client, userdata, mid, reason_codes, properties):
    print(f"Suscripción con reason: {reason_codes} - mid {mid} y properties: {properties}")
    if mid == 1:
        print("Suscripción exitosa")
    # Any reason code >= 128 is a failure.
    if mid >= 128:
        print(f"Error al suscribirse: {reason_codes}")

if __name__ == "__main__":
    main()
