# file: lab3_variant3.py
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# ВАРІАНТ №3 (згідно з вашими скріншотами)
# ==========================================

DATA_FILE = "y3.txt"

# Параметри інтегрування
T_START = 0.0
T_END = 50.0  # Зі скріншоту

# ВІДОМІ параметри
c2_known = 0.3
c4_known = 0.12
m2_known = 28.0
m3_known = 18.0

# ПОЧАТКОВЕ НАБЛИЖЕННЯ для невідомих параметрів
# Ми шукаємо вектор beta = [c1, c3, m1]
# Початкове наближення beta0 = [0.1, 0.1, 9.0]
initial_guess = np.array([0.1, 0.1, 9.0]) 

# ==========================================
# МОДЕЛЬ ТА ЧУТЛИВІСТЬ
# ==========================================

def get_derivatives(t, Y, params):
    """
    Y = [x1, v1, x2, v2, x3, v3]
    params = [c1, c3, m1] (невідомі)
    """
    x1, v1, x2, v2, x3, v3 = Y
    c1, c3, m1 = params
    
    # Використовуємо відомі параметри
    c2 = c2_known
    c4 = c4_known
    m2 = m2_known
    m3 = m3_known
    
    # Рівняння руху для системи з 3 мас та 4 пружин:
    # m1*a1 = -c1*x1 + c2*(x2 - x1)  => -(c1+c2)x1 + c2*x2
    # m2*a2 = -c2*(x2 - x1) + c3*(x3 - x2) => c2*x1 - (c2+c3)x2 + c3*x3
    # m3*a3 = -c3*(x3 - x2) - c4*x3  => c3*x2 - (c3+c4)x3
    
    dx1 = v1
    dv1 = (-(c1 + c2) * x1 + c2 * x2) / m1
    
    dx2 = v2
    dv2 = (c2 * x1 - (c2 + c3) * x2 + c3 * x3) / m2
    
    dx3 = v3
    dv3 = (c3 * x2 - (c3 + c4) * x3) / m3
    
    return np.array([dx1, dv1, dx2, dv2, dx3, dv3])

def get_sensitivity_derivatives(t, Y, U, params):
    """
    U - матриця чутливості розміру (6, 3).
    Стовпці відповідають параметрам: [c1, c3, m1]
    """
    x1, v1, x2, v2, x3, v3 = Y
    c1, c3, m1 = params
    
    c2 = c2_known
    c4 = c4_known
    m2 = m2_known
    m3 = m3_known
    
    # --- Матриця A = df/dY (6x6) ---
    A = np.zeros((6, 6))
    
    # dx1/dt = v1
    A[0, 1] = 1.0
    
    # dv1/dt = (-(c1+c2)x1 + c2*x2) / m1
    A[1, 0] = -(c1 + c2) / m1  # d(dv1)/dx1
    A[1, 2] = c2 / m1          # d(dv1)/dx2
    
    # dx2/dt = v2
    A[2, 3] = 1.0
    
    # dv2/dt = (c2*x1 - (c2+c3)x2 + c3*x3) / m2
    A[3, 0] = c2 / m2          # d(dv2)/dx1
    A[3, 2] = -(c2 + c3) / m2  # d(dv2)/dx2
    A[3, 4] = c3 / m2          # d(dv2)/dx3
    
    # dx3/dt = v3
    A[4, 5] = 1.0
    
    # dv3/dt = (c3*x2 - (c3+c4)x3) / m3
    A[5, 2] = c3 / m3          # d(dv3)/dx2
    A[5, 4] = -(c3 + c4) / m3  # d(dv3)/dx3
    
    # --- Матриця B = df/d_beta (6x3) ---
    # beta = [c1, c3, m1]
    B = np.zeros((6, 3))
    
    # 1. Похідні по c1 (тільки в рівнянні для v1)
    # dv1/dc1 = (-x1)/m1
    B[1, 0] = -x1 / m1
    
    # 2. Похідні по c3 (в рівняннях для v2 та v3)
    # dv2/dc3 = (-x2 + x3)/m2
    B[3, 1] = (x3 - x2) / m2
    # dv3/dc3 = (x2 - x3)/m3
    B[5, 1] = (x2 - x3) / m3
    
    # 3. Похідні по m1 (тільки в рівнянні для v1)
    # dv1/dm1 = - (Force1) / m1^2
    force1 = (-(c1 + c2) * x1 + c2 * x2)
    B[1, 2] = -force1 / (m1**2)
    
    # Рівняння чутливості: dU/dt = A*U + B
    dU_dt = A @ U + B
    return dU_dt

# ==========================================
# ЧИСЕЛЬНІ МЕТОДИ (Рунге-Кутта 4)
# ==========================================

def solve_system_and_sensitivity(Y0, params, times):
    N = len(times)
    h = times[1] - times[0]
    num_vars = len(Y0)
    num_params = len(params)
    
    Y_history = np.zeros((num_vars, N))
    U_history = np.zeros((num_vars, num_params, N))
    
    Y_curr = Y0.copy()
    U_curr = np.zeros((num_vars, num_params))
    
    Y_history[:, 0] = Y_curr
    U_history[:, :, 0] = U_curr
    
    # Функція для розширеної системи (стан + чутливість)
    def extended_system(t_ext, State_ext, p_ext):
        # State_ext: перші 6 елементів - Y, наступні 18 - U (6x3 розгорнуті)
        y_local = State_ext[:6]
        u_local = State_ext[6:].reshape(6, num_params)
        
        dy = get_derivatives(t_ext, y_local, p_ext)
        du = get_sensitivity_derivatives(t_ext, y_local, u_local, p_ext)
        
        return np.concatenate([dy, du.flatten()])

    for i in range(N - 1):
        t = times[i]
        
        State_curr = np.concatenate([Y_curr, U_curr.flatten()])
        
        k1 = extended_system(t, State_curr, params)
        k2 = extended_system(t + 0.5*h, State_curr + 0.5*h*k1, params)
        k3 = extended_system(t + 0.5*h, State_curr + 0.5*h*k2, params)
        k4 = extended_system(t + h, State_curr + h*k3, params)
        
        State_next = State_curr + (h/6.0)*(k1 + 2*k2 + 2*k3 + k4)
        
        Y_next = State_next[:6]
        U_next = State_next[6:].reshape(6, num_params)
        
        Y_history[:, i+1] = Y_next
        U_history[:, :, i+1] = U_next
        
        Y_curr = Y_next
        U_curr = U_next
        
    return Y_history, U_history

# ==========================================
# ГОЛОВНА ФУНКЦІЯ
# ==========================================

def main():
    print(f"--- Лабораторна робота №3: Варіант 3 ---")
    
    # 1. Завантаження даних
    try:
        data = np.loadtxt(DATA_FILE)
        # Перевіряємо орієнтацію даних
        if data.shape[0] == 6 and data.shape[1] > 6:
            Y_obs = data
        else:
            Y_obs = data.T
            
        N_points = Y_obs.shape[1]
        print(f"  Дані завантажено: {N_points} точок, {Y_obs.shape[0]} змінних.")
    except Exception as e:
        print(f"Помилка завантаження {DATA_FILE}: {e}")
        return

    # 2. Часова сітка (0..50)
    times = np.linspace(T_START, T_END, N_points)
    dt = times[1] - times[0]
    print(f"  Час: {T_START}..{T_END}, крок dt = {dt:.4f}")
    
    # 3. Початкові умови (з файлу)
    Y0 = Y_obs[:, 0]
    
    # 4. Ідентифікація
    params = initial_guess.copy()
    max_iter = 50
    tol = 1e-5
    
    print("\n--- Старт ідентифікації (Гаусс-Ньютон) ---")
    print(f"  Відомі: c2={c2_known}, c4={c4_known}, m2={m2_known}, m3={m3_known}")
    print(f"  Шукаємо: [c1, c3, m1]")
    print(f"  Початкове наближення: {params}\n")
    
    loss_history = []
    
    for iteration in range(max_iter):
        # Пряма задача
        Y_model, U_model = solve_system_and_sensitivity(Y0, params, times)
        
        # Вектор нев'язки R (всі точки в один вектор)
        Residuals = (Y_obs - Y_model)
        R_vec = Residuals.flatten()
        
        # Функціонал якості (сума квадратів)
        loss = np.sum(R_vec**2)
        loss_history.append(loss)
        
        print(f"Iter {iteration+1:2d}: Loss = {loss:.6f}, Params = {params}")
        
        if loss < tol:
            print("  Збіжність досягнута (tolerance).")
            break
            
        # Матриця Якобі J (для МНК)
        # Розміри: (6*N_points, 3_params)
        J = np.zeros((6 * N_points, 3))
        
        # Заповнюємо J з матриці чутливості U
        # R_vec сформовано як [y1(t0)..y1(tk), y2(t0)..y2(tk)...] якщо flatten() row-major для (6,N)
        # (6, N) -> flatten -> 0-й рядок, 1-й рядок...
        
        # Тому J має бути структуровано так само
        for v in range(6): # по змінних
            for p in range(3): # по параметрах
                # v-й рядок U[:, p, :] - це похідні v-ї змінної по p-му параметру в усі моменти часу
                start_idx = v * N_points
                end_idx = (v + 1) * N_points
                J[start_idx:end_idx, p] = U_model[v, p, :]
        
        # Крок методу: delta = (J.T J)^-1 J.T R
        try:
            delta_p, _, _, _ = np.linalg.lstsq(J, R_vec, rcond=None)
        except np.linalg.LinAlgError:
            print("  Помилка лінійної алгебри (сингулярність).")
            break
            
        params = params + delta_p
        
        # Перевірка на малість кроку
        if np.linalg.norm(delta_p) < 1e-6:
            print("  Зміна параметрів замала. Зупинка.")
            break
            
    print("\n===========================================")
    print(f"ЗНАЙДЕНІ ПАРАМЕТРИ:")
    print(f"  c1 = {params[0]:.6f}")
    print(f"  c3 = {params[1]:.6f}")
    print(f"  m1 = {params[2]:.6f}")
    print("===========================================")
    
    # 5. Результати та графіки
    Y_final, _ = solve_system_and_sensitivity(Y0, params, times)
    
    plt.figure(figsize=(14, 6))
    
    plt.subplot(1, 2, 1)
    # Відобразимо координати x1, x2, x3
    plt.plot(times, Y_obs[0, :], 'r.', markersize=2, label='Obs x1')
    plt.plot(times, Y_final[0, :], 'r-', linewidth=1, label='Mod x1')
    
    plt.plot(times, Y_obs[2, :], 'g.', markersize=2, label='Obs x2')
    plt.plot(times, Y_final[2, :], 'g-', linewidth=1, label='Mod x2')
    
    plt.plot(times, Y_obs[4, :], 'b.', markersize=2, label='Obs x3')
    plt.plot(times, Y_final[4, :], 'b-', linewidth=1, label='Mod x3')
    
    plt.title("Порівняння моделі та експерименту")
    plt.xlabel("Час")
    plt.ylabel("Координати")
    plt.legend()
    plt.grid(True)
    
    plt.subplot(1, 2, 2)
    plt.plot(loss_history, 'k-o')
    plt.yscale('log')
    plt.title("Функція втрат (Loss)")
    plt.xlabel("Ітерація")
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig("lab3_v3_result.png")
    print("Графік збережено у lab3_v3_result.png")
    plt.show()

if __name__ == "__main__":
    main()