import manager.TariffManager;

public class Main {
    public static void main(String[] args) {
        System.out.println("=== Мобільна Компанія (JSON + Packages) ===");
        
        TariffManager manager = new TariffManager();
        
        // 1. Завантаження (Вимога: файли)
        manager.loadFromJson("data.json");

        // 2. Друк всіх тарифів
        System.out.println("\n--- Всі тарифи ---");
        manager.printAll();

        // 3. Підрахунок клієнтів (Вимога: підрахунок)
        System.out.println("\n--- Всього клієнтів: " + manager.countClients());

        // 4. Сортування (Вимога: сортування)
        System.out.println("\n--- Сортування за ціною ---");
        manager.sortByFee();
        manager.printAll();
        
        // 5. Пошук (Вимога: пошук за діапазоном)
        System.out.println("\n--- Пошук (300-500 грн) ---");
        manager.findByPrice(300, 500).forEach(System.out::println);
    }
}