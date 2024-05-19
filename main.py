import dearpygui.dearpygui as dpg
from screeninfo import get_monitors
from datetime import datetime

# Variables globales para la entrada de fechas
year_input, month_input, day_input, hour_input, minute_input = None, None, None, None, None
year_input_end, month_input_end, day_input_end, hour_input_end, minute_input_end = None, None, None, None, None


# Función para ejecutar el comando y registrar en la tabla
def send_command(sender, app_data, user_data):
    year = dpg.get_value(year_input)
    month = dpg.get_value(month_input)
    day = dpg.get_value(day_input)
    hour = dpg.get_value(hour_input)
    minute = dpg.get_value(minute_input)
    start_date = f"{year}-{month}-{day} {hour}:{minute}"

    year = dpg.get_value(year_input_end)
    month = dpg.get_value(month_input_end)
    day = dpg.get_value(day_input_end)
    hour = dpg.get_value(hour_input_end)
    minute = dpg.get_value(minute_input_end)
    end_date = f"{year}-{month}-{day} {hour}:{minute}"

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Agregar el comando a la tabla
    with dpg.table_row(parent=table):
        dpg.add_text(now)
        dpg.add_text(start_date)
        dpg.add_text(end_date)

    print(f"Comando ejecutado: Fecha Inicio: {start_date}, Fecha Fin: {end_date}")


def connect_to_broker(sender, app_data, user_data):
    # Aquí iría el código para conectar al broker
    dpg.configure_item(state_label, label="Conectado", color=[0, 255, 0])


def main():
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
                    global state_label
                    state_label = dpg.add_text("Desconectado", color=[255, 0, 0])

            with dpg.tab(label="Comandos"):
                # Configurar el layout de la ventana de comandos
                with dpg.group(horizontal=True):
                    with dpg.group():
                        # Widget para ingresar fechas (ARRIBA IZQUIERDA)
                        with dpg.child_window(width=window_width // 2 - 10, height=window_height // 2 - 10):
                            dpg.add_text("Fecha y hora Inicio:")
                            global year_input, month_input, day_input, hour_input, minute_input
                            with dpg.group(horizontal=True):
                                year_input = dpg.add_input_text(label="-", width=35, hint="YYYY")
                                month_input = dpg.add_input_text(label="-", width=25, hint="MM")
                                day_input = dpg.add_input_text(label="-", width=25, hint="DD")
                                hour_input = dpg.add_input_text(label=":", width=25, hint="HH")
                                minute_input = dpg.add_input_text(label="", width=25, hint="MM")

                            dpg.add_text("Fecha y hora Fin:")
                            global year_input_end, month_input_end, day_input_end, hour_input_end, minute_input_end
                            with dpg.group(horizontal=True):
                                year_input_end = dpg.add_input_text(label="-", width=35, hint="YYYY")
                                month_input_end = dpg.add_input_text(label="-", width=25, hint="MM")
                                day_input_end = dpg.add_input_text(label="-", width=25, hint="DD")
                                hour_input_end = dpg.add_input_text(label=":", width=25, hint="HH")
                                minute_input_end = dpg.add_input_text(label="", width=25, hint="MM")

                            dpg.add_button(label="Enviar", callback=send_command)

                        # Tabla para comandos ingresados (ABAJO IZQUIERDA)
                        with dpg.child_window(width=window_width // 2 - 10, height=window_height // 2 - 10):
                            dpg.add_text("Comandos Ingresados")
                            global table
                            with dpg.table(header_row=True, resizable=True, policy=dpg.mvTable_SizingStretchProp) as table:
                                dpg.add_table_column(label="Fecha y Hora")
                                dpg.add_table_column(label="Fecha Inicio")
                                dpg.add_table_column(label="Fecha Fin")

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


if __name__ == "__main__":
    main()
