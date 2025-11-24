package ua.knu.model;

import java.util.Comparator;

public class Page {
    private String id;
    private boolean authorize;
    private String title;
    private String type;
    
    // Характеристики (Chars)
    private String email;
    private boolean hasNews;
    private boolean hasArchive;
    private String voting; // Anonymous, Authorized, None
    private boolean paid;

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public boolean isAuthorize() { return authorize; }
    public void setAuthorize(boolean authorize) { this.authorize = authorize; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getType() { return type; }
    public void setType(String type) { this.type = type; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public boolean isHasNews() { return hasNews; }
    public void setHasNews(boolean hasNews) { this.hasNews = hasNews; }

    public boolean isHasArchive() { return hasArchive; }
    public void setHasArchive(boolean hasArchive) { this.hasArchive = hasArchive; }

    public String getVoting() { return voting; }
    public void setVoting(String voting) { this.voting = voting; }

    public boolean isPaid() { return paid; }
    public void setPaid(boolean paid) { this.paid = paid; }

    @Override
    public String toString() {
        return String.format("Page[ID=%s, Type=%s, Title='%s', Auth=%s, Paid=%s]",
                id, type, title, authorize, paid);
    }

    // Компаратор для сортування за назвою
    public static Comparator<Page> byTitle = Comparator.comparing(Page::getTitle);
}