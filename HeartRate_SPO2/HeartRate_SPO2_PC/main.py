import threading
import dearpygui.dearpygui as dpg
import Max_30102
import winsound
import time


# 设备串口，根据实际串口号更改
PORT = "COM11"


max_device = Max_30102.Device(PORT, 200)
dpg.create_context()


with dpg.font_registry():
    default_font = dpg.add_font("simhei.ttf", 20)
    big_font = dpg.add_font("simhei.ttf", 100)


with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(
            dpg.mvThemeCol_FrameBg, (0, 0, 0), category=dpg.mvThemeCat_Core
        )
        dpg.add_theme_color(
            dpg.mvThemeCol_WindowBg, (0, 0, 0), category=dpg.mvThemeCat_Core
        )
        dpg.add_theme_color(
            dpg.mvPlotCol_Line, (255, 255, 0), category=dpg.mvThemeCat_Plots
        )
        dpg.add_theme_color(
            dpg.mvPlotCol_FrameBg, (255, 255, 255), category=dpg.mvThemeCat_Core
        )
        dpg.add_theme_style(
            dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core
        )


def update_data():
    while True:
        max_device.get_data()
        dpg.set_value("rawIR", max_device.ir_list_data)
        if max_device.data_valid:
            dpg.set_value(
                "series_tag",
                [
                    max_device.range_list_time,
                    max_device.ir_list_data_filtered,
                ],
            )
        dpg.set_value(
            "Temperature_text",
            "Temperature: {:.1f} °C".format(max_device.data["temperatureC"]),
        )
        dpg.set_value("bpm_text", "BPM: {:.0f} ".format(max_device.data["HR"]))
        dpg.set_value("SPO2_text", "SPO2: {:.1f} %".format(max_device.data["SPO2"]))
        dpg.set_value("IR_text", "IR: {}".format(max_device.data["ir"]))
        dpg.set_value("RED_text", "RED: {}".format(max_device.data["red"]))


with dpg.window(tag="primary", label="IR Graph") as win_prima:
    dpg.add_simple_plot(
        label="", tag="rawIR", default_value=(0, 0), height=100, width=800
    )
    with dpg.plot(label="IR-F", height=300, width=800):
        # optionally create legend
        dpg.add_plot_legend()

        # REQUIRED: create x and y axes
        dpg.add_plot_axis(dpg.mvXAxis, label="x")
        dpg.add_plot_axis(dpg.mvYAxis, label="y", tag="y_axis")

        # series belong to a y axis
        dpg.add_line_series(
            max_device.data_list_time,
            max_device.ir_list_data_filtered,
            label="IR",
            parent="y_axis",
            tag="series_tag",
        )
    with dpg.drawlist(width=800, height=100):
        dpg.draw_rectangle(
            (0, 0),
            (800, 100),
            tag="beep_view",
            color=(255, 0, 0, 255),
            fill=(255, 0, 0, 255),
            show=False,
        )
    BPM_text = dpg.add_text("BPM:", pos=(0, 413), indent=20, tag="bpm_text")
    SPO2_text = dpg.add_text("SPO2:", tag="SPO2_text")
    dpg.add_text("Temperature:", tag="Temperature_text")
    dpg.add_text("IR:", tag="IR_text")
    dpg.add_text("RED:", tag="RED_text")
    dpg.bind_font(default_font)
    dpg.bind_item_font(BPM_text, big_font)
    dpg.bind_item_font(SPO2_text, big_font)


def HR_beep():
    while True:
        while max_device.k < 0:
            time.sleep(0.01)
        while max_device.k >= 0:
            time.sleep(0.01)
        winsound.Beep(2000, 150)
        dpg.configure_item("beep_view", show=True)
        time.sleep(0.1)
        dpg.configure_item("beep_view", show=False)


threading.Thread(target=update_data, daemon=True).start()
threading.Thread(target=HR_beep, daemon=True).start()
dpg.bind_theme(global_theme)
dpg.create_viewport(title="Heart Rate And SPO2", width=870, height=800)
dpg.set_primary_window("primary", True)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
