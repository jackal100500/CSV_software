# Исправление ошибки временных пресетов в Multi-Parameter Data Analyzer v1.1

## Описание проблемы

**Дата исправления:** 12 июня 2025 г.

**Ошибка:** KeyError 't3' при использовании кнопок временных пресетов (1 час, неделя, сброс) в режиме v1.1 (paired mode).

**Причина:** Методы `reset_time_range()` и `set_time_preset()` были разработаны только для режима v1.0 и пытались использовать `self.datetime_column`, который не установлен в режиме v1.1.

## Исправления

### 1. Метод `reset_time_range()`

**Файл:** `graf_csv.py` (строки ~746-775)

**Изменения:**
- Добавлена проверка `self.use_paired_mode`
- Для режима v1.1: используется `create_combined_timeline()` для получения min/max дат
- Для режима v1.0: сохранена оригинальная логика с `self.datetime_column`
- Добавлена обработка случаев, когда данные могут быть None

```python
def reset_time_range(self):
    """Сброс временного диапазона к полному"""
    if self.df is None:
        return
        
    min_date = None
    max_date = None
    
    if self.use_paired_mode:
        # Режим v1.1 - используем объединенную временную шкалу
        if hasattr(self, 'time_param_pairs') and self.time_param_pairs:
            combined_timeline = self.create_combined_timeline()
            if combined_timeline is not None and not combined_timeline.empty:
                min_date = combined_timeline.index.min()
                max_date = combined_timeline.index.max()
    else:
        # Режим v1.0 - используем единый столбец времени
        if hasattr(self, 'datetime_column') and self.datetime_column is not None:
            min_date = self.df[self.datetime_column].min()
            max_date = self.df[self.datetime_column].max()
    
    if min_date is not None and max_date is not None:
        self.start_date_entry.delete(0, tk.END)
        self.start_date_entry.insert(0, min_date.strftime("%Y-%m-%d %H:%M:%S"))
        
        self.end_date_entry.delete(0, tk.END)
        self.end_date_entry.insert(0, max_date.strftime("%Y-%m-%d %H:%M:%S"))
        
        self.update_plot()
```

### 2. Метод `set_time_preset()`

**Файл:** `graf_csv.py` (строки ~777-810)

**Изменения:**
- Добавлена аналогичная проверка режима
- Для режима v1.1: используется объединенная временная шкала для получения max_date
- Для режима v1.0: сохранена оригинальная логика

```python
def set_time_preset(self, hours=None, days=None):
    """Установка предустановленного временного диапазона"""
    if self.df is None:
        return
        
    max_date = None
    
    if self.use_paired_mode:
        # Режим v1.1 - используем объединенную временную шкалу
        if hasattr(self, 'time_param_pairs') and self.time_param_pairs:
            combined_timeline = self.create_combined_timeline()
            if combined_timeline is not None and not combined_timeline.empty:
                max_date = combined_timeline.index.max()
    else:
        # Режим v1.0 - используем единый столбец времени
        if hasattr(self, 'datetime_column') and self.datetime_column is not None:
            max_date = self.df[self.datetime_column].max()
    
    if max_date is None:
        return
        
    # Остальная логика без изменений...
```

## Тестирование

### Шаги для тестирования:

1. **Запуск приложения:** ✅ Успешно
   ```
   python graf_csv.py
   ```

2. **Тест режима v1.1:**
   - [ ] Загрузить файл с парными данными время-параметр
   - [ ] Включить режим "Paired Parameters (v1.1)"
   - [ ] Проверить работу кнопок:
     - [ ] "1 час"
     - [ ] "Неделя" 
     - [ ] "Сброс"

3. **Тест режима v1.0:**
   - [ ] Загрузить обычный CSV файл
   - [ ] Убедиться, что режим v1.0 работает как прежде
   - [ ] Проверить работу кнопок временных пресетов

## Статус исправления

- ✅ **Синтаксические ошибки исправлены**
- ✅ **Приложение запускается без ошибок**
- ⏳ **Функциональное тестирование в процессе**

## Файлы, затронутые исправлением

- `graf_csv.py` - основной файл приложения
- `BUGFIX_TIME_PRESETS_v1.1.md` - данный документ с описанием исправления

## Следующие шаги

1. Провести полное функциональное тестирование в обоих режимах
2. Обновить документацию пользователя
3. Добавить автоматические тесты для предотвращения регрессии
4. Рассмотреть возможность рефакторинга для упрощения поддержки двух режимов

---

**Исправление выполнено:** GitHub Copilot  
**Дата:** 12 июня 2025 г.
