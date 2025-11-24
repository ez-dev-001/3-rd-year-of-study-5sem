package model;

import java.util.Objects;

// Абстрактний клас (вимога ООП)
public abstract class Tariff implements Comparable<Tariff> {
    private String name;
    private double monthlyFee;
    private int clientsCount;

    public Tariff(String name, double monthlyFee, int clientsCount) {
        this.name = name;
        this.monthlyFee = monthlyFee;
        this.clientsCount = clientsCount;
    }

    public String getName() { return name; }
    public double getMonthlyFee() { return monthlyFee; }
    public int getClientsCount() { return clientsCount; }

    // Абстрактний метод
    public abstract String getDetails();

    @Override
    public int compareTo(Tariff other) {
        return Double.compare(this.monthlyFee, other.monthlyFee);
    }

    @Override
    public String toString() {
        return String.format("| %-12s | %8.2f грн | %6d клієнтів | %s", 
                             name, monthlyFee, clientsCount, getDetails());
    }

    // Вкладені класи (щоб не плодити файли)
    public static class Basic extends Tariff {
        private int minutes;
        public Basic(String name, double fee, int clients, int minutes) {
            super(name, fee, clients);
            this.minutes = minutes;
        }
        @Override
        public String getDetails() { return "Хвилин: " + minutes; }
    }

    public static class Internet extends Tariff {
        private int gigabytes;
        public Internet(String name, double fee, int clients, int gigabytes) {
            super(name, fee, clients);
            this.gigabytes = gigabytes;
        }
        @Override
        public String getDetails() { return "Інтернет: " + gigabytes + " ГБ"; }
    }

    public static class Premium extends Tariff {
        private boolean roaming;
        public Premium(String name, double fee, int clients, boolean roaming) {
            super(name, fee, clients);
            this.roaming = roaming;
        }
        @Override
        public String getDetails() { return "Роумінг: " + (roaming ? "Так" : "Ні"); }
    }

    // Фабрика для створення
    public static Tariff create(String type, String name, double fee, int clients, int param) {
        switch (type.toLowerCase()) {
            case "basic": return new Basic(name, fee, clients, param);
            case "internet": return new Internet(name, fee, clients, param);
            case "premium": return new Premium(name, fee, clients, param == 1);
            default: return null;
        }
    }
}