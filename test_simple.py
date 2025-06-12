import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class SimpleTimelineManager:
    def __init__(self):
        self.time_param_pairs = []
        self.time_keywords = ['date', 'time', 'datetime', 'дата', 'время', 'timestamp']
        
    def detect_time_columns(self, df):
        """Автоматически находит столбцы времени по ключевым словам"""
        time_columns = []
        
        for col in df.columns:
            col_lower = str(col).lower()
            
            # Проверяем по ключевым словам
            if any(keyword in col_lower for keyword in self.time_keywords):
                time_columns.append(col)
                continue
                
            # Проверяем тип данных (пытаемся преобразовать к datetime)
            try:
                sample = df[col].dropna().head(10)
                if len(sample) > 0:
                    pd.to_datetime(sample, errors='raise')
                    time_columns.append(col)
            except:
                continue
                
        return time_columns
    
    def auto_detect_pairs(self, df):
        """Автоматически связывает столбцы времени с параметрами"""
        time_columns = self.detect_time_columns(df)
        pairs = []
        columns_list = list(df.columns)
        
        for time_col in time_columns:
            time_idx = columns_list.index(time_col)
            
            # Ищем ближайший числовой столбец справа
            for i in range(time_idx + 1, len(columns_list)):
                param_col = columns_list[i]
                
                # Проверяем, что это числовой столбец
                if pd.api.types.is_numeric_dtype(df[param_col]):
                    # Проверяем, что столбец еще не использован
                    if not any(pair[1] == param_col for pair in pairs):
                        pairs.append((time_col, param_col))
                        break
                        
        return pairs


def test_simple_manager():
    """Простой тест менеджера"""
    print("=== Тест SimpleTimelineManager ===")
    
    # Создаем тестовые данные
    base_time = datetime(2025, 6, 12, 10, 0, 0)
    
    data = {
        'Date/Time1': [base_time + timedelta(seconds=i*10) for i in range(10)],
        'Information1': np.random.normal(100, 10, 10),
        'Date/Time2': [base_time + timedelta(seconds=i*15) for i in range(10)],
        'Information2': np.random.normal(50, 5, 10),
    }
    
    df = pd.DataFrame(data)
    print("Тестовые данные:")
    print(df.head())
    print(f"Столбцы: {list(df.columns)}")
    
    # Создаем менеджер
    manager = SimpleTimelineManager()
    
    # Тестируем автоопределение
    time_columns = manager.detect_time_columns(df)
    print(f"Найденные столбцы времени: {time_columns}")
    
    pairs = manager.auto_detect_pairs(df)
    print(f"Автоопределенные пары: {pairs}")
    
    print("=== Тест завершен ===")


if __name__ == "__main__":
    test_simple_manager()
