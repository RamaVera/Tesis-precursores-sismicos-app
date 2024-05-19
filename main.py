import dearpygui.dearpygui as dpg
from screeninfo import get_monitors
from datetime import datetime, timedelta
import traceback

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
        year = dpg.get_value(TAG_YEAR_INPUT_START)
        month = dpg.get_value(TAG_MONTH_INPUT_START)
        day = dpg.get_value(TAG_DAY_INPUT_START)
        hour = dpg.get_value(TAG_HOUR_INPUT_START)
        minute = dpg.get_value(TAG_MINUTE_INPUT_START)
        print(f"Valores obtenidos: year={year}, month={month}, day={day}, hour={hour}, minute={minute}")

        if not year or not month or not day or not hour or not minute:
            raise ValueError("Todos los campos de fecha y hora deben estar completos para la fecha de inicio.")

        year = int(year)
        month = int(month)
        day = int(day)
        hour = int(hour)
        minute = int(minute)
        start_date = f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}"

        year_end = dpg.get_value(TAG_YEAR_INPUT_END)
        month_end = dpg.get_value(TAG_MONTH_INPUT_END)
        day_end = dpg.get_value(TAG_DAY_INPUT_END)
        hour_end = dpg.get_value(TAG_HOUR_INPUT_END)
        minute_end = dpg.get_value(TAG_MINUTE_INPUT_END)

        if not year_end or not month_end or not day_end or not hour_end or not minute_end:
            raise ValueError("Todos los campos de fecha y hora deben estar completos para la fecha de fin.")

        year_end = int(year_end)
        month_end = int(month_end)
        day_end = int(day_end)
        hour_end = int(hour_end)
        minute_end = int(minute_end)
        end_date = f"{year_end}-{month_end:02d}-{day_end:02d} {hour_end:02d}:{minute_end:02d}"

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Agregar el comando a la tabla
        with dpg.table_row(parent=table):
            dpg.add_text(now)
            dpg.add_text(start_date)
            dpg.add_text(end_date)

        print(f"Comando ejecutado: Fecha Inicio: {start_date}, Fecha Fin: {end_date}")
    except ValueError as ve:
        print(f"Error: {ve}")
        print(traceback.format_exc())
    except Exception as e:
        print(f"Se produjo un error: {e}")
        print(traceback.format_exc())


def send_command_by_init_duration(sender, app_data, user_data):
    try:
        year = dpg.get_value(TAG_YEAR_INPUT_START_DUR)
        month = dpg.get_value(TAG_MONTH_INPUT_START_DUR)
        day = dpg.get_value(TAG_DAY_INPUT_START_DUR)
        hour = dpg.get_value(TAG_HOUR_INPUT_START_DUR)
        minute = dpg.get_value(TAG_MINUTE_INPUT_START_DUR)
        print(f"Valores obtenidos: year={year}, month={month}, day={day}, hour={hour}, minute={minute}")

        if not year or not month or not day or not hour or not minute:
            raise ValueError("Todos los campos de fecha y hora deben estar completos para la fecha de inicio.")

        year = int(year)
        month = int(month)
        day = int(day)
        hour = int(hour)
        minute = int(minute)
        start_date = f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}"

        duration_hours = dpg.get_value(TAG_DURATION_HOUR_INPUT)
        duration_minutes = dpg.get_value(TAG_DURATION_MINUTE_INPUT)

        if not duration_hours or not duration_minutes:
            raise ValueError("Todos los campos de duración deben estar completos.")

        duration_hours = int(duration_hours)
        duration_minutes = int(duration_minutes)

        # Crear un objeto datetime para la fecha de inicio
        start_datetime = datetime(year, month, day, hour, minute)

        # Sumar la duración al datetime de inicio
        end_datetime = start_datetime + timedelta(hours=duration_hours, minutes=duration_minutes)

        end_date = end_datetime.strftime("%Y-%m-%d %H:%M:%S")

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Agregar el comando a la tabla
        with dpg.table_row(parent=table):
            dpg.add_text(now)
            dpg.add_text(start_date)
            dpg.add_text(end_date)

        print(f"Comando ejecutado: Fecha Inicio: {start_date}, Fecha Fin: {end_date}")
    except ValueError as ve:
        print(f"Error: {ve}")
        print(traceback.format_exc())
    except Exception as e:
        print(f"Se produjo un error: {e}")
        print(traceback.format_exc())


def connect_to_broker(sender, app_data, user_data):
    try:
        # Aquí iría el código para conectar al broker
        dpg.set_value(state_label, "Conectado")
        dpg.configure_item(state_label, color=[0, 255, 0])
    except Exception as e:
        print(f"Se produjo un error al conectar: {e}")
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
