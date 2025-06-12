# 🔧 Техническая документация Multi-Parameter Data Analyzer v1.1

## 🐛 **Исправленные проблемы в v1.1**

### ⚠️ **Проблема 1: KeyError 't3' при использовании временных пресетов в режиме v1.1**

**Описание:** Кнопки "1 час", "неделя", "сброс" вызывали ошибку в режиме парной привязки.

**Причина:** Методы `reset_time_range()` и `set_time_preset()` пытались использовать `self.datetime_column`, который не установлен в режиме v1.1.

**✅ Решение:**
```python
def reset_time_range(self):
    if self.use_paired_mode:
        # Режим v1.1 - используем объединенную временную шкалу
        if hasattr(self, 'time_param_pairs') and self.time_param_pairs:
            combined_timeline = self.create_combined_timeline()
            if combined_timeline is not None and not combined_timeline.empty:
                min_date = combined_timeline.index.min()
                max_date = combined_timeline.index.max()
    else:
        # Режим v1.0 - оригинальная логика
        min_date = self.df[self.datetime_column].min()
        max_date = self.df[self.datetime_column].max()
```

**Статус:** ✅ ИСПРАВЛЕНО

---

### ⚠️ **Проблема 2: Курсор привязывался только к первому столбцу времени в v1.1**

**Описание:** В режиме парной привязки курсор двигался только по первому временному ряду, игнорируя остальные.

**Причина:** Метод `on_mouse_move()` использовал `first_time_col = self.time_param_pairs[0][0]` вместо объединенной временной шкалы.

**✅ Решение:**
```python
def on_mouse_move(self, event):
    if self.use_paired_mode:
        # Создаем объединенную временную шкалу
        combined_timeline = self.create_combined_timeline()
        if combined_timeline is not None:
            # Находим ближайшую временную точку из всех систем
            nearest_time = combined_timeline.index[
                np.argmin(np.abs(combined_timeline.index - event.xdata))
            ]
    else:
        # Режим v1.0 - оригинальная логика
        # ...
```

**Статус:** ✅ ИСПРАВЛЕНО

---

## 🧹 **Очистка проекта**

### 📊 **Статистика удаления:**
- **Удалено файлов:** 15
- **Удалено папок:** 5  
- **Осталось актуальных файлов:** 11

### 🗑️ **Удаленные категории:**
- Устаревшие тестовые файлы (10 шт.)
- Дублирующаяся документация (3 шт.)
- Устаревшие модули разработки (2 шт.)
- Пустые папки разработки (5 шт.)

### ✅ **Сохраненные файлы:**
- `graf_csv.py` - основное приложение
- `MultiParameterAnalyzer.exe` - исполняемая версия
- `test_manual_pairs_v11_final.csv` - единственный нужный тест
- Оптимизированная документация (4 MD файла)

---

## 🔧 **Архитектура v1.1**

### 🎛️ **Основные компоненты:**

#### 1. **Режимы работы:**
- `self.use_paired_mode = False` - режим v1.0
- `self.use_paired_mode = True` - режим v1.1

#### 2. **Ключевые методы:**
- `select_columns()` - двухрежимный интерфейс выбора
- `apply_selection_v10()` - обработка v1.0
- `apply_selection_v11()` - обработка v1.1  
- `create_combined_timeline()` - объединение временных шкал
- `update_plot()` - универсальная отрисовка

#### 3. **Структуры данных v1.1:**
```python
# Парные привязки
self.time_param_pairs = [
    ("timestamp_A", "temperature_A"),
    ("timestamp_B", "pressure_B"),
    ("timestamp_C", "flow_rate_C")
]

# Цвета параметров
self.param_colors = {
    "temperature_A": "red",
    "pressure_B": "blue", 
    "flow_rate_C": "green"
}
```

### 🔄 **Алгоритм объединения временных шкал:**
1. Извлечение данных из каждой пары время-параметр
2. Переименование столбцов времени в единый 'timestamp'
3. Установка timestamp как индекс
4. Объединение через `pd.concat(axis=1, sort=True)`
5. Создание общей временной оси для всех параметров

---

## 📋 **Чек-лист для разработчиков**

### ✅ **Добавление новых функций:**
- [ ] Проверить совместимость с обоими режимами (v1.0 и v1.1)
- [ ] Протестировать с `test_manual_pairs_v11_final.csv`
- [ ] Обновить соответствующую документацию
- [ ] Добавить обработку ошибок для режима v1.1

### ✅ **Исправление багов:**
- [ ] Проверить влияние на оба режима
- [ ] Протестировать временные пресеты в v1.1
- [ ] Проверить работу курсора с объединенной временной шкалой
- [ ] Валидировать парные привязки

---

**📅 Последнее обновление:** 12 июня 2025  
**🔧 Статус:** Все известные проблемы исправлены ✅
