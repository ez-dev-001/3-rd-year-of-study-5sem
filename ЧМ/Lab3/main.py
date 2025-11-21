import numpy as np
import math

# ==========================================
# ЗАВДАННЯ 1: Власні значення матриці
# ==========================================

def task_1_eigenvalues():
    print("\n" + "="*60)
    print("ЗАВДАННЯ 1: Власні значення матриці")
    print("="*60)

    A = np.array([
        [3.0, 1.0, 0.0, 1.0],
        [1.0, 2.0, 1.0, 0.0],
        [0.0, 1.0, 4.0, 2.0],
        [1.0, 0.0, 2.0, 5.0]
    ])
    
    print("Матриця A:")
    print(A)

    # --- 1.1 Стешеневий метод (для найменшого значення використовуємо обернену ітерацію) ---
    print("\n--- Пошук найменшого власного значення (Обернена ітерація) ---")
    # Для пошуку найменшого лямбда застосовуємо степеневий метод до матриці A^(-1)
    # Власне значення A^(-1) буде 1/lambda_min
    
    try:
        A_inv = np.linalg.inv(A)
    except np.linalg.LinAlgError:
        print("Матриця вироджена, метод не застосовується.")
        return

    x = np.ones(A.shape[0]) # Початковий вектор
    lam_prev = 0
    epsilon = 1e-4
    
    print(f"{'Iter':<5} | {'Lambda (approx)':<20} | {'Delta':<20}")
    print("-" * 50)

    for i in range(100):
        x_next = np.dot(A_inv, x)
        # Нормування вектора (знаходимо компоненту з макс. модулем)
        lam = x_next[np.argmax(np.abs(x_next))]
        x_next = x_next / np.max(np.abs(x_next)) # Нормування
        
        delta = abs(lam - lam_prev)
        print(f"{i+1:<5} | {1/lam:<20.5f} | {delta:<20.5e}") # Виводимо 1/lam, бо шукаємо для A
        
        if delta < epsilon and i > 0:
            x = x_next
            break
        
        lam_prev = lam
        x = x_next

    min_lambda = 1 / lam_prev
    print(f"\nНайменше власне значення (approx): {min_lambda:.5f}")


    # --- 1.2 Метод обертань Якобі ---
    print("\n--- Метод обертань Якобі (всі власні значення) ---")
    
    # Копія для роботи
    Aj = A.copy()
    n = Aj.shape[0]
    iterations = 5 # Як в умові (3-4 ітерації, зробимо 5 для наочності)
    
    # Матриця власних векторів (початково одинична)
    V = np.eye(n)

    print(f"{'Iter':<5} | {'Max Element (off-diag)':<25} | {'Indices (p, q)'}")
    print("-" * 50)

    for k in range(iterations):
        # Пошук максимального недіагонального елемента
        max_val = 0.0
        p, q = 0, 0
        for i in range(n):
            for j in range(i + 1, n):
                if abs(Aj[i, j]) > max_val:
                    max_val = abs(Aj[i, j])
                    p, q = i, j
        
        if max_val < 1e-5:
            break

        # Обчислення кута обертання
        if Aj[p, p] == Aj[q, q]:
            theta = math.pi / 4
        else:
            theta = 0.5 * math.atan(2 * Aj[p, q] / (Aj[p, p] - Aj[q, q]))
        
        c = math.cos(theta)
        s = math.sin(theta)
        
        # Матриця обертання U
        # Перерахунок елементів (спрощена схема для симетричної матриці)
        new_App = c**2 * Aj[p, p] + s**2 * Aj[q, q] + 2*c*s*Aj[p, q]
        new_Aqq = s**2 * Aj[p, p] + c**2 * Aj[q, q] - 2*c*s*Aj[p, q]
        new_Apq = 0.0 # Цілеспрямовано занулюємо
        
        # Перерахунок інших елементів у рядках/стовпцях p та q
        for i in range(n):
            if i != p and i != q:
                new_Api = c * Aj[p, i] + s * Aj[q, i]
                new_Aqi = -s * Aj[p, i] + c * Aj[q, i]
                Aj[i, p] = Aj[p, i] = new_Api
                Aj[i, q] = Aj[q, i] = new_Aqi
        
        Aj[p, p] = new_App
        Aj[q, q] = new_Aqq
        Aj[p, q] = Aj[q, p] = new_Apq
        
        print(f"{k+1:<5} | {max_val:<25.5f} | ({p+1}, {q+1})")

    print("\nНаближені власні значення (діагональ):")
    eig_vals = np.diag(Aj)
    print(np.round(eig_vals, 4))
    print("Перевірка numpy.linalg.eigvals:")
    print(np.round(np.linalg.eigvals(A), 4))


# ==========================================
# ЗАВДАННЯ 2: Модифікований метод Ньютона
# ==========================================

def sys_f(vars):
    x, y = vars
    # sin(x - 0.6) - y = 1.6  =>  f1 = sin(x - 0.6) - y - 1.6
    # 3x - cos(y) = 0.9       =>  f2 = 3x - cos(y) - 0.9
    return np.array([
        math.sin(x - 0.6) - y - 1.6,
        3 * x - math.cos(y) - 0.9
    ])

def sys_jacobian(vars):
    x, y = vars
    # df1/dx = cos(x - 0.6),  df1/dy = -1
    # df2/dx = 3,             df2/dy = sin(y)
    return np.array([
        [math.cos(x - 0.6), -1.0],
        [3.0, math.sin(y)]
    ])

def task_2_newton():
    print("\n" + "="*60)
    print("ЗАВДАННЯ 2: Модифікований метод Ньютона")
    print("="*60)
    
    # Початкове наближення
    # З першого рівняння y ≈ -1.6 (якщо sin малий)
    # З другого рівняння 3x ≈ 0.9 + cos(-1.6) ≈ 0.9 - 0.02 ≈ 0.9 => x ≈ 0.3
    x0 = np.array([0.15, -2.0]) 
    
    print(f"Початкове наближення: x={x0[0]}, y={x0[1]}")
    
    # Для модифікованого методу Якобіан обчислюється один раз в точці x0
    J0 = sys_jacobian(x0)
    try:
        J0_inv = np.linalg.inv(J0)
    except np.linalg.LinAlgError:
        print("Якобіан вироджений.")
        return

    curr_x = x0.copy()
    
    print(f"{'Iter':<5} | {'x':<10} | {'y':<10} | {'dx':<10} | {'dy':<10}")
    print("-" * 55)

    for k in range(5): # 5 ітерацій як в умові
        F_val = sys_f(curr_x)
        
        # Модифікований Ньютон: x(k+1) = x(k) - J(x0)^(-1) * F(x(k))
        delta = np.dot(J0_inv, F_val)
        
        next_x = curr_x - delta
        
        print(f"{k+1:<5} | {next_x[0]:<10.4f} | {next_x[1]:<10.4f} | {delta[0]:<10.4e} | {delta[1]:<10.4e}")
        
        curr_x = next_x

    print("-" * 55)
    print("Кінцевий результат:")
    print(f"x = {curr_x[0]:.5f}")
    print(f"y = {curr_x[1]:.5f}")
    
    # Перевірка
    res = sys_f(curr_x)
    print(f"Нев'язка (Residuals): {res}")

def main():
    task_1_eigenvalues()
    task_2_newton()

if __name__ == "__main__":
    main()