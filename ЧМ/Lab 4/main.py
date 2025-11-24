import numpy as np
import math

# ==========================================
# 1. ФУНКЦІЯ ТА ВУЗЛИ
# ==========================================

def f(x):
    # Варіант 2: 2*x^6 + 3*x^5 + 4*x^2 - 1
    return 2 * x**6 + 3 * x**5 + 4 * x**2 - 1

def get_chebyshev_nodes(a, b, n):
    """Генерація n вузлів Чебишова на відрізку [a, b]."""
    k = np.arange(n)
    # Вузли на [-1, 1]
    t_k = np.cos((2 * k + 1) / (2 * n) * math.pi)
    # Масштабування на [a, b]
    x_k = 0.5 * (a + b) + 0.5 * (b - a) * t_k
    return x_k

# ==========================================
# 2. ПОЛІНОМ НЬЮТОНА
# ==========================================

def divided_differences(x, y):
    """Обчислення розділених різниць."""
    n = len(y)
    coef = np.zeros([n, n])
    coef[:, 0] = y
    
    for j in range(1, n):
        for i in range(n - j):
            coef[i][j] = (coef[i+1][j-1] - coef[i][j-1]) / (x[i+j] - x[i])
            
    return coef[0, :]

def newton_poly(coef, x_data, x):
    """Обчислення значення полінома Ньютона в точці x."""
    n = len(x_data) - 1 
    p = coef[n]
    for k in range(1, n + 1):
        p = coef[n-k] + (x - x_data[n-k]) * p
    return p

# ==========================================
# 3. ОСНОВНА ЧАСТИНА
# ==========================================

def generate_plots(x_nodes, y_nodes, a, b, coef):
    try:
        import matplotlib.pyplot as plt
        
        # Графік 1: Функція та Поліном
        x_plot = np.linspace(a, b, 200)
        y_true = f(x_plot)
        y_interp = [newton_poly(coef, x_nodes, xi) for xi in x_plot]
        
        plt.figure(figsize=(10, 6))
        plt.plot(x_plot, y_true, 'b-', label='Функція $f(x)$', linewidth=2)
        plt.plot(x_plot, y_interp, 'r--', label='Поліном Ньютона $P_4(x)$')
        plt.plot(x_nodes, y_nodes, 'ko', label='Вузли Чебишова', zorder=5)
        plt.title(f"Інтерполяція поліномом Ньютона (n={len(x_nodes)})")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.legend()
        plt.grid(True)
        plt.savefig("graph_task_1.png")
        plt.close()
        print("Графік інтерполяції збережено як 'graph_task_1.png'")

        # Графік 2: Графік похибки (Error plot)
        error = np.abs(y_true - y_interp)
        plt.figure(figsize=(10, 6))
        plt.plot(x_plot, error, 'm-', label='|f(x) - P(x)|')
        plt.title("Графік абсолютної похибки інтерполяції")
        plt.xlabel("x")
        plt.ylabel("Похибка")
        plt.legend()
        plt.grid(True)
        plt.savefig("graph_task_2.png")
        plt.close()
        print("Графік похибки збережено як 'graph_task_2.png'")
        
        return np.max(error)

    except ImportError:
        print("[INFO] Matplotlib не знайдено. Графіки не згенеровано.")
        return 0.0

def main():
    print("\n" + "="*60)
    print("ЛАБОРАТОРНА РОБОТА №4: Інтерполяція")
    print("="*60)

    # Параметри
    a, b = 1.0, 5.0
    n = 5  # Кількість вузлів
    
    # 1. Вузли та поліном
    x_nodes = get_chebyshev_nodes(a, b, n)
    y_nodes = f(x_nodes)
    
    print(f"Проміжок: [{a}, {b}]")
    print(f"Вузли Чебишова ({n} шт.):")
    for i in range(n):
        print(f"  x[{i}] = {x_nodes[i]:.5f},  y[{i}] = {y_nodes[i]:.5f}")

    # Коефіцієнти полінома Ньютона
    coefs = divided_differences(x_nodes, y_nodes)
    print("\nКоефіцієнти полінома Ньютона (розділені різниці):")
    print(coefs)

    # Графіки та похибка
    max_err = generate_plots(x_nodes, y_nodes, a, b, coefs)
    print(f"\nМаксимальна похибка на відрізку: {max_err:.5e}")

    # 2. Знаходження кореня рівняння (f(x) = 0)
    print("\n" + "="*60)
    print("ЗАВДАННЯ 2: Знаходження кореня рівняння f(x)=0")
    print("="*60)
    
    # 2.1 Обернена інтерполяція (будуємо x(y))
    # Міняємо місцями x та y
    coefs_inv = divided_differences(y_nodes, x_nodes)
    
    # Шукаємо x для y=0
    root_inverse = newton_poly(coefs_inv, y_nodes, 0.0)
    
    print("Метод оберненої інтерполяції:")
    print(f"  Знайдений корінь x* ≈ {root_inverse:.5f}")
    print(f"  Нев'язка f(x*) = {f(root_inverse):.5e}")

    # 2.2 Пряма інтерполяція (розв'язуємо P(x) = 0)
    # Оскільки корінь (близько 0.46) лежить поза межами [1, 5], метод може бути неточним.
    # Спробуємо знайти корінь полінома чисельно
    from scipy.optimize import brentq, newton
    
    # Функція-обгортка для полінома
    def poly_func(x):
        return newton_poly(coefs, x_nodes, x)
    
    print("\nМетод прямої інтерполяції (шукаємо нуль полінома P(x)):")
    try:
        # Шукаємо корінь поблизу 0.5 (хоча це екстраполяція)
        root_direct = newton(poly_func, 0.5) 
        print(f"  Знайдений корінь x** ≈ {root_direct:.5f}")
        print(f"  Нев'язка f(x**) = {f(root_direct):.5e}")
    except:
        print("  Не вдалося знайти корінь методом Ньютона для полінома.")

    # Перевірка справжнього кореня
    print("\n[Довідка] Справжній корінь рівняння (fsolve):")
    try:
        from scipy.optimize import fsolve
        true_root = fsolve(f, 0.5)[0]
        print(f"  x_true ≈ {true_root:.5f}")
    except:
        pass

    print("\nПРИМІТКА: Корінь знаходиться поза проміжком інтерполяції [1, 5],")
    print("тому методи інтерполяції працюють в режимі екстраполяції, що знижує точність.")

if __name__ == "__main__":
    main()