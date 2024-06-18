import paho.mqtt.client as mqtt
import dearpygui.dearpygui as dpg
from screeninfo import get_monitors
from datetime import datetime, timedelta
import traceback
import struct
import re

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

# Identificadores de los inputs
year_input_start, month_input_start, day_input_start, hour_input_start, minute_input_start = "", "", "", "", ""
year_input_end, month_input_end, day_input_end, hour_input_end, minute_input_end = "", "", "", "", ""
duration_hour_input, duration_minute_input = "", ""
state_label, table = "", ""

# Configuración del broker MQTT
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883

# Temas MQTT
TOPIC_COMMAND = "tesis/commands"
TOPIC_RESPONSE = "tesis/data"

# Cliente MQTT
mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id="myPy", protocol=mqtt.MQTTv5)

def main():
    global year_input_start, month_input_start, day_input_start, hour_input_start, minute_input_start
    global year_input_end, month_input_end, day_input_end, hour_input_end, minute_input_end
    global duration_hour_input, duration_minute_input
    global state_label, table

    # Obtener el tamaño de la pantalla
    monitor = get_monitors()[0]
    screen_width, screen_height = monitor.width, monitor.height

    # Tamaño de la ventana
    window_width, window_height = 800, 600

    # Calcular la posición para centrar la ventana
    pos_x = int((screen_width - window_width) / 2)
    pos_y = int((screen_height - window_height) / 2)

    dpg.create_context()

    with dpg.window(label="Tesis Precursores Sismicos", width=window_width + 20, height=window_height + 60):
        dpg.add_tab_bar()
        with dpg.tab_bar():
            with dpg.tab(label="Conexión"):
                # Configurar el layout de la ventana de conexión
                with dpg.child_window(width=window_width // 2 - 10, height=window_height // 2 - 10):
                    dpg.add_text("Conexión al Broker")
                    dpg.add_button(label="Conectar", callback=connect_to_broker)
                    state_label = dpg.add_text("Desconectado", color=[255, 0, 0])

            with dpg.tab(label="Comandos"):
                # Configurar el layout de la ventana de comandos
                with dpg.group(horizontal=True):
                    with dpg.group():
                        # Widget para ingresar fechas (ARRIBA IZQUIERDA)
                        with dpg.child_window(width=window_width // 2 - 10, height=window_height // 2 - 10):
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
                            with dpg.table(header_row=True, resizable=True, policy=dpg.mvTable_SizingFixedFit) as table:
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


# Función para ejecutar el comando y registrar en la tabla
def send_command_by_init_end(sender, app_data, user_data):
    try:
        start_datetime = user_input_to_datetime(TAG_YEAR_INPUT_START, TAG_MONTH_INPUT_START, TAG_DAY_INPUT_START, TAG_HOUR_INPUT_START, TAG_MINUTE_INPUT_START)
        end_datetime = user_input_to_datetime(TAG_YEAR_INPUT_END, TAG_MONTH_INPUT_END, TAG_DAY_INPUT_END, TAG_HOUR_INPUT_END, TAG_MINUTE_INPUT_END)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_date = start_datetime.strftime("%Y-%m-%d %H:%M:%S")
        end_date = end_datetime.strftime("%Y-%m-%d %H:%M:%S")

        # Agregar el comando a la tabla
        with dpg.table_row(parent=table):
            dpg.add_text(now)
            dpg.add_text(start_date)
            dpg.add_text(end_date)

        print(f"Comando ejecutado: Fecha Inicio: {start_date}, Fecha Fin: {end_date}")
        publish_command(TOPIC_COMMAND, ToCommand(end_datetime, start_datetime))
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
        with dpg.table_row(parent=table):
            dpg.add_text(now)
            dpg.add_text(start_date)
            dpg.add_text(end_date)

        print(f"Comando ejecutado: Fecha Inicio: {start_datetime}, Fecha Fin: {end_date}")
        publish_command(TOPIC_COMMAND, ToCommand(end_datetime, start_datetime))
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

def ToCommand(end_datetime, start_datetime):
    command_to_send = f"R {start_datetime.year}-{start_datetime.month}-{start_datetime.day}-{start_datetime.hour}-{start_datetime.minute}-{end_datetime.year}-{end_datetime.month}-{end_datetime.day}-{end_datetime.hour}-{end_datetime.minute}"
    return command_to_send


def publish_command(topic, message):
    from paho.mqtt.properties import Properties
    from paho.mqtt.packettypes import PacketTypes
    properties = Properties(PacketTypes.PUBLISH)
    properties.MessageExpiryInterval = 30  # in seconds

    mqtt_client.publish(topic, message, 0, properties=properties);

def connect_to_broker(sender, app_data, user_data):
    try:
        mqtt_client.on_message = on_message
        mqtt_client.on_connect = on_connect
        mqtt_client.on_subscribe = on_subscribe

        from paho.mqtt.properties import Properties
        from paho.mqtt.packettypes import PacketTypes
        properties = Properties(PacketTypes.CONNECT)
        properties.SessionExpiryInterval = 30 * 60  # in seconds
        mqtt_client.connect(MQTT_BROKER,
                            port=MQTT_PORT,
                            clean_start=mqtt.MQTT_CLEAN_START_FIRST_ONLY,
                            properties=properties,
                            keepalive=60)

        # Configurar la interfaz de usuario para indicar la conexión exitosa
        dpg.set_value(state_label, "Conectado")
        dpg.configure_item(state_label, color=[0, 255, 0])

        mqtt_client.loop_start()

    except Exception as e:
        print(f"Se produjo un error al conectar: {e}")
        print(traceback.format_exc())


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Conexión con reason: {reason_code} - flags: {flags} y properties: {properties}")
    if reason_code == "Success":
        print("Conexión exitosa")
        mqtt_client.subscribe(TOPIC_RESPONSE)
    else:
        print(f"Error al conectar: {reason_code}")


def on_message(client, userdata, message):
    msg = message.payload.decode("utf-8")
    decode_message(msg)

def decode_message(msg):
    if "error" in msg:
        print("Se detectó un error de lectura.")
    else:
        match = re.search(r'(\d{2}):(\d{2})', msg)
        if match:
            hour, minute = map(int, match.groups())
            print(f"Hora: {hour}, Minuto: {minute}")
        else:
            sensor_data = msg.split("\n")[0]

            # Convertimos la cadena hexadecimal a bytes
            data_bytes = bytes.fromhex(sensor_data.strip())

            # Desempaquetamos los datos
            mpu_accelX, mpu_accelY, mpu_accelZ, adc_adcX, adc_adcY, adc_adcZ = struct.unpack('HHHHHH', data_bytes)

            # Ahora puedes usar estos valores para recrear tus estructuras
            mpu_data = {'accelX': mpu_accelX, 'accelY': mpu_accelY, 'accelZ': mpu_accelZ}
            adc_data = {'adcX': adc_adcX, 'adcY': adc_adcY, 'adcZ': adc_adcZ}
            sd_data = {'mpuData': mpu_data, 'adcData': adc_data}

            print(f"Datos del sensor: {sd_data}")


def on_subscribe(client, userdata, mid, reason_codes, properties):
    print(f"Suscripción con reason: {reason_codes} - mid {mid} y properties: {properties}")
    if mid == 1:
        print("Suscripción exitosa")
    # Any reason code >= 128 is a failure.
    if mid >= 128:
        print(f"Error al suscribirse: {reason_codes}")


if __name__ == "__main__":
    main()
