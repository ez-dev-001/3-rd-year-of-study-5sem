package ua.knu.controller;

import org.xml.sax.Attributes;
import org.xml.sax.helpers.DefaultHandler;
import ua.knu.model.Page;
import javax.xml.parsers.SAXParser;
import javax.xml.parsers.SAXParserFactory;
import java.io.File;
import java.util.ArrayList;
import java.util.List;

public class SAXPageParser {
    public List<Page> parse(String filePath) throws Exception {
        SAXParserFactory factory = SAXParserFactory.newInstance();
        SAXParser parser = factory.newSAXParser();
        PageHandler handler = new PageHandler();
        parser.parse(new File(filePath), handler);
        return handler.getPages();
    }

    private static class PageHandler extends DefaultHandler {
        private List<Page> pages = new ArrayList<>();
        private Page current;
        private StringBuilder data;

        public List<Page> getPages() { return pages; }

        @Override
        public void startElement(String uri, String localName, String qName, Attributes attributes) {
            data = new StringBuilder();
            if (qName.equalsIgnoreCase("Page")) {
                current = new Page();
                current.setId(attributes.getValue("id"));
                current.setAuthorize(Boolean.parseBoolean(attributes.getValue("authorize")));
            }
        }

        @Override
        public void characters(char[] ch, int start, int length) {
            data.append(new String(ch, start, length));
        }

        @Override
        public void endElement(String uri, String localName, String qName) {
            if (current == null) return;
            switch (qName) {
                case "Title": current.setTitle(data.toString()); break;
                case "Type": current.setType(data.toString()); break;
                case "Email": current.setEmail(data.toString()); break;
                case "HasNews": current.setHasNews(Boolean.parseBoolean(data.toString())); break;
                case "HasArchive": current.setHasArchive(Boolean.parseBoolean(data.toString())); break;
                case "Voting": current.setVoting(data.toString()); break;
                case "Paid": current.setPaid(Boolean.parseBoolean(data.toString())); break;
                case "Page": pages.add(current); break;
            }
        }
    }
}