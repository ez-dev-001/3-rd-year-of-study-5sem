package test;

import manager.TariffManager;
import model.Tariff;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

class TariffTest {
    private TariffManager manager;

    @BeforeEach
    void setUp() {
        manager = new TariffManager();
        manager.addTariff(Tariff.create("Basic", "T1", 100, 10, 10));
        manager.addTariff(Tariff.create("Internet", "T2", 200, 20, 20));
    }

    @Test
    void testCountClients() {
        assertEquals(30, manager.countClients());
    }

    @Test
    void testFindInRange() {
        List<Tariff> res = manager.findByPrice(150, 250);
        assertEquals(1, res.size());
        assertEquals("T2", res.get(0).getName());
    }
}