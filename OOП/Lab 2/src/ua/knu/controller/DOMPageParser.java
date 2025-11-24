package ua.knu.controller;

import org.w3c.dom.*;
import ua.knu.model.Page;
import javax.xml.parsers.*;
import java.io.File;
import java.util.ArrayList;
import java.util.List;

public class DOMPageParser {
    public List<Page> parse(String filePath) throws Exception {
        List<Page> pages = new ArrayList<>();
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        DocumentBuilder builder = factory.newDocumentBuilder();
        Document doc = builder.parse(new File(filePath));

        NodeList nodeList = doc.getElementsByTagName("Page");

        for (int i = 0; i < nodeList.getLength(); i++) {
            Element elem = (Element) nodeList.item(i);
            Page page = new Page();
            page.setId(elem.getAttribute("id"));
            page.setAuthorize(Boolean.parseBoolean(elem.getAttribute("authorize")));
            
            page.setTitle(getTagValue("Title", elem));
            page.setType(getTagValue("Type", elem));

            // Chars parsing
            Element chars = (Element) elem.getElementsByTagName("Chars").item(0);
            if (chars != null) {
                page.setEmail(getTagValue("Email", chars));
                String news = getTagValue("HasNews", chars);
                page.setHasNews(news != null && Boolean.parseBoolean(news));
                String archive = getTagValue("HasArchive", chars);
                page.setHasArchive(archive != null && Boolean.parseBoolean(archive));
                page.setVoting(getTagValue("Voting", chars));
                page.setPaid(Boolean.parseBoolean(getTagValue("Paid", chars)));
            }
            pages.add(page);
        }
        return pages;
    }

    private String getTagValue(String tag, Element element) {
        NodeList nl = element.getElementsByTagName(tag);
        if (nl != null && nl.getLength() > 0) {
            Node node = nl.item(0).getFirstChild();
            if (node != null) return node.getNodeValue();
        }
        return null;
    }
}