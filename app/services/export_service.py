import io
import csv
import json
import tempfile
import os
from datetime import datetime
from typing import Optional, Dict, List, Any

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    Image, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing, Rect, String, Circle
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF


# =========================
# PALETTE COULEURS PFE - PROFESSIONNELLE
# =========================
BRAND_PRIMARY = colors.HexColor('#1E3A5F')      # Bleu marine profond
BRAND_SECONDARY = colors.HexColor('#2563EB')     # Bleu électrique
BRAND_ACCENT = colors.HexColor('#0EA5E9')       # Cyan

SCORE_EXCELLENT = colors.HexColor('#10B981')     # Vert émeraude
SCORE_GOOD = colors.HexColor('#22C55E')          # Vert clair
SCORE_MODERATE = colors.HexColor('#F59E0B')      # Orange
SCORE_POOR = colors.HexColor('#EF4444')          # Rouge
SCORE_CRITICAL = colors.HexColor('#DC2626')      # Rouge foncé
SCORE_GRAY = colors.HexColor('#6B7280')          # Gris

BG_LIGHT = colors.HexColor('#F8FAFC')
BG_CARD = colors.HexColor('#FFFFFF')
TEXT_DARK = colors.HexColor('#1E293B')
TEXT_MEDIUM = colors.HexColor('#475569')
TEXT_LIGHT = colors.HexColor('#94A3B8')
BORDER_COLOR = colors.HexColor('#E2E8F0')

# Couleurs par catégorie
CAT_TECHNICAL = colors.HexColor('#3B82F6')       # Bleu
CAT_CONTENT = colors.HexColor('#8B5CF6')         # Violet
CAT_UX = colors.HexColor('#10B981')              # Vert
CAT_POPULARITY = colors.HexColor('#F97316')      # Orange


# ============================================================================
# TRANSLATIONS - I18N
# ============================================================================

TRANSLATIONS = {
    "fr": {
        # Header/Footer
        "platform_name": "SEO PLATFORM",
        "confidential": "Rapport confidentiel - PFE 2026",
        "page": "Page",

        # Cover Page
        "report_title": "RAPPORT D'ANALYSE SEO",
        "report_subtitle": "Évaluation complète de la performance web",
        "url_analyzed": "URL Analysée:",
        "analysis_date": "Date d'analyse:",
        "report_type": "Type de rapport:",
        "generated_by": "Généré par:",
        "full_report": "Complet (4 catégories)",
        "global_score": "Score Global SEO",
        "executive_summary": "Résumé Exécutif",
        "issues_found": "problèmes",
        "recommendations_found": "recommandations",
        "optimization_level": "optimisation",

        # Performance Page
        "performance_by_category": "PERFORMANCE PAR CATÉGORIE",
        "category": "Catégorie",
        "score": "Score",
        "progress_bar": "Barre de progression",
        "status": "Status",
        "score_distribution": "Distribution des Scores",

        # Sections
        "technical_seo": "Technical SEO",
        "content_quality": "Content Quality",
        "ux_ui": "UX / UI",
        "popularity": "Popularity",

        # Issues
        "issues_identified": "Problèmes identifiés",
        "no_issues": "✓ Aucun problème majeur identifié dans cette catégorie.",
        "impact": "Impact",
        "solution": "Solution",

        # Recommendations
        "priority_recommendations": "RECOMMANDATIONS PRIORITAIRES",
        "recommendations_count": "recommandations identifiées",
        "no_recommendations": "✓ Aucune recommandation spécifique - votre site est bien optimisé !",
        "effort": "Effort",
        "actions": "Actions",

        # Conclusion
        "conclusion_title": "CONCLUSION ET ACTIONS PRIORITAIRES",
        "strengths": "Points forts",
        "weaknesses": "Points à améliorer prioritairement",
        "next_steps": "Prochaines étapes recommandées",
        "no_strengths": "Aucun point fort majeur identifié",
        "no_weaknesses": "Aucun point critique - continuez à maintenir votre optimisation",
        "step_1": "Corriger les problèmes critiques et haute priorité",
        "step_2": "Implémenter les recommendations par ordre d'impact",
        "step_3": "Relancer une analyse dans 2-4 semaines pour mesurer les progrès",
        "step_4": "Maintenir une veille SEO régulière",
        "footer_note": "Ce rapport a été généré automatiquement par la plateforme SEO.",
        "contact": "Pour toute question, contactez votre équipe SEO.",
        "all_rights": "Confidentiel - PFE 2026 - Tous droits réservés",

        # Score Labels
        "excellent": "Excellent",
        "good": "Bon",
        "moderate": "Modéré",
        "poor": "Faible",
        "critical": "Critique",
        "na": "N/A",

        # Metrics
        "technical_metrics": "Métriques Techniques",
        "content_metrics": "Métriques de Contenu",
        "ux_metrics": "Métriques UX/UI",
        "popularity_metrics": "Métriques de Popularité",
        "meta_tags": "Meta Tags",
        "title": "Titre",
        "description": "Description",
        "load_time": "Temps de chargement",
        "html_size": "Taille HTML",
        "word_count": "Nombre de mots",
        "robots_txt": "robots.txt",
        "sitemap_xml": "Sitemap XML",
        "https": "HTTPS",
        "viewport": "Viewport",
        "charset": "Charset",
        "structured_data": "Données structurées",
        "favicon": "Favicon",
        "present": "✓ Présent",
        "missing": "✗ Manquant",
        "active": "✓ Actif",
        "inactive": "✗ Inactif",
        "declared": "✓ Déclaré",
        "h1_count": "Titres H1",
        "h2_count": "Titres H2",
        "h3_count": "Titres H3",
        "internal_links": "Liens internes",
        "external_links": "Liens externes",
        "nofollow_links": "Liens nofollow",
        "navigation": "Navigation",
        "authority": "Autorité",
        "seo": "SEO",
        "responsive": "Responsive",
        "accessibility": "Accessibilité",
        "text_rendering": "Rendu texte",
        "rich_snippets": "Rich snippets",
        "branding": "Branding",
        "essential": "Essentiel",
        "mandatory": "Obligatoire",
        "mobile": "Mobile",
        "encoding": "Encodage",
        "characters": "caractères",

        # CSV
        "csv_report_title": "RAPPORT SEO - Platform",
        "csv_category": "CATEGORIE",
        "csv_score": "SCORE",
        "csv_status": "STATUS",
        "csv_global_score": "SCORE GLOBAL",
        "csv_priority": "PRIORITE",
        "csv_title_col": "TITRE",
        "csv_description_col": "DESCRIPTION",
        "csv_impact_col": "IMPACT",
        "csv_solution": "SOLUTION",
        "csv_effort": "EFFORT",
    },
    "en": {
        # Header/Footer
        "platform_name": "SEO PLATFORM",
        "confidential": "Confidential Report - PFE 2026",
        "page": "Page",

        # Cover Page
        "report_title": "SEO ANALYSIS REPORT",
        "report_subtitle": "Complete web performance evaluation",
        "url_analyzed": "Analyzed URL:",
        "analysis_date": "Analysis Date:",
        "report_type": "Report Type:",
        "generated_by": "Generated by:",
        "full_report": "Full (4 categories)",
        "global_score": "Global SEO Score",
        "executive_summary": "Executive Summary",
        "issues_found": "issues",
        "recommendations_found": "recommendations",
        "optimization_level": "optimization",

        # Performance Page
        "performance_by_category": "PERFORMANCE BY CATEGORY",
        "category": "Category",
        "score": "Score",
        "progress_bar": "Progress Bar",
        "status": "Status",
        "score_distribution": "Score Distribution",

        # Sections
        "technical_seo": "Technical SEO",
        "content_quality": "Content Quality",
        "ux_ui": "UX / UI",
        "popularity": "Popularity",

        # Issues
        "issues_identified": "Issues Identified",
        "no_issues": "✓ No major issues identified in this category.",
        "impact": "Impact",
        "solution": "Solution",

        # Recommendations
        "priority_recommendations": "PRIORITY RECOMMENDATIONS",
        "recommendations_count": "recommendations identified",
        "no_recommendations": "✓ No specific recommendations - your site is well optimized!",
        "effort": "Effort",
        "actions": "Actions",

        # Conclusion
        "conclusion_title": "CONCLUSION AND PRIORITY ACTIONS",
        "strengths": "Strengths",
        "weaknesses": "Areas to improve urgently",
        "next_steps": "Recommended Next Steps",
        "no_strengths": "No major strengths identified",
        "no_weaknesses": "No critical issues - continue maintaining your optimization",
        "step_1": "Fix critical and high priority issues",
        "step_2": "Implement recommendations by impact order",
        "step_3": "Re-run analysis in 2-4 weeks to measure progress",
        "step_4": "Maintain regular SEO monitoring",
        "footer_note": "This report was automatically generated by the SEO platform.",
        "contact": "For any questions, contact your SEO team.",
        "all_rights": "Confidential - PFE 2026 - All rights reserved",

        # Score Labels
        "excellent": "Excellent",
        "good": "Good",
        "moderate": "Moderate",
        "poor": "Poor",
        "critical": "Critical",
        "na": "N/A",

        # Metrics
        "technical_metrics": "Technical Metrics",
        "content_metrics": "Content Metrics",
        "ux_metrics": "UX/UI Metrics",
        "popularity_metrics": "Popularity Metrics",
        "meta_tags": "Meta Tags",
        "title": "Title",
        "description": "Description",
        "load_time": "Load Time",
        "html_size": "HTML Size",
        "word_count": "Word Count",
        "robots_txt": "robots.txt",
        "sitemap_xml": "Sitemap XML",
        "https": "HTTPS",
        "viewport": "Viewport",
        "charset": "Charset",
        "structured_data": "Structured Data",
        "favicon": "Favicon",
        "present": "✓ Present",
        "missing": "✗ Missing",
        "active": "✓ Active",
        "inactive": "✗ Inactive",
        "declared": "✓ Declared",
        "h1_count": "H1 Titles",
        "h2_count": "H2 Titles",
        "h3_count": "H3 Titles",
        "internal_links": "Internal Links",
        "external_links": "External Links",
        "nofollow_links": "Nofollow Links",
        "navigation": "Navigation",
        "authority": "Authority",
        "seo": "SEO",
        "responsive": "Responsive",
        "accessibility": "Accessibility",
        "text_rendering": "Text Rendering",
        "rich_snippets": "Rich Snippets",
        "branding": "Branding",
        "essential": "Essential",
        "mandatory": "Mandatory",
        "mobile": "Mobile",
        "encoding": "Encoding",
        "characters": "characters",

        # CSV
        "csv_report_title": "SEO REPORT - Platform",
        "csv_category": "CATEGORY",
        "csv_score": "SCORE",
        "csv_status": "STATUS",
        "csv_global_score": "GLOBAL SCORE",
        "csv_priority": "PRIORITY",
        "csv_title_col": "TITLE",
        "csv_description_col": "DESCRIPTION",
        "csv_impact_col": "IMPACT",
        "csv_solution": "SOLUTION",
        "csv_effort": "EFFORT",
    }
}


class NumberedCanvas(canvas.Canvas):
    """Canvas avec numéros de page et header/footer"""

    def __init__(self, *args, lang="fr", **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        self.lang = lang
        self._trans = TRANSLATIONS.get(lang, TRANSLATIONS["fr"])

    def _t(self, key):
        return self._trans.get(key, key)

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """Ajouter header/footer sur chaque page"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_header_footer(self, num_pages):
        """Dessiner header et footer sur chaque page"""
        page_num = self._pageNumber

        # Header - Bandeau supérieur
        self.setFillColor(BRAND_PRIMARY)
        self.rect(0, A4[1] - 15*mm, A4[0], 15*mm, fill=1, stroke=0)

        # Logo texte dans header
        self.setFillColor(colors.white)
        self.setFont("Helvetica-Bold", 10)
        self.drawString(15*mm, A4[1] - 10*mm, "SEO PLATFORM")

        # Date dans header
        self.setFont("Helvetica", 8)
        self.drawRightString(A4[0] - 15*mm, A4[1] - 10*mm, 
                           datetime.now().strftime("%d/%m/%Y"))

        # Footer - Bandeau inférieur
        self.setFillColor(BRAND_PRIMARY)
        self.rect(0, 0, A4[0], 12*mm, fill=1, stroke=0)

        # Texte footer
        self.setFillColor(colors.white)
        self.setFont("Helvetica", 8)
        self.drawString(15*mm, 4*mm, self._t("confidential"))
        self.drawRightString(A4[0] - 15*mm, 4*mm, 
                           f"{self._t('page')} {page_num}/{num_pages}")


class ExportService:

    def __init__(self, lang: str = "fr"):
        self.lang = lang if lang in TRANSLATIONS else "fr"
        self.t = TRANSLATIONS[self.lang]
        self.styles = self._create_styles()

    def _t(self, key: str) -> str:
        """Get translated text"""
        return self.t.get(key, key)

    def _create_styles(self):
        """Créer les styles personnalisés"""
        styles = getSampleStyleSheet()

        # Style titre principal
        styles.add(ParagraphStyle(
            'MainTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=BRAND_PRIMARY,
            alignment=TA_CENTER,
            spaceAfter=30,
            fontName='Helvetica-Bold',
            leading=34
        ))

        # Style sous-titre
        styles.add(ParagraphStyle(
            'SubTitle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=TEXT_MEDIUM,
            alignment=TA_CENTER,
            spaceAfter=20,
            leading=18
        ))

        # Style section header
        styles.add(ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=BRAND_PRIMARY,
            spaceBefore=20,
            spaceAfter=15,
            fontName='Helvetica-Bold',
            borderColor=BRAND_SECONDARY,
            borderWidth=2,
            borderPadding=5,
            leftIndent=0,
            leading=22
        ))

        # Style sous-section
        styles.add(ParagraphStyle(
            'SubSection',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=TEXT_DARK,
            spaceBefore=15,
            spaceAfter=10,
            fontName='Helvetica-Bold',
            leading=18
        ))

        # Style texte normal
        styles.add(ParagraphStyle(
            'CustomBodyText',
            parent=styles['Normal'],
            fontSize=10,
            textColor=TEXT_MEDIUM,
            alignment=TA_JUSTIFY,
            leading=14,
            spaceAfter=8
        ))

        # Style pour issues
        styles.add(ParagraphStyle(
            'IssueTitle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=SCORE_CRITICAL,
            fontName='Helvetica-Bold',
            leading=14,
            spaceAfter=4
        ))

        styles.add(ParagraphStyle(
            'IssueText',
            parent=styles['Normal'],
            fontSize=9,
            textColor=TEXT_MEDIUM,
            leading=12,
            spaceAfter=8,
            leftIndent=15
        ))

        # Style pour recommendations
        styles.add(ParagraphStyle(
            'RecTitle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=BRAND_SECONDARY,
            fontName='Helvetica-Bold',
            leading=14,
            spaceAfter=4
        ))

        # Style pour métriques
        styles.add(ParagraphStyle(
            'MetricValue',
            parent=styles['Normal'],
            fontSize=20,
            textColor=BRAND_PRIMARY,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            leading=24
        ))

        styles.add(ParagraphStyle(
            'MetricLabel',
            parent=styles['Normal'],
            fontSize=9,
            textColor=TEXT_LIGHT,
            alignment=TA_CENTER,
            leading=12
        ))

        # Style badge priorité
        styles.add(ParagraphStyle(
            'BadgeText',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.white,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        return styles

    # =========================
    # SCORE COLOR
    # =========================
    def _get_score_color(self, score: Any):
        try:
            s = float(score)
            if s >= 80:
                return SCORE_EXCELLENT
            elif s >= 60:
                return SCORE_GOOD
            elif s >= 40:
                return SCORE_MODERATE
            elif s >= 20:
                return SCORE_POOR
            else:
                return SCORE_CRITICAL
        except:
            return SCORE_GRAY

    def _get_score_label(self, score: Any):
        try:
            s = float(score)
            if s >= 80:
                return self._t("excellent")
            elif s >= 60:
                return self._t("good")
            elif s >= 40:
                return self._t("moderate")
            elif s >= 20:
                return self._t("poor")
            else:
                return self._t("critical")
        except:
            return self._t("na")

    def _get_category_color(self, category: str):
        colors_map = {
            'technical': CAT_TECHNICAL,
            'content': CAT_CONTENT,
            'ux': CAT_UX,
            'popularity': CAT_POPULARITY
        }
        return colors_map.get(category.lower(), BRAND_SECONDARY)

    def _get_category_label(self, key: str) -> str:
        labels = {
            'technical': self._t("technical_seo"),
            'content': self._t("content_quality"),
            'ux': self._t("ux_ui"),
            'popularity': self._t("popularity"),
        }
        return labels.get(key, key)

    # =========================
    # DRAW GAUGE
    # =========================
    def _draw_gauge(self, score: float, size: int = 120):
        """Créer un drawing de gauge circulaire"""
        d = Drawing(size, size)

        d.add(Circle(size/2, size/2, size/2 - 5, 
                    fillColor=colors.HexColor('#E2E8F0'), 
                    strokeColor=None))

        color = self._get_score_color(score)

        d.add(Circle(size/2, size/2, (size/2 - 5) * (score/100),
                    fillColor=color, strokeColor=None, 
                    fillOpacity=0.8))

        d.add(Circle(size/2, size/2, size/3,
                    fillColor=colors.white, strokeColor=None))

        d.add(String(size/2, size/2 + 5, str(int(score)),
                    fontName='Helvetica-Bold', fontSize=24,
                    fillColor=TEXT_DARK, textAnchor='middle'))

        d.add(String(size/2, size/2 - 15, "/100",
                    fontName='Helvetica', fontSize=10,
                    fillColor=TEXT_LIGHT, textAnchor='middle'))

        return d

    # =========================
    # CREATE SCORE CARD TABLE
    # =========================
    def _create_score_card(self, label: str, score: float, color: colors.Color):
        """Créer une carte de score visuelle"""
        data = [
            [Paragraph(f"<b>{label}</b>", self.styles['MetricLabel'])],
            [Paragraph(f"<font size=24 color={color.hexval()}><b>{int(score)}</b></font><font size=10 color='#94A3B8'>/100</font>", 
                      self.styles['MetricValue'])],
            [Paragraph(f"<font size=8 color={color.hexval()}>● {self._get_score_label(score)}</font>", 
                      self.styles['MetricLabel'])]
        ]

        t = Table(data, colWidths=[6*cm], rowHeights=[0.8*cm, 1.5*cm, 0.6*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('ROUNDEDCORNERS', [5, 5, 5, 5]),
        ]))
        return t

    # =========================
    # CREATE PROGRESS BAR
    # =========================
    def _create_progress_bar(self, score: float, width: float = 14*cm, height: float = 0.6*cm):
        """Créer une barre de progression visuelle"""
        color = self._get_score_color(score)

        bg = Rect(0, 0, width, height, 
                 fillColor=colors.HexColor('#E2E8F0'), 
                 strokeColor=None, rx=height/2)

        bar_width = width * (score / 100)
        bar = Rect(0, 0, bar_width, height,
                  fillColor=color, strokeColor=None, rx=height/2)

        d = Drawing(width, height)
        d.add(bg)
        d.add(bar)

        return d

    # =========================
    # CREATE ISSUE CARD
    # =========================
    def _create_issue_card(self, issue: Dict, category: str = ""):
        """Créer une carte d'issue détaillée"""
        priority = issue.get('priority', 'medium')
        priority_colors = {
            'critical': ('#DC2626', '#FEE2E2'),
            'high': ('#EF4444', '#FEE2E2'),
            'medium': ('#F59E0B', '#FEF3C7'),
            'low': ('#3B82F6', '#DBEAFE')
        }
        text_color, bg_color = priority_colors.get(priority, ('#6B7280', '#F3F4F6'))

        title = issue.get('title', '')
        description = issue.get('description', '')
        impact = issue.get('impact', '')
        solution = issue.get('solution', '')

        data = [
            [Paragraph(f"<font color='{text_color}'>● <b>{title}</b></font>", self.styles['IssueTitle'])],
            [Paragraph(f"<font color='#475569'>{description}</font>", self.styles['IssueText'])],
        ]

        if impact:
            data.append([Paragraph(f"<font color='#EF4444' size=8><b>{self._t('impact')}:</b> {impact}</font>", 
                          self.styles['IssueText'])])

        if solution:
            data.append([Paragraph(f"<font color='#2563EB' size=8><b>{self._t('solution')}:</b> {solution}</font>", 
                          self.styles['IssueText'])])

        t = Table(data, colWidths=[16*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(bg_color)),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor(text_color)),
            ('ROUNDEDCORNERS', [4, 4, 4, 4]),
        ]))

        return t

    # =========================
    # CREATE RECOMMENDATION CARD
    # =========================
    def _create_recommendation_card(self, rec: Dict):
        """Créer une carte de recommendation détaillée"""
        priority = rec.get('priority', 'medium')
        category = rec.get('category', 'technical')

        priority_colors = {
            'high': ('#DC2626', '#FEE2E2'),
            'medium': ('#F59E0B', '#FEF3C7'),
            'low': ('#3B82F6', '#DBEAFE')
        }
        text_color, bg_color = priority_colors.get(priority, ('#6B7280', '#F3F4F6'))
        cat_color = self._get_category_color(category)

        title = rec.get('title', '')
        description = rec.get('description', '')
        impact = rec.get('impact', '')
        effort = rec.get('effort', rec.get('time', ''))
        steps = rec.get('steps', rec.get('actions', []))

        badge = Table([[Paragraph(f"<b>{priority.upper()}</b>", self.styles['BadgeText'])]], 
                     colWidths=[2*cm], rowHeights=[0.5*cm])
        badge.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(text_color)),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROUNDEDCORNERS', [3, 3, 3, 3]),
        ]))

        cat_badge = Table([[Paragraph(f"<b>{category.upper()}</b>", self.styles['BadgeText'])]], 
                         colWidths=[2.5*cm], rowHeights=[0.5*cm])
        cat_badge.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), cat_color),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROUNDEDCORNERS', [3, 3, 3, 3]),
        ]))

        data = [
            [[badge, cat_badge], Paragraph(f"<b>{title}</b>", self.styles['RecTitle'])],
            ['', Paragraph(f"<font color='#475569' size=9>{description}</font>", self.styles['CustomBodyText'])],
        ]

        if impact:
            data.append(['', Paragraph(f"<font color='#059669' size=8>📈 {self._t('impact')}: {impact}</font>", 
                              self.styles['CustomBodyText'])])

        if effort:
            data.append(['', Paragraph(f"<font color='#7C3AED' size=8>⏱ {self._t('effort')}: {effort}</font>", 
                              self.styles['CustomBodyText'])])

        if steps and len(steps) > 0:
            steps_text = "<br/>".join([f"  {i+1}. {step}" for i, step in enumerate(steps[:3])])
            data.append(['', Paragraph(f"<font color='#475569' size=8><b>{self._t('actions')}:</b><br/>{steps_text}</font>", 
                              self.styles['CustomBodyText'])])

        t = Table(data, colWidths=[3*cm, 13*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(bg_color)),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (0, -1), 'TOP'),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('ROUNDEDCORNERS', [6, 6, 6, 6]),
        ]))

        return t

    # =========================
    # MAIN PDF EXPORT
    # =========================
    async def generate_pdf(
        self,
        data: Dict[str, Any],
        user_id: Optional[str] = None,
        task_id: Optional[str] = None,
        include_charts: bool = True
    ) -> str:

        buffer = io.BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=2.2 * cm,
            bottomMargin=1.8 * cm
        )

        story = []
        styles = self.styles

        meta = data.get("meta", {})
        url = meta.get('url_analyzed', meta.get('url', 'N/A'))
        section = meta.get('section', 'full')

        scores = data.get("scores", {})
        global_score = scores.get("global", 0)

        # =====================================================================
        # PAGE 1: COVER PAGE
        # =====================================================================
        story.append(Spacer(1, 3*cm))

        story.append(Paragraph(self._t("report_title"), styles['MainTitle']))
        story.append(Paragraph(self._t("report_subtitle"), styles['SubTitle']))

        story.append(Spacer(1, 1.5*cm))

        story.append(HRFlowable(width="80%", thickness=2, color=BRAND_SECONDARY, 
                               spaceBefore=10, spaceAfter=10, hAlign='CENTER'))

        story.append(Spacer(1, 1*cm))

        info_data = [
            [Paragraph(f"<b>{self._t('url_analyzed')}</b>", styles['CustomBodyText']), 
             Paragraph(f"<font color='#2563EB'>{url}</font>", styles['CustomBodyText'])],
            [Paragraph(f"<b>{self._t('analysis_date')}</b>", styles['CustomBodyText']), 
             Paragraph(datetime.now().strftime("%d %B %Y %H:%M"), styles['CustomBodyText'])],
            [Paragraph(f"<b>{self._t('report_type')}</b>", styles['CustomBodyText']), 
             Paragraph(section.upper() if section != 'full' else self._t("full_report"), styles['CustomBodyText'])],
            [Paragraph(f"<b>{self._t('generated_by')}</b>", styles['CustomBodyText']), 
             Paragraph("SEO Platform - PFE 2026", styles['CustomBodyText'])],
        ]

        info_table = Table(info_data, colWidths=[5*cm, 10*cm])
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(info_table)

        story.append(Spacer(1, 2*cm))

        score_color = self._get_score_color(global_score)
        score_label = self._get_score_label(global_score)

        score_data = [
            [Paragraph(f"<font size=48 color='{score_color.hexval()}'><b>{int(global_score)}</b></font>", styles['MetricValue'])],
            [Paragraph(f"<font size=14 color='#475569'>{self._t('global_score')}</font>", styles['MetricLabel'])],
            [Paragraph(f"<font size=12 color='{score_color.hexval()}'>● {score_label}</font>", styles['MetricLabel'])],
        ]

        score_table = Table(score_data, colWidths=[8*cm], rowHeights=[2*cm, 0.8*cm, 0.6*cm])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
            ('BOX', (0, 0), (-1, -1), 2, score_color),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('ROUNDEDCORNERS', [10, 10, 10, 10]),
        ]))
        story.append(score_table)

        story.append(Spacer(1, 2*cm))

        story.append(Paragraph(f"<b>{self._t('executive_summary')}</b>", styles['SubSection']))

        total_issues = sum(len(data.get(k, {}).get('issues', [])) for k in ['technical', 'content', 'ux', 'popularity'] if k in data)
        total_recos = 0
        if 'recommendations' in data:
            recos = data['recommendations']
            if isinstance(recos, dict):
                total_recos = sum(len(v) for v in recos.values() if isinstance(v, list))
            elif isinstance(recos, list):
                total_recos = len(recos)

        summary_text = f"""
        {self._t('executive_summary')} <b>{url}</b>. 
        {self._t('global_score')} <b>{int(global_score)}/100</b> - {self._t('optimization_level')} 
        <font color='{score_color.hexval()}'>{score_label.lower()}</font>. 
        <b>{total_issues}</b> {self._t('issues_found')} | <b>{total_recos}</b> {self._t('recommendations_found')}.
        """
        story.append(Paragraph(summary_text, styles['CustomBodyText']))

        story.append(PageBreak())

        # =====================================================================
        # PAGE 2: SCORES PAR CATÉGORIE
        # =====================================================================
        story.append(Paragraph(self._t("performance_by_category"), styles['SectionHeader']))
        story.append(Spacer(1, 0.5*cm))

        cat_data = [[Paragraph(f"<b>{self._t('category')}</b>", styles['CustomBodyText']), 
                    Paragraph(f"<b>{self._t('score')}</b>", styles['CustomBodyText']),
                    Paragraph(f"<b>{self._t('progress_bar')}</b>", styles['CustomBodyText']),
                    Paragraph(f"<b>{self._t('status')}</b>", styles['CustomBodyText'])]]

        categories = [
            ('technical', self._t('technical_seo'), CAT_TECHNICAL),
            ('content', self._t('content_quality'), CAT_CONTENT),
            ('ux', self._t('ux_ui'), CAT_UX),
            ('popularity', self._t('popularity'), CAT_POPULARITY)
        ]

        for key, label, color in categories:
            if key in data or section == 'full':
                score = data.get(key, {}).get('score', scores.get(key, 0))
                status = self._get_score_label(score)
                score_color = self._get_score_color(score)

                bar_filled = int((score / 100) * 20)
                bar_empty = 20 - bar_filled
                bar = "█" * bar_filled + "░" * bar_empty

                cat_data.append([
                    Paragraph(f"<font color='{color.hexval()}'><b>{label}</b></font>", styles['CustomBodyText']),
                    Paragraph(f"<b>{int(score)}</b>/100", styles['CustomBodyText']),
                    Paragraph(f"<font color='{score_color.hexval()}'>{bar}</font>", styles['CustomBodyText']),
                    Paragraph(f"<font color='{score_color.hexval()}'><b>{status}</b></font>", styles['CustomBodyText'])
                ])

        cat_table = Table(cat_data, colWidths=[5*cm, 3*cm, 6*cm, 3*cm])
        cat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BRAND_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
        ]))
        story.append(cat_table)

        story.append(Spacer(1, 1*cm))

        story.append(Paragraph(f"<b>{self._t('score_distribution')}</b>", styles['SubSection']))

        for key, label, color in categories:
            if key in data or section == 'full':
                score = data.get(key, {}).get('score', scores.get(key, 0))
                bar_width = int((score / 100) * 50)
                bar = "█" * bar_width
                story.append(Paragraph(
                    f"<font color='{color.hexval()}'>{label:20}</font> {bar} <b>{int(score)}%</b>",
                    styles['CustomBodyText']
                ))

        story.append(PageBreak())

        # =====================================================================
        # SECTIONS DÉTAILLÉES
        # =====================================================================

        for key, label, color in categories:
            if key not in data and section != 'full':
                continue

            section_data = data.get(key, {})
            if not section_data and section != 'full':
                continue

            score = section_data.get('score', scores.get(key, 0))
            issues = section_data.get('issues', [])

            story.append(Paragraph(f"{label.upper()}", styles['SectionHeader']))
            story.append(Spacer(1, 0.3*cm))

            score_color = self._get_score_color(score)
            story.append(Paragraph(
                f"{self._t('score')}: <font color='{score_color.hexval()}'><b>{int(score)}</b></font>/100 - "
                f"<font color='{score_color.hexval()}'>{self._get_score_label(score)}</font>",
                styles['SubSection']
            ))

            bar_width = int((score / 100) * 50)
            bar = "█" * bar_width + "░" * (50 - bar_width)
            story.append(Paragraph(
                f"<font color='{score_color.hexval()}'>{bar}</font>",
                styles['CustomBodyText']
            ))

            story.append(Spacer(1, 0.5*cm))

            if key == 'technical' and 'raw_data' in data:
                self._add_technical_metrics(story, data.get('raw_data', {}), styles)
            elif key == 'content' and 'raw_data' in data:
                self._add_content_metrics(story, data.get('raw_data', {}), styles)
            elif key == 'ux' and 'raw_data' in data:
                self._add_ux_metrics(story, data.get('raw_data', {}), styles)
            elif key == 'popularity' and 'raw_data' in data:
                self._add_popularity_metrics(story, data.get('raw_data', {}), styles)

            if issues:
                story.append(Paragraph(f"<b>{self._t('issues_identified')} ({len(issues)})</b>", styles['SubSection']))
                story.append(Spacer(1, 0.3*cm))

                for issue in issues:
                    story.append(self._create_issue_card(issue, key))
                    story.append(Spacer(1, 0.3*cm))
            else:
                story.append(Paragraph(
                    self._t("no_issues"),
                    styles['CustomBodyText']
                ))

            story.append(PageBreak())

        # =====================================================================
        # PAGE RECOMMENDATIONS
        # =====================================================================
        story.append(Paragraph(self._t("priority_recommendations"), styles['SectionHeader']))
        story.append(Spacer(1, 0.5*cm))

        recommendations = data.get('recommendations', {})
        all_recos = []

        if isinstance(recommendations, dict):
            for priority in ['critical', 'high', 'medium', 'low']:
                recos = recommendations.get(priority, [])
                for rec in recos:
                    rec['priority'] = priority
                    all_recos.append(rec)
        elif isinstance(recommendations, list):
            all_recos = recommendations

        if all_recos:
            story.append(Paragraph(f"<b>{len(all_recos)} {self._t('recommendations_count')}</b>", styles['SubSection']))
            story.append(Spacer(1, 0.3*cm))

            for rec in all_recos:
                story.append(self._create_recommendation_card(rec))
                story.append(Spacer(1, 0.3*cm))
        else:
            story.append(Paragraph(
                self._t("no_recommendations"),
                styles['CustomBodyText']
            ))

        story.append(PageBreak())

        # =====================================================================
        # PAGE CONCLUSION
        # =====================================================================
        story.append(Paragraph(self._t("conclusion_title"), styles['SectionHeader']))
        story.append(Spacer(1, 0.5*cm))

        conclusion_text = f"""
        {self._t('conclusion_title')} <b>{url}</b> - <b>{int(global_score)}/100</b>, 
        {self._t('status')}: <font color='{score_color.hexval()}'>{score_label}</font>.
        <br/><br/>
        <b>{self._t('strengths')}:</b><br/>
        """

        strengths = []
        for key, label, color in categories:
            s = data.get(key, {}).get('score', scores.get(key, 0))
            if s >= 60:
                strengths.append(f"• {label}: {int(s)}/100")

        if strengths:
            conclusion_text += "<br/>".join(strengths)
        else:
            conclusion_text += f"• {self._t('no_strengths')}"

        conclusion_text += f"<br/><br/><b>{self._t('weaknesses')}:</b><br/>"

        weaknesses = []
        for key, label, color in categories:
            s = data.get(key, {}).get('score', scores.get(key, 0))
            if s < 60:
                weaknesses.append(f"• {label}: {int(s)}/100 - {self._t('weaknesses')}")

        if weaknesses:
            conclusion_text += "<br/>".join(weaknesses)
        else:
            conclusion_text += f"• {self._t('no_weaknesses')}"

        conclusion_text += f"""
        <br/><br/>
        <b>{self._t('next_steps')}:</b><br/>
        1. {self._t('step_1')}<br/>
        2. {self._t('step_2')}<br/>
        3. {self._t('step_3')}<br/>
        4. {self._t('step_4')}<br/>
        <br/><br/>
        <font size=8 color='#94A3B8'>
        {self._t('footer_note')}<br/>
        {self._t('contact')}<br/>
        <b>{self._t('all_rights')}</b>
        </font>
        """

        story.append(Paragraph(conclusion_text, styles['CustomBodyText']))

        # =========================
        # BUILD PDF
        # =========================
        # 🆕 Passer la langue au canvas sans conflit avec ReportLab
        def make_canvas(*args, **kwargs):
            kwargs.pop('lang', None)  # Retirer si ReportLab le passe
            return NumberedCanvas(*args, lang=self.lang, **kwargs)

        doc.build(story, canvasmaker=make_canvas)

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        tmp.write(buffer.getvalue())
        tmp.close()

        return tmp.name

    # =========================
    # METRICS HELPERS
    # =========================
    def _add_technical_metrics(self, story, raw_data, styles):
        """Ajouter les métriques techniques"""
        story.append(Paragraph(f"<b>{self._t('technical_metrics')}</b>", styles['SubSection']))

        tech = raw_data.get('technical', {})
        meta = raw_data.get('meta_tags', {})

        metrics = [
            (self._t("load_time"), f"{tech.get('load_time_ms', 0)/1000:.2f}s", "< 2s"),
            (self._t("html_size"), f"{tech.get('html_size_kb', 0)} KB", "< 500 KB"),
            (self._t("word_count"), str(tech.get('word_count', 0)), "> 300"),
            (self._t("robots_txt"), self._t("present") if tech.get('has_robots_txt') else self._t("missing"), self._t("essential")),
            (self._t("sitemap_xml"), self._t("present") if tech.get('has_sitemap') else self._t("missing"), self._t("essential")),
            (self._t("https"), self._t("active") if tech.get('is_https') else self._t("inactive"), self._t("mandatory")),
            (self._t("viewport"), self._t("present") if tech.get('has_viewport') else self._t("missing"), self._t("mobile")),
            (self._t("charset"), self._t("declared") if tech.get('has_charset') else self._t("missing"), self._t("encoding")),
            (self._t("structured_data"), self._t("present") if tech.get('has_structured_data') else self._t("missing"), self._t("rich_snippets")),
            (self._t("favicon"), self._t("present") if tech.get('has_favicon') else self._t("missing"), self._t("branding")),
        ]

        for label, value, note in metrics:
            status_color = '#10B981' if '✓' in value else '#EF4444'
            story.append(Paragraph(
                f"<font color='{status_color}'>{value}</font> - <b>{label}</b> <font color='#94A3B8'>({note})</font>",
                styles['CustomBodyText']
            ))

        story.append(Paragraph(f"<b>{self._t('meta_tags')}</b>", styles['SubSection']))
        title = meta.get('title') or 'N/A'
        story.append(Paragraph(
            f"{self._t('title')}: <b>{title}</b> ({meta.get('title_length', 0)} {self._t('characters')})",
            styles['CustomBodyText']
        ))
        desc = meta.get('description') or 'N/A'
        desc_display = desc[:80] if len(desc) > 80 else desc
        story.append(Paragraph(
            f"{self._t('description')}: <b>{desc_display}</b> ({meta.get('description_length', 0)} {self._t('characters')})",
            styles['CustomBodyText']
        ))

        story.append(Spacer(1, 0.3*cm))

    def _add_content_metrics(self, story, raw_data, styles):
        """Ajouter les métriques de contenu"""
        story.append(Paragraph(f"<b>{self._t('content_metrics')}</b>", styles['SubSection']))

        tech = raw_data.get('technical', {})
        headings = raw_data.get('headings', {})

        metrics = [
            (self._t("word_count"), str(tech.get('word_count', 0)), "> 1000"),
            (self._t("h1_count"), str(headings.get('h1_count', 0)), "= 1"),
            (self._t("h2_count"), str(len(headings.get('h2', []))), "> 2"),
            (self._t("h3_count"), str(len(headings.get('h3', []))), "> 3"),
        ]

        for label, value, note in metrics:
            story.append(Paragraph(
                f"<b>{label}:</b> {value} <font color='#94A3B8'>({note})</font>",
                styles['CustomBodyText']
            ))

        story.append(Spacer(1, 0.3*cm))

    def _add_ux_metrics(self, story, raw_data, styles):
        """Ajouter les métriques UX"""
        story.append(Paragraph(f"<b>{self._t('ux_metrics')}</b>", styles['SubSection']))

        tech = raw_data.get('technical', {})

        metrics = [
            (self._t("viewport"), "✓" if tech.get('has_viewport') else "✗", self._t("responsive")),
            ("lang", "✓" if tech.get('has_lang') else "✗", self._t("accessibility")),
            (self._t("charset"), "✓" if tech.get('has_charset') else "✗", self._t("text_rendering")),
        ]

        for label, value, note in metrics:
            status_color = '#10B981' if value == '✓' else '#EF4444'
            story.append(Paragraph(
                f"<font color='{status_color}'>{value}</font> <b>{label}</b> <font color='#94A3B8'>({note})</font>",
                styles['CustomBodyText']
            ))

        story.append(Spacer(1, 0.3*cm))

    def _add_popularity_metrics(self, story, raw_data, styles):
        """Ajouter les métriques de popularité"""
        story.append(Paragraph(f"<b>{self._t('popularity_metrics')}</b>", styles['SubSection']))

        links = raw_data.get('links', {})
        internal = links.get('internal', [])
        external = links.get('external', [])

        metrics = [
            (self._t("internal_links"), str(len(internal)), self._t("navigation")),
            (self._t("external_links"), str(len(external)), self._t("authority")),
            (self._t("nofollow_links"), str(sum(1 for l in external if l.get('is_nofollow'))), self._t("seo")),
        ]

        for label, value, note in metrics:
            story.append(Paragraph(
                f"<b>{label}:</b> {value} <font color='#94A3B8'>({note})</font>",
                styles['CustomBodyText']
            ))

        story.append(Spacer(1, 0.3*cm))

    # =========================
    # CSV EXPORT
    # =========================
    def generate_csv(self, data: Dict[str, Any]) -> io.StringIO:
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')

        meta = data.get("meta", {})

        writer.writerow([self._t("csv_report_title")])
        writer.writerow(["URL", meta.get("url_analyzed", "N/A")])
        writer.writerow([self._t("analysis_date"), datetime.now().strftime("%d/%m/%Y %H:%M")])
        writer.writerow([self._t("report_type"), meta.get("section", "full")])
        writer.writerow([])

        writer.writerow([self._t("csv_category"), self._t("csv_score"), self._t("csv_status")])

        scores = data.get("scores", {})
        for key in ["technical", "content", "ux", "popularity"]:
            if key in data or meta.get("section") == "full":
                sc = data.get(key, {}).get("score", scores.get(key, 0))
                status = self._get_score_label(sc)
                writer.writerow([key.upper(), sc, status])

        writer.writerow([])
        writer.writerow([self._t("csv_global_score"), scores.get("global", 0)])

        writer.writerow([])
        writer.writerow([self._t("csv_category"), self._t("csv_priority"), self._t("csv_title_col"), 
                        self._t("csv_description_col"), self._t("csv_impact_col"), self._t("csv_solution")])

        for key in ["technical", "content", "ux", "popularity"]:
            issues = data.get(key, {}).get("issues", [])
            for issue in issues:
                writer.writerow([
                    key.upper(),
                    issue.get("priority", "medium"),
                    issue.get("title", ""),
                    issue.get("description", ""),
                    issue.get("impact", ""),
                    issue.get("solution", "")
                ])

        writer.writerow([])
        writer.writerow([self._t("csv_priority"), self._t("csv_category"), self._t("csv_title_col"), 
                        self._t("csv_description_col"), self._t("csv_impact_col"), self._t("csv_effort")])

        recommendations = data.get("recommendations", {})
        if isinstance(recommendations, dict):
            for priority, recos in recommendations.items():
                for rec in recos:
                    writer.writerow([
                        priority,
                        rec.get("category", ""),
                        rec.get("title", ""),
                        rec.get("description", ""),
                        rec.get("impact", ""),
                        rec.get("effort", rec.get("time", ""))
                    ])
        elif isinstance(recommendations, list):
            for rec in recommendations:
                writer.writerow([
                    rec.get("priority", ""),
                    rec.get("category", ""),
                    rec.get("title", ""),
                    rec.get("description", ""),
                    rec.get("impact", ""),
                    rec.get("effort", rec.get("time", ""))
                ])

        output.seek(0)
        return output

    # =========================
    # JSON EXPORT
    # =========================
    def generate_json(self, data: Dict[str, Any], pretty=True) -> str:
        result = {
            "meta": data.get("meta", {}),
            "scores": data.get("scores", {}),
            "categories": {
                k: {
                    "score": data.get(k, {}).get("score"),
                    "issues": data.get(k, {}).get("issues", [])
                }
                for k in ["technical", "content", "ux", "popularity"]
                if k in data
            },
            "recommendations": data.get("recommendations", {}),
            "generated_at": datetime.utcnow().isoformat(),
            "language": self.lang
        }

        if pretty:
            return json.dumps(result, indent=2, ensure_ascii=False)
        return json.dumps(result, ensure_ascii=False)


print("✅ Export Service Bilingual PFE Pro loaded successfully")