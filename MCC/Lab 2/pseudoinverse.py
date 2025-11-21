# file: pseudoinverse.py

import numpy as np


def is_pseudoinverse(A: np.ndarray,
                     A_plus: np.ndarray,
                     tol: float = 1e-8) -> bool:
    """
    перевірка 4 умов Мура–Пенроуза для псевдооберненої матриці
    """
    # 1) A A⁺ A = A
    cond1 = np.allclose(A @ A_plus @ A, A, atol=tol)
    # 2) A⁺ A A⁺ = A⁺
    cond2 = np.allclose(A_plus @ A @ A_plus, A_plus, atol=tol)
    # 3) A A⁺ симетрична
    AA_plus = A @ A_plus
    cond3 = np.allclose(AA_plus, AA_plus.T, atol=tol)
    # 4) A⁺ A симетрична
    A_plusA = A_plus @ A
    cond4 = np.allclose(A_plusA, A_plusA.T, atol=tol)

    print("Перевірка умов Мура–Пенроуза:")
    print(f"  1) A A⁺ A ≈ A : {cond1}")
    print(f"  2) A⁺ A A⁺ ≈ A⁺ : {cond2}")
    print(f"  3) A A⁺ симетрична : {cond3}")
    print(f"  4) A⁺ A симетрична : {cond4}")

    return cond1 and cond2 and cond3 and cond4


def pseudo_inverse_moore_penrose(A: np.ndarray,
                                 eps: float = 1e-6,
                                 delta_init: float = 10.0,
                                 max_iter: int = 1000):
    """
    псевдообернена за означенням Мура–Пенроуза через граничний перехід:
      A⁺ ≈ Aᵀ (A Aᵀ + δ² I)⁻¹  (якщо m <= n)
      A⁺ ≈ (Aᵀ A + δ² I)⁻¹ Aᵀ  (якщо m > n)

    ітераційно зменшуємо δ, поки ||A⁺_k - A⁺_{k-1}||_F < eps
    або не досягнемо max_iter.
    повертає (A_plus, iterations).
    """
    A = np.asarray(A, dtype=float)
    m, n = A.shape

    delta = float(delta_init)

    def compute_A_plus(delta_val: float) -> np.ndarray:
        if m <= n:
            # використовуємо Aᵀ (A Aᵀ + δ² I)⁻¹
            M = A @ A.T + (delta_val ** 2) * np.eye(m)
            return A.T @ np.linalg.inv(M)
        else:
            # використовуємо (Aᵀ A + δ² I)⁻¹ Aᵀ
            M = A.T @ A + (delta_val ** 2) * np.eye(n)
            return np.linalg.inv(M) @ A.T

    A_prev = compute_A_plus(delta)
    iterations = 0

    while iterations < max_iter:
        delta /= 2.0
        A_cur = compute_A_plus(delta)
        diff = np.linalg.norm(A_cur - A_prev, ord="fro")

        if diff < eps:
            return A_cur, iterations + 1

        A_prev = A_cur
        iterations += 1

    # Якщо не збіглося до eps, повертаємо останнє наближення
    print("Увага: досягнуто max_iter у Moore–Penrose, збіжність до eps не гарантована.")
    return A_prev, iterations


def pseudo_inverse_greville(A: np.ndarray,
                            eps: float = 1e-10):
    """
    псевдообернена матриця за методом Гревіля.
    A — розмір m x n, обробляємо рядки A як a_i^T

    повертає (A_plus, iterations), де iterations = m - 1 (к-ть кроків)
    """
    A = np.asarray(A, dtype=float)
    m, n = A.shape

    # Перший рядок
    a1 = A[0, :].reshape(n, 1)      # стовпчик
    denom = float(a1.T @ a1)        # скаляр a1^T a1

    if abs(denom) < eps:
        A_plus = np.zeros((n, 1), dtype=float)
    else:
        A_plus = a1 / denom         # n x 1

    current_A = A[0:1, :]           # 1 x n

    # Послідовно додаємо рядки
    for i in range(1, m):
        a = A[i, :].reshape(n, 1)   # n x 1

        # Z = I - A⁺ A
        Z = np.eye(current_A.shape[1]) - A_plus @ current_A  # n x n
        quad_form = float(a.T @ Z @ a)                       # скаляр a^T Z a

        if quad_form > eps:
            # випадок a^T Z a > 0
            left = A_plus - (Z @ a @ (a.T @ A_plus)) / quad_form
            right = (Z @ a) / quad_form
            A_plus = np.hstack((left, right))
        else:
            # випадок a^T Z a ≈ 0
            R = A_plus @ A_plus.T
            denom2 = 1.0 + float(a.T @ R @ a)
            left = A_plus - (R @ a @ (a.T @ A_plus)) / denom2
            right = (R @ a) / denom2
            A_plus = np.hstack((left, right))

        current_A = np.vstack((current_A, A[i, :]))

    iterations = m - 1
    return A_plus, iterations
