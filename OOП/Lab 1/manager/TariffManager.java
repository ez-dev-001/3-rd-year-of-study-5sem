package manager;

import model.Tariff;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

public class TariffManager {
    private List<Tariff> tariffs = new ArrayList<>();

    public void addTariff(Tariff t) {
        if (t != null) tariffs.add(t);
    }

    // Метод для завантаження JSON без зовнішніх бібліотек
    public void loadFromJson(String filePath) {
        try {
            String content = new String(Files.readAllBytes(Paths.get(filePath)));
            // Видаляємо квадратні дужки масиву
            content = content.trim().replace("[", "").replace("]", "");
            
            // Розбиваємо на об'єкти по закриваючій дужці
            String[] objects = content.split("},");

            for (String objStr : objects) {
                // Чистимо рядок
                objStr = objStr.replace("{", "").replace("}", "").trim();
                if (objStr.isEmpty()) continue;

                // Парсимо поля вручну
                String type = parseValue(objStr, "type");
                String name = parseValue(objStr, "name");
                double fee = Double.parseDouble(parseValue(objStr, "fee"));
                int clients = Integer.parseInt(parseValue(objStr, "clients"));
                int param = Integer.parseInt(parseValue(objStr, "param"));

                addTariff(Tariff.create(type, name, fee, clients, param));
            }
            System.out.println("Дані з JSON успішно завантажено.");
        } catch (Exception e) {
            System.err.println("Помилка JSON: " + e.getMessage());
        }
    }

    private String parseValue(String json, String key) {
        String search = "\"" + key + "\":";
        int start = json.indexOf(search);
        if (start == -1) return "0"; // Захист
        start += search.length();
        int end = json.indexOf(",", start);
        if (end == -1) end = json.length();
        
        return json.substring(start, end).replace("\"", "").trim();
    }

    public int countClients() {
        return tariffs.stream().mapToInt(Tariff::getClientsCount).sum();
    }

    public void sortByFee() {
        Collections.sort(tariffs);
    }

    public List<Tariff> findByPrice(double min, double max) {
        return tariffs.stream()
                .filter(t -> t.getMonthlyFee() >= min && t.getMonthlyFee() <= max)
                .collect(Collectors.toList());
    }

    public void printAll() {
        tariffs.forEach(System.out::println);
    }
}