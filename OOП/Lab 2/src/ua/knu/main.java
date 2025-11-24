package ua.knu;

import ua.knu.controller.*;
import ua.knu.model.Page;
import javax.xml.transform.*;
import javax.xml.transform.stream.StreamResult;
import javax.xml.transform.stream.StreamSource;
import java.io.File;
import java.util.Collections;
import java.util.List;
import java.util.logging.Logger;

public class Main {
    private static final Logger logger = Logger.getLogger(Main.class.getName());

    public static void main(String[] args) {
        String xmlPath = "xml/pages.xml";
        String xsdPath = "xml/pages.xsd";
        String xslPath = "xml/pages.xsl";
        String outPath = "xml/pages_new.xml";

        // 1. Валідація
        logger.info("Starting validation...");
        if (XMLValidator.validate(xmlPath, xsdPath)) {
            logger.info("XML is valid.");
        } else {
            logger.severe("XML is Invalid!");
            return;
        }

        try {
            // 2. Парсинг (DOM для прикладу)
            logger.info("Parsing using DOM parser...");
            DOMPageParser parser = new DOMPageParser();
            List<Page> pages = parser.parse(xmlPath);
            
            // 3. Сортування
            logger.info("Sorting pages by Title...");
            Collections.sort(pages, Page.byTitle);
            
            System.out.println("--- Parsed & Sorted Pages ---");
            pages.forEach(System.out::println);

            // 4. XSLT Трансформація
            logger.info("Transforming XML...");
            transform(xmlPath, xslPath, outPath);
            logger.info("Transformation complete. Check " + outPath);

        } catch (Exception e) {
            logger.severe("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private static void transform(String xml, String xsl, String out) throws TransformerException {
        TransformerFactory factory = TransformerFactory.newInstance();
        Transformer transformer = factory.newTransformer(new StreamSource(new File(xsl)));
        transformer.setOutputProperty(OutputKeys.INDENT, "yes");
        transformer.transform(new StreamSource(new File(xml)), new StreamResult(new File(out)));
    }
}