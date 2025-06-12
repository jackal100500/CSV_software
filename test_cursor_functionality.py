#!/usr/bin/env python3
"""
Тест интерактивного курсора для Multi-Parameter Data Analyzer v2.0
Проверяет функциональность курсора с отображением значений параметров
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk

def create_test_data():
    """Создание тестовых данных для проверки курсора"""
    # Временной ряд
    start_time = datetime(2024, 1, 1, 10, 0, 0)
    times = [start_time + timedelta(minutes=i) for i in range(11)]
    
    # Данные параметров
    temperature = [25.5 + i * 0.2 for i in range(11)]  # 25.5 - 27.5
    pressure = [1.013 + i * 0.001 for i in range(11)]  # 1.013 - 1.023
    flow = [120.5 + i * 0.7 for i in range(11)]  # 120.5 - 128.0
    
    return times, temperature, pressure, flow

class InteractiveCursorTest:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Тест интерактивного курсора v2.0")
        self.root.geometry("1000x700")
          # Данные
        self.times, self.temperature, self.pressure, self.flow = create_test_data()
        
        # Курсор
        self.cursor_line = None
        self.param_value_labels = {}
        
        # UI элементы
        self.setup_ui()
        self.create_plot()
        
    def setup_ui(self):
        """Создание пользовательского интерфейса"""
        # Контейнер для значений параметров вверху
        self.param_frame = ttk.Frame(self.root)
        self.param_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(self.param_frame, text="Значения под курсором:", 
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        
        # Метки для значений параметров
        self.values_frame = ttk.Frame(self.param_frame)
        self.values_frame.pack(side=tk.LEFT, padx=20)
        
        # Создание меток для каждого параметра
        for i, (param, color) in enumerate([('Temperature', 'red'), ('Pressure', 'blue'), ('Flow', 'green')]):
            frame = ttk.Frame(self.values_frame)
            frame.pack(side=tk.LEFT, padx=10)
            
            ttk.Label(frame, text=f"{param}:", foreground=color, 
                     font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
            
            value_label = ttk.Label(frame, text="--", foreground=color, 
                                   font=('Arial', 9))
            value_label.pack(side=tk.LEFT, padx=(5, 0))
            
            self.param_value_labels[param] = value_label
            
        # Контейнер для графика
        self.plot_frame = ttk.Frame(self.root)
        self.plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
    def create_plot(self):
        """Создание графика с множественными Y-осями"""
        # Создание фигуры
        self.fig, self.ax1 = plt.subplots(figsize=(12, 8))
        self.fig.suptitle('Тест интерактивного курсора v2.0', fontsize=14, fontweight='bold')
        
        # Конвертация времени для matplotlib
        time_nums = mdates.date2num(self.times)
        
        # Ось 1 - Temperature (красная)
        self.ax1.plot(time_nums, self.temperature, 'r-', linewidth=2, label='Temperature')
        self.ax1.set_xlabel('Время')
        self.ax1.set_ylabel('Temperature (°C)', color='red')
        self.ax1.tick_params(axis='y', labelcolor='red')
        self.ax1.grid(True, alpha=0.3)
        
        # Ось 2 - Pressure (синяя)
        self.ax2 = self.ax1.twinx()
        self.ax2.plot(time_nums, self.pressure, 'b-', linewidth=2, label='Pressure')
        self.ax2.set_ylabel('Pressure (atm)', color='blue')
        self.ax2.tick_params(axis='y', labelcolor='blue')
        
        # Ось 3 - Flow (зеленая)
        self.ax3 = self.ax1.twinx()
        # Смещение третьей оси
        self.ax3.spines['right'].set_position(('outward', 60))
        self.ax3.plot(time_nums, self.flow, 'g-', linewidth=2, label='Flow')
        self.ax3.set_ylabel('Flow (L/min)', color='green')
        self.ax3.tick_params(axis='y', labelcolor='green')
        
        # Форматирование оси времени
        self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        self.ax1.xaxis.set_major_locator(mdates.MinuteLocator(interval=2))
        
        # Сохранение всех осей для курсора
        self.all_axes = [self.ax1, self.ax2, self.ax3]
        self.param_data = {
            'Temperature': (self.temperature, self.ax1),
            'Pressure': (self.pressure, self.ax2),
            'Flow': (self.flow, self.ax3)
        }
        
        # Интеграция с tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Подключение событий мыши
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.canvas.mpl_connect('axes_leave_event', self.on_mouse_leave)
        
        print("✅ Тестовый график создан с интерактивным курсором")
        
    def on_mouse_move(self, event):
        """Обработка движения мыши"""
        if event.inaxes and event.xdata and event.ydata:
            # Обновление курсора
            self.update_cursor_line(event.xdata)
            # Обновление значений параметров
            self.update_param_values(event.xdata)
            
    def on_mouse_leave(self, event):
        """Обработка выхода мыши из области графика"""
        self.clear_cursor_line()
        self.clear_param_values()
        
    def update_cursor_line(self, x_position):
        """Обновление вертикальной линии курсора"""
        try:
            # Удаление предыдущей линии
            if self.cursor_line is not None:
                try:
                    self.cursor_line.remove()
                except:
                    pass
                    
            # Создание новой линии на главной оси
            self.cursor_line = self.ax1.axvline(x=x_position, color='gray', 
                                               linestyle='--', alpha=0.7, linewidth=1)
            
            # Обновление холста
            self.canvas.draw_idle()
            
        except Exception as e:
            print(f"Ошибка обновления курсора: {e}")
            
    def clear_cursor_line(self):
        """Очистка линии курсора"""
        if self.cursor_line is not None:
            try:
                self.cursor_line.remove()
            except:
                pass
            self.cursor_line = None
            self.canvas.draw_idle()
            
    def update_param_values(self, x_position):
        """Обновление значений параметров под курсором"""
        try:
            # Конвертация X-координаты в datetime
            cursor_time = mdates.num2date(x_position)
            
            # Убираем информацию о часовом поясе для сравнения
            if hasattr(cursor_time, 'tzinfo') and cursor_time.tzinfo is not None:
                cursor_time = cursor_time.replace(tzinfo=None)
                
            # Найти ближайший индекс во временной шкале
            time_diffs = [abs((t - cursor_time).total_seconds()) for t in self.times]
            closest_idx = time_diffs.index(min(time_diffs))
            
            # Обновить значения для каждого параметра
            values = {
                'Temperature': self.temperature[closest_idx],
                'Pressure': self.pressure[closest_idx],
                'Flow': self.flow[closest_idx]
            }
            
            for param_name, value in values.items():
                if param_name in self.param_value_labels:
                    if param_name == 'Temperature':
                        self.param_value_labels[param_name].config(text=f"{value:.1f}°C")
                    elif param_name == 'Pressure':
                        self.param_value_labels[param_name].config(text=f"{value:.3f} atm")
                    elif param_name == 'Flow':
                        self.param_value_labels[param_name].config(text=f"{value:.1f} L/min")
                        
            # Отображение времени в заголовке
            time_str = cursor_time.strftime('%H:%M:%S')
            self.fig.suptitle(f'Тест интерактивного курсора v2.0 - Время: {time_str}', 
                             fontsize=14, fontweight='bold')
            
        except Exception as e:
            print(f"Ошибка обновления значений: {e}")
            
    def clear_param_values(self):
        """Очистка значений параметров"""
        for label in self.param_value_labels.values():
            label.config(text="--")
        self.fig.suptitle('Тест интерактивного курсора v2.0', fontsize=14, fontweight='bold')
        
    def run(self):
        """Запуск теста"""
        print("🚀 Запуск теста интерактивного курсора...")
        print("📍 Наведите мышь на график для просмотра значений")
        self.root.mainloop()

if __name__ == "__main__":
    test = InteractiveCursorTest()
    test.run()
