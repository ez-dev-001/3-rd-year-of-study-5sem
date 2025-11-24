<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" indent="yes"/>
    <xsl:key name="typeKey" match="Page" use="Type"/>

    <xsl:template match="/Site">
        <SiteByTypes>
            <xsl:for-each select="Page[generate-id() = generate-id(key('typeKey', Type)[1])]">
                <xsl:variable name="currentType" select="Type"/>
                <TypeGroup name="{$currentType}">
                    <xsl:for-each select="key('typeKey', $currentType)">
                        <PageItem id="{@id}" auth="{@authorize}">
                            <Title><xsl:value-of select="Title"/></Title>
                        </PageItem>
                    </xsl:for-each>
                </TypeGroup>
            </xsl:for-each>
        </SiteByTypes>
    </xsl:template>
</xsl:stylesheet>