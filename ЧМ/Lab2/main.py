import numpy as np

# ==========================================
# 1. МЕТОД ГАУССА
# ==========================================
def solve_gauss():
    print("\n" + "="*50)
    print("ЗАВДАННЯ 1: Метод Гаусса")
    print("="*50)

    A = np.array([
        [7.0, 2.0, 3.0, 0.0],
        [0.0, 3.0, 2.0, 6.0],
        [2.0, 5.0, 1.0, 0.0],
        [0.0, 1.0, 4.0, 2.0]
    ])
    B = np.array([32.0, 47.0, 23.0, 29.0])

    print("Матриця A:")
    print(A)
    print("Вектор B:", B)

    # Розв'язок системою numpy (що використовує ефективний LU/Gauss)
    try:
        det = np.linalg.det(A)
        inv_A = np.linalg.inv(A)
        X = np.linalg.solve(A, B)
    except np.linalg.LinAlgError:
        print("Матриця вироджена, розв'язку не існує.")
        return

    print("-" * 30)
    print(f"Визначник (Determinant): {det:.4f}")
    print("-" * 30)
    print("Обернена матриця (Inverse):")
    for row in inv_A:
        print("  " + "  ".join(f"{val:8.4f}" for val in row))
    print("-" * 30)
    print("Вектор розв'язку X:")
    for i, val in enumerate(X):
        print(f"  x{i+1} = {val:.4f}")

# ==========================================
# 2. МЕТОД ПРОГОНКИ (THOMAS ALGORITHM)
# ==========================================
def solve_sweep():
    print("\n" + "="*50)
    print("ЗАВДАННЯ 2: Метод прогонки")
    print("="*50)

    # Система:
    # 1*x1 + 2*x2 + 0*x3 = 8
    # 2*x1 + 2*x2 + 3*x3 = 22
    # 0*x1 + 3*x2 + 2*x3 = 17
    
    n = 3
    # Коефіцієнти: a (під діагоналлю), b (діагональ), c (над діагоналлю), d (права частина)
    # Для першого рівняння a[0] = 0
    # Для останнього рівняння c[n-1] = 0
    
    a = np.array([0.0, 2.0, 3.0]) # Нижня діагональ (зсунута)
    b = np.array([1.0, 2.0, 2.0]) # Головна діагональ
    c = np.array([2.0, 3.0, 0.0]) # Верхня діагональ
    d = np.array([8.0, 22.0, 17.0]) # Права частина

    print("Коефіцієнти:")
    print(f"a: {a}")
    print(f"b: {b}")
    print(f"c: {c}")
    print(f"d: {d}")

    # Прямий хід
    alpha = np.zeros(n)
    beta = np.zeros(n)

    # Перший рядок
    alpha[0] = -c[0] / b[0]
    beta[0] = d[0] / b[0]

    print("\nПрогоночні коефіцієнти:")
    print(f"alpha[1]: {alpha[0]:.4f}, beta[1]: {beta[0]:.4f}")

    for i in range(1, n):
        denom = b[i] + a[i] * alpha[i-1]
        if i < n - 1:
            alpha[i] = -c[i] / denom
        beta[i] = (d[i] - a[i] * beta[i-1]) / denom
        print(f"alpha[{i+1}]: {alpha[i]:.4f} (якщо є), beta[{i+1}]: {beta[i]:.4f}")

    # Зворотний хід
    x = np.zeros(n)
    x[n-1] = beta[n-1]
    
    for i in range(n-2, -1, -1):
        x[i] = alpha[i] * x[i+1] + beta[i]

    print("-" * 30)
    print("Вектор розв'язку X:")
    for i, val in enumerate(x):
        print(f"  x{i+1} = {val:.4f}")

# ==========================================
# 3. МЕТОД ЯКОБІ
# ==========================================
def solve_jacobi(epsilon=1e-3):
    print("\n" + "="*50)
    print("ЗАВДАННЯ 3: Метод Якобі")
    print("="*50)

    A = np.array([
        [4.0, 0.0, 1.0, 0.0],
        [0.0, 3.0, 0.0, 2.0],
        [1.0, 0.0, 5.0, 1.0],
        [0.0, 2.0, 1.0, 4.0]
    ])
    B = np.array([7.0, 14.0, 20.0, 23.0])
    n = len(B)
    
    print("Перевірка діагональної переваги:")
    for i in range(n):
        diag = abs(A[i, i])
        off_diag = sum(abs(A[i, j]) for j in range(n) if i != j)
        print(f"Рядок {i+1}: |{diag}| > {off_diag}? {'Так' if diag > off_diag else 'Ні'}")

    x = np.zeros(n) # Початкове наближення
    print("\nТаблиця ітерацій:")
    print(f"{'Iter':<5} | {'x1':<10} | {'x2':<10} | {'x3':<10} | {'x4':<10} | {'Max Norm':<10}")
    print("-" * 70)
    
    iter_count = 0
    max_iter = 100
    
    while iter_count < max_iter:
        x_new = np.zeros(n)
        for i in range(n):
            s = sum(A[i, j] * x[j] for j in range(n) if i != j)
            x_new[i] = (B[i] - s) / A[i, i]
        
        norm = np.max(np.abs(x_new - x))
        iter_count += 1
        
        print(f"{iter_count:<5} | {x_new[0]:<10.4f} | {x_new[1]:<10.4f} | {x_new[2]:<10.4f} | {x_new[3]:<10.4f} | {norm:<10.4e}")
        
        x = x_new
        if norm < epsilon:
            break
            
    print("-" * 30)
    print(f"Знайдено розв'язок за {iter_count} ітерацій.")
    print("Вектор розв'язку X:")
    for i, val in enumerate(x):
        print(f"  x{i+1} = {val:.4f}")

def main():
    solve_gauss()
    solve_sweep()
    solve_jacobi()

if __name__ == "__main__":
    main()