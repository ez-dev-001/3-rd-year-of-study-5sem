package ua.knu;

import org.junit.jupiter.api.Test;
import ua.knu.controller.DOMPageParser;
import ua.knu.controller.SAXPageParser;
import ua.knu.controller.StAXPageParser;
import ua.knu.model.Page;

import java.util.List;
import static org.junit.jupiter.api.Assertions.*;

class PageParserTest {
    private final String XML_PATH = "xml/pages.xml";

    @Test
    void testDOMParser() throws Exception {
        DOMPageParser parser = new DOMPageParser();
        List<Page> pages = parser.parse(XML_PATH);
        assertNotNull(pages);
        assertFalse(pages.isEmpty());
        assertEquals("Portal", pages.get(0).getType());
    }

    @Test
    void testSAXParser() throws Exception {
        SAXPageParser parser = new SAXPageParser();
        List<Page> pages = parser.parse(XML_PATH);
        assertEquals(4, pages.size()); // У нас 4 сторінки в XML
    }

    @Test
    void testStAXParser() throws Exception {
        StAXPageParser parser = new StAXPageParser();
        List<Page> pages = parser.parse(XML_PATH);
        assertTrue(pages.stream().anyMatch(p -> p.getTitle().contains("BBC")));
    }
}