def select_columns(self):
    """Открытие окна для выбора столбцов для отображения - v1.1"""
    select_window = tk.Toplevel(self.root)
    select_window.title("Выбор столбцов для отображения - v1.1")
    select_window.geometry("600x700")

    # Основной фрейм
    main_frame = ttk.Frame(select_window)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # === ВЫБОР РЕЖИМА РАБОТЫ ===
    mode_frame = ttk.LabelFrame(main_frame, text="Режим работы:")
    mode_frame.pack(fill="x", padx=5, pady=5)
    
    mode_var = tk.StringVar(value="v1.0")
    
    ttk.Radiobutton(mode_frame, text="Режим v1.0 (один столбец времени для всех)", 
                   variable=mode_var, value="v1.0").pack(anchor="w", padx=10, pady=2)
    ttk.Radiobutton(mode_frame, text="Режим v1.1 (парная привязка время → параметр)", 
                   variable=mode_var, value="v1.1").pack(anchor="w", padx=10, pady=2)

    # === РЕЖИМ v1.0 (СОВМЕСТИМОСТЬ) ===
    v10_frame = ttk.LabelFrame(main_frame, text="Режим v1.0:")
    v10_frame.pack(fill="x", padx=5, pady=5)

    # Выбор столбца времени
    datetime_frame = ttk.Frame(v10_frame)
    datetime_frame.pack(fill="x", padx=5, pady=5)
    
    ttk.Label(datetime_frame, text="Столбец времени:").pack(anchor="w")
    datetime_var = tk.StringVar()
    datetime_combo = ttk.Combobox(datetime_frame, textvariable=datetime_var, 
                                values=list(self.df.columns), state="readonly")
    datetime_combo.pack(fill="x", pady=2)

    # Автоопределение столбца времени
    for col in self.df.columns:
        if any(kw in col.lower() for kw in ['date', 'time', 'datetime', 'дата', 'время']):
            datetime_combo.set(col)
            break

    # Выбор параметров
    params_frame = ttk.Frame(v10_frame)
    params_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    ttk.Label(params_frame, text="Параметры для отображения:").pack(anchor="w")
    
    param_vars = {}
    param_colors_vars = {}
    colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
    
    # Скроллируемый фрейм для параметров
    params_canvas = tk.Canvas(params_frame, height=150)
    params_scrollbar = ttk.Scrollbar(params_frame, orient="vertical", command=params_canvas.yview)
    params_scrollable_frame = ttk.Frame(params_canvas)
    
    params_scrollable_frame.bind(
        "<Configure>",
        lambda e: params_canvas.configure(scrollregion=params_canvas.bbox("all"))
    )
    
    params_canvas.create_window((0, 0), window=params_scrollable_frame, anchor="nw")
    params_canvas.configure(yscrollcommand=params_scrollbar.set)
    
    params_canvas.pack(side="left", fill="both", expand=True)
    params_scrollbar.pack(side="right", fill="y")
    
    # Создание чекбоксов для каждого столбца (кроме времени)
    for i, col in enumerate(self.df.columns):
        if col != datetime_var.get():
            var = tk.BooleanVar()
            param_vars[col] = var
            
            param_frame = ttk.Frame(params_scrollable_frame)
            param_frame.pack(fill="x", padx=5, pady=2)
            
            ttk.Checkbutton(param_frame, text=col, variable=var).pack(side="left")
            
            color_var = tk.StringVar(value=colors[i % len(colors)])
            param_colors_vars[col] = color_var
            ttk.Combobox(param_frame, textvariable=color_var, values=colors, 
                       state="readonly", width=10).pack(side="right", padx=(10, 0))

    # === РЕЖИМ v1.1 (ПАРНАЯ ПРИВЯЗКА) ===
    v11_frame = ttk.LabelFrame(main_frame, text="Режим v1.1 - Пары время → параметр:")
    v11_frame.pack(fill="x", padx=5, pady=5)

    # Список для хранения пар
    pairs_list = []
    
    def add_pair():
        """Добавить новую пару время → параметр"""
        pair_frame = ttk.Frame(pairs_container)
        pair_frame.pack(fill="x", pady=2)
        
        # Выпадающий список времени
        time_var = tk.StringVar()
        time_combo = ttk.Combobox(pair_frame, textvariable=time_var, 
                                values=list(self.df.columns), state="readonly", width=15)
        time_combo.pack(side="left", padx=2)
        
        # Стрелка
        ttk.Label(pair_frame, text="→").pack(side="left", padx=5)
        
        # Выпадающий список параметров
        param_var = tk.StringVar()
        param_combo = ttk.Combobox(pair_frame, textvariable=param_var, 
                                 values=list(self.df.columns), state="readonly", width=15)
        param_combo.pack(side="left", padx=2)
        
        # Выбор цвета
        color_var = tk.StringVar(value=colors[len(pairs_list) % len(colors)])
        color_combo = ttk.Combobox(pair_frame, textvariable=color_var, 
                                 values=colors, state="readonly", width=8)
        color_combo.pack(side="left", padx=2)
        
        # Кнопка удаления
        def remove_pair():
            pair_frame.destroy()
            pairs_list.remove(pair_data)
        
        ttk.Button(pair_frame, text="×", command=remove_pair, width=3).pack(side="left", padx=2)
        
        # Сохранение данных пары
        pair_data = {
            'frame': pair_frame,
            'time_var': time_var,
            'param_var': param_var,
            'color_var': color_var
        }
        pairs_list.append(pair_data)
    
    # Контейнер для пар
    pairs_container = ttk.Frame(v11_frame)
    pairs_container.pack(fill="x", padx=5, pady=5)
    
    # Кнопка добавления пары
    ttk.Button(v11_frame, text="+ Добавить пару", command=add_pair).pack(pady=5)

    # Функция переключения интерфейса
    def toggle_mode():
        """Переключение между режимами v1.0 и v1.1"""
        if mode_var.get() == "v1.0":
            v10_frame.pack(fill="x", padx=5, pady=5)
            v11_frame.pack_forget()
        else:
            v10_frame.pack_forget()
            v11_frame.pack(fill="x", padx=5, pady=5)
    
    # Привязка переключения режима
    mode_var.trace("w", lambda *args: toggle_mode())
    
    # Изначально показываем v1.0
    toggle_mode()

    # === КНОПКИ УПРАВЛЕНИЯ ===
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill="x", pady=10)
    
    def apply_selection():
        """Применить выбранные настройки"""
        selected_mode = mode_var.get()
        
        if selected_mode == "v1.0":
            # Режим v1.0 - старая логика
            selected_params = {}
            selected_colors = {}
            
            for col, var in param_vars.items():
                if var.get():
                    selected_params[col] = True
                    selected_colors[col] = param_colors_vars[col].get()
            
            if not selected_params:
                tk.messagebox.showwarning("Предупреждение", "Выберите хотя бы один параметр!")
                return
            
            if not datetime_var.get():
                tk.messagebox.showwarning("Предупреждение", "Выберите столбец времени!")
                return
            
            # Применяем настройки v1.0
            self.apply_selection_v10(datetime_var.get(), selected_params, selected_colors, select_window)
            
        else:
            # Режим v1.1 - новая логика с парами
            if not pairs_list:
                tk.messagebox.showwarning("Предупреждение", "Добавьте хотя бы одну пару время → параметр!")
                return
            
            # Проверка корректности пар
            valid_pairs = []
            for pair in pairs_list:
                time_col = pair['time_var'].get()
                param_col = pair['param_var'].get()
                color = pair['color_var'].get()
                
                if time_col and param_col and time_col != param_col:
                    valid_pairs.append((time_col, param_col, color))
            
            if not valid_pairs:
                tk.messagebox.showwarning("Предупреждение", "Настройте корректные пары время → параметр!")
                return
            
            # Применяем настройки v1.1
            self.apply_selection_v11(valid_pairs, select_window)
    
    ttk.Button(button_frame, text="OK", command=apply_selection).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Отмена", command=select_window.destroy).pack(side="left", padx=5)
