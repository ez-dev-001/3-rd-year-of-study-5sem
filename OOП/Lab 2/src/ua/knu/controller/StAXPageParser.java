package ua.knu.controller;

import ua.knu.model.Page;
import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLStreamConstants;
import javax.xml.stream.XMLStreamReader;
import java.io.FileInputStream;
import java.util.ArrayList;
import java.util.List;

public class StAXPageParser {
    public List<Page> parse(String filePath) throws Exception {
        List<Page> pages = new ArrayList<>();
        Page current = null;
        String tagContent = null;
        
        XMLInputFactory factory = XMLInputFactory.newInstance();
        XMLStreamReader reader = factory.createXMLStreamReader(new FileInputStream(filePath));

        while (reader.hasNext()) {
            int event = reader.next();
            switch (event) {
                case XMLStreamConstants.START_ELEMENT:
                    if ("Page".equals(reader.getLocalName())) {
                        current = new Page();
                        current.setId(reader.getAttributeValue(null, "id"));
                        current.setAuthorize(Boolean.parseBoolean(reader.getAttributeValue(null, "authorize")));
                    }
                    break;
                case XMLStreamConstants.CHARACTERS:
                    tagContent = reader.getText().trim();
                    break;
                case XMLStreamConstants.END_ELEMENT:
                    if (current != null) {
                        switch (reader.getLocalName()) {
                            case "Title": current.setTitle(tagContent); break;
                            case "Type": current.setType(tagContent); break;
                            case "Email": current.setEmail(tagContent); break;
                            case "HasNews": current.setHasNews(Boolean.parseBoolean(tagContent)); break;
                            case "HasArchive": current.setHasArchive(Boolean.parseBoolean(tagContent)); break;
                            case "Voting": current.setVoting(tagContent); break;
                            case "Paid": current.setPaid(Boolean.parseBoolean(tagContent)); break;
                            case "Page": pages.add(current); break;
                        }
                    }
                    break;
            }
        }
        return pages;
    }
}