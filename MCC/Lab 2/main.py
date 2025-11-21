import numpy as np
import time
import os


from PIL import Image
import matplotlib.pyplot as plt

from image_io import read_grayscale_image, save_grayscale_image
from pseudoinverse import (
    pseudo_inverse_moore_penrose,
    pseudo_inverse_greville,
    is_pseudoinverse,
)

def read_and_resize(path: str, target_shape: tuple) -> np.ndarray:
   
    try:
        img = Image.open(path).convert("L")
    except FileNotFoundError:
        print(f"Помилка: Файл {path} не знайдено!")
        
        raise
    
    # numpy shape = (height, width), а PIL требует (width, height)
    target_h, target_w = target_shape
    
    
    if (img.height, img.width) != (target_h, target_w):
        print(f"   -> Масштабування {path}: {img.size} -> {(target_w, target_h)}")
        img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    arr = np.asarray(img, dtype=np.float64)
    arr /= 255.0
    return arr

def augment_with_ones(X: np.ndarray) -> np.ndarray:
    """
    додає рядок одиниць до X
        X̃ = [ X
              1 ... 1 ]
    """
    ones = np.ones((1, X.shape[1]), dtype=float)
    return np.vstack((X, ones))


def compute_errors(Y_true: np.ndarray, Y_pred: np.ndarray):
    diff = Y_true - Y_pred
    error_norm = np.linalg.norm(diff, ord=1)
    mse = np.mean(diff ** 2)
    rmse = np.sqrt(mse)
    return error_norm, mse, rmse


def build_operator_and_predict(
    X: np.ndarray,
    Y: np.ndarray,
    pinv_method,
    method_name: str,
):
    """
    1)будує X̃ = [X; 1 ... 1]
    2)обчислює X̃⁺ заданим методом
    3)перевіряє умови Мура–Пенроуза
    4)будує A = Y X̃⁺
    5) тримує Ŷ = A X̃ та рахує помилки
    """
    X_tilde = augment_with_ones(X)

    print(f"\n=== Метод {method_name} ===")
    print(f"Розмір X̃: {X_tilde.shape}, розмір Y: {Y.shape}")

    start = time.perf_counter()
    # Виклик методу псевдообернення
    X_pinv, iterations = pinv_method(X_tilde)
    elapsed = time.perf_counter() - start

    print(f"Розмір X̃⁺: {X_pinv.shape}")
    print(f"Ітерацій: {iterations}")
    print(f"Час: {elapsed:.6f} c")

    # Перевірка умов Мура–Пенроуза (вивід в консоль всередині функції)
    # is_pseudoinverse(X_tilde, X_pinv) 

    # Оператор A = Y X̃⁺
    A = Y @ X_pinv
    print(f"Розмір оператора A: {A.shape}")

    # Відновлений вихід Ŷ = A X̃
    Y_hat = A @ X_tilde
    print(f"Розмір Ŷ: {Y_hat.shape}")

    # Помилки
    error_norm, mse, rmse = compute_errors(Y, Y_hat)
    print(f"L1 = {error_norm:.6f}")
    print(f"MSE = {mse:.6e}")
    print(f"RMSE = {rmse:.6e}")

    # Обрізаємо до [0, 1] для коректного відображення
    Y_hat = np.clip(Y_hat, 0.0, 1.0)

    return Y_hat, error_norm, mse, rmse, elapsed


def main():
    # === Вхідні зображення ===
    file_x = "x1.bmp"
    file_y = "y3.bmp"  
    
    print(f"Завантаження {file_x}...")
    try:
        X = read_grayscale_image(file_x)
    except FileNotFoundError:
        print(f"Файл {file_x} не знайдено. Перевірте папку.")
        return

    print(f"Завантаження та підгонка {file_y}...")
    try:
        # Тут ми використовуємо нашу нову функцію, щоб підігнати Y під розмір X
        Y = read_and_resize(file_y, X.shape)
    except FileNotFoundError:
        print(f"Файл {file_y} не знайдено. Перевірте папку.")
        return

    print(f"X shape = {X.shape}")
    print(f"Y shape = {Y.shape}")

    X_mat = X.copy()
    Y_mat = Y.copy()

    # === Мур–Пенроуз ===
    Y_hat_MP, err_MP, mse_MP, rmse_MP, time_MP = build_operator_and_predict(
        X_mat, Y_mat, pseudo_inverse_moore_penrose, "Мур–Пенроуз"
    )
    save_grayscale_image("result_moore_penrose.bmp", Y_hat_MP)

    # === Гревіль ===
    Y_hat_G, err_G, mse_G, rmse_G, time_G = build_operator_and_predict(
        X_mat, Y_mat, pseudo_inverse_greville, "Гревіль"
    )
    save_grayscale_image("result_greville.bmp", Y_hat_G)

    # === Порівняння в консолі ===
    print("\n=== Порівняння методів ===")
    print(f"Мур–Пенроуз: час = {time_MP:.6f} с, RMSE = {rmse_MP:.6e}")
    print(f"Гревіль    : час = {time_G:.6f} с, RMSE = {rmse_G:.6e}")

    if rmse_MP < rmse_G:
        print("Метод Мур–Пенроуза дав точніший результат.")
    elif rmse_MP > rmse_G:
        print("Метод Гревіля дав точніший результат.")
    else:
        print("Методи дали однаковий результат (в межах похибки).")

    # === Графічне порівняння ===
    os.makedirs("results", exist_ok=True)

    fig = plt.figure(figsize=(16, 10))

    # 1. Вхід X
    ax1 = plt.subplot(2, 4, 1)
    im1 = ax1.imshow(X_mat, cmap="gray", vmin=0, vmax=1)
    ax1.set_title("Вхідне зображення X")
    ax1.axis("off")
    plt.colorbar(im1, ax=ax1, fraction=0.046)

    # 2. Ціль Y
    ax2 = plt.subplot(2, 4, 2)
    im2 = ax2.imshow(Y_mat, cmap="gray", vmin=0, vmax=1)
    ax2.set_title("Цільове зображення Y")
    ax2.axis("off")
    plt.colorbar(im2, ax=ax2, fraction=0.046)

    # 3. Результат Мур–Пенроуз
    ax3 = plt.subplot(2, 4, 3)
    im3 = ax3.imshow(Y_hat_MP, cmap="gray", vmin=0, vmax=1)
    ax3.set_title(f"Мур–Пенроуз\nRMSE = {rmse_MP:.4f}")
    ax3.axis("off")
    plt.colorbar(im3, ax=ax3, fraction=0.046)

    # 4. Результат Гревіль
    ax4 = plt.subplot(2, 4, 4)
    im4 = ax4.imshow(Y_hat_G, cmap="gray", vmin=0, vmax=1)
    ax4.set_title(f"Гревіль\nRMSE = {rmse_G:.4f}")
    ax4.axis("off")
    plt.colorbar(im4, ax=ax4, fraction=0.046)

    # 5. Різниця |Y − Ŷ_MP|
    diff_MP = np.abs(Y_mat - Y_hat_MP)
    ax5 = plt.subplot(2, 4, 5)
    im5 = ax5.imshow(diff_MP, cmap="hot", vmin=0, vmax=diff_MP.max())
    ax5.set_title(f"|Y − Ŷ_MP|, max = {diff_MP.max():.4f}")
    ax5.axis("off")
    plt.colorbar(im5, ax=ax5, fraction=0.046)

    # 6. Різниця |Y − Ŷ_G|
    diff_G = np.abs(Y_mat - Y_hat_G)
    ax6 = plt.subplot(2, 4, 6)
    im6 = ax6.imshow(diff_G, cmap="hot", vmin=0, vmax=diff_G.max())
    ax6.set_title(f"|Y − Ŷ_G|, max = {diff_G.max():.4f}")
    ax6.axis("off")
    plt.colorbar(im6, ax=ax6, fraction=0.046)

    # 7. Барчарт часу
    ax7 = plt.subplot(2, 4, 7)
    methods = ["Мур–Пенроуз", "Гревіль"]
    times = [time_MP, time_G]
    bars_time = ax7.bar(methods, times)
    ax7.set_title("Час виконання")
    ax7.set_ylabel("секунди")
    ax7.grid(axis="y", alpha=0.3)
    for bar, t in zip(bars_time, times):
        height = bar.get_height()
        ax7.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{t:.3f}s",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    # 8. Барчарт RMSE
    ax8 = plt.subplot(2, 4, 8)
    rmses = [rmse_MP, rmse_G]
    bars_rmse = ax8.bar(methods, rmses)
    ax8.set_title("Помилка RMSE")
    ax8.set_ylabel("RMSE")
    ax8.grid(axis="y", alpha=0.3)
    for bar, r in zip(bars_rmse, rmses):
        height = bar.get_height()
        ax8.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{r:.4f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()
    out_path = os.path.join("results", "comparison_dashboard.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"\nГрафічний підсумок збережено у файлі: {out_path}")
    
    # Показуємо вікно з графіками
    plt.show()

if __name__ == "__main__":
    main()