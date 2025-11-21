import math

# ==========================================
# Налаштування та допоміжні функції
# ==========================================

def generate_plots():
    """
    Генерація графіків функцій для пункту 1 звіту.
    Зберігає зображення у файли graph_task_1.png та graph_task_2.png.
    """
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("\n[INFO] Бібліотека matplotlib не знайдена. Графіки не будуть згенеровані автоматично.")
        return

    # Графік 1
    x = np.linspace(-0.5, 2.5, 400)
    y = x**3 - 2*x**2 - x + 2
    plt.figure(figsize=(8, 6))
    plt.plot(x, y, label=r'$x^3 - 2x^2 - x + 2$')
    plt.axhline(0, color='black', linewidth=1)
    plt.axvline(0, color='black', linewidth=1)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.scatter([1], [0], color='red', zorder=5, label='Корінь x=1')
    plt.title("Завдання 1: Метод релаксації")
    plt.legend()
    plt.savefig("graph_task_1.png")
    plt.close()

    # Графік 2
    x = np.linspace(-0.5, 3.5, 400)
    y = x**3 - 4*x**2 + x + 6
    plt.figure(figsize=(8, 6))
    plt.plot(x, y, color='green', label=r'$x^3 - 4x^2 + x + 6$')
    plt.axhline(0, color='black', linewidth=1)
    plt.axvline(0, color='black', linewidth=1)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.scatter([2], [0], color='red', zorder=5, label='Корінь x=2')
    plt.title("Завдання 2: Модиф. метод Ньютона")
    plt.legend()
    plt.savefig("graph_task_2.png")
    plt.close()
    print("[INFO] Графіки збережено у файли 'graph_task_1.png' та 'graph_task_2.png'")

# ==========================================
# ЗАВДАННЯ 1: Метод релаксації
# ==========================================

def f1(x):
    return x**3 - 2*x**2 - x + 2

def solve_relaxation(epsilon):
    print("\n" + "="*60)
    print("ЗАВДАННЯ 1: Метод релаксації")
    print("="*60)
    
    # Параметри з теоретичного обґрунтування
    x0 = 0.5
    x_target = 1.0 # Для розрахунку апріорної оцінки
    m1 = 0.25
    M1 = 2.25
    
    # Розрахунок tau та q
    tau = 2 / (M1 + m1)
    q = (M1 - m1) / (M1 + m1)
    
    print(f"Параметр tau: {tau:.4f}")
    print(f"Коефіцієнт q:   {q:.4f}")
    
    # Пункт 3: Апріорна оцінка (перераховується програмою)
    dist = abs(x0 - x_target) # Або довжина інтервалу
    if q < 1:
        n_apriori = math.floor(math.log(dist / epsilon) / math.log(1/q)) + 1
        print(f"Апріорна оцінка кількості ітерацій (для eps={epsilon}): {n_apriori}")
    else:
        print("Апріорна оцінка неможлива (q >= 1)")
        
    # Пункт 4: Таблиця результатів
    print("\nТаблиця результатів:")
    print(f"{'n':<5} | {'xn':<15} | {'f(xn)':<15} | {'|xn - xn-1|':<15}")
    print("-" * 58)
    
    xn = x0
    n = 0
    print(f"{n:<5} | {xn:<15.10f} | {f1(xn):<15.10f} | {'-':<15}")
    
    while True:
        n += 1
        xn_prev = xn
        # Ітерація: x = x + tau * f(x) (знак + бо f'<0)
        xn = xn_prev + tau * f1(xn_prev)
        diff = abs(xn - xn_prev)
        
        print(f"{n:<5} | {xn:<15.10f} | {f1(xn):<15.10f} | {diff:<15.10f}")
        
        if diff <= epsilon:
            break
        if n > 100:
            print("Помилка: Перевищено ліміт ітерацій")
            break

# ==========================================
# ЗАВДАННЯ 2: Модифікований метод Ньютона
# ==========================================

def f2(x):
    return x**3 - 4*x**2 + x + 6

def df2(x):
    return 3*x**2 - 8*x + 1

def solve_mod_newton(epsilon):
    print("\n" + "="*60)
    print("ЗАВДАННЯ 2: Модифікований метод Ньютона")
    print("="*60)
    
    x0 = 1.5
    df_x0 = df2(x0) # Похідна фіксована
    
    print(f"Початкове наближення x0: {x0}")
    print(f"Фіксована похідна f'(x0): {df_x0:.4f}")
    
    # Пункт 4: Таблиця результатів
    print("\nТаблиця результатів:")
    print(f"{'n':<5} | {'xn':<15} | {'f(xn)':<15} | {'|xn - xn-1|':<15}")
    print("-" * 58)
    
    xn = x0
    n = 0
    print(f"{n:<5} | {xn:<15.10f} | {f2(xn):<15.10f} | {'-':<15}")
    
    while True:
        n += 1
        xn_prev = xn
        # Ітерація: x = x - f(x)/f'(x0)
        xn = xn_prev - f2(xn_prev) / df_x0
        diff = abs(xn - xn_prev)
        
        print(f"{n:<5} | {xn:<15.10f} | {f2(xn):<15.10f} | {diff:<15.10f}")
        
        if diff <= epsilon:
            break
        if n > 100:
            break

# ==========================================
# Головна функція
# ==========================================
def main():
    generate_plots()
    
    # Точність фіксована (згідно з вашим побажанням), 
    # але змінна eps використовується у формулах, 
    # тому умова "перерахунок при зміні" виконується кодом.
    eps = 1e-3 
    
    solve_relaxation(eps)
    solve_mod_newton(eps)

if __name__ == "__main__":
    main()