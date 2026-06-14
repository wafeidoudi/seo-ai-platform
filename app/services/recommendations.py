# backend/app/services/recommendations.py
from typing import Dict, Any, List


def generate_recommendations(raw_data: Dict[str, Any], scores: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate detailed SEO recommendations based on analysis and scores
    
    Args:
        raw_data (Dict): Raw crawler data (from meta.py)
        scores (Dict): Calculated scores (from scoring.py)
        
    Returns:
        Dict: Recommendations structured by priority
    """
    recommendations = {
        "critical": [],
        "high": [],
        "medium": [],
        "low": []
    }
    
    meta_tags = raw_data.get("meta_tags", {})
    headings = raw_data.get("headings", {})
    technical = raw_data.get("technical", {})
    images = raw_data.get("images", [])
    links = raw_data.get("links", {})
    
    # Find the images summary object
    images_summary = next((i for i in images if i.get("_summary")), {})
    total_images = images_summary.get("total", 0)
    missing_alt = images_summary.get("missing_alt", 0)
    
    # ==================== CRITICAL RECOMMENDATIONS ====================
    
    # Missing Title Tag
    if not meta_tags.get("title"):
        recommendations["critical"].append({
            "id": "missing-title",
            "category": "Meta Tags",
            "icon": "fa-tag",
            "title": "Missing Title Tag",
            "description": "No page title detected. Search engines use the title to understand and rank your page.",
            "impact": "Critical - Directly affects visibility in search results",
            "solution": "Add a unique, descriptive title to each page (50-60 characters)",
            "code_example": "<title>Your Page Title | Brand Name</title>",
            "priority": "critical",
            "effort": "Low",
            "roi": "High"
        })
    
    # Title too short or too long
    title_length = meta_tags.get("title_length", 0)
    if title_length and (title_length < 30 or title_length > 60):
        recommendations["critical"].append({
            "id": "title-length",
            "category": "Meta Tags",
            "icon": "fa-tag",
            "title": "Title Tag Length Not Optimal",
            "description": f"Your title is {title_length} characters. Optimal length is between 30-60 characters.",
            "impact": "High - May affect click-through rate and rankings",
            "solution": "Adjust title length to be between 30-60 characters",
            "code_example": f"<title>{meta_tags.get('title', '')[:60]}...</title>",
            "priority": "critical",
            "effort": "Low",
            "roi": "High"
        })
    
    # Missing Meta Description
    if not meta_tags.get("description"):
        recommendations["critical"].append({
            "id": "missing-description",
            "category": "Meta Tags",
            "icon": "fa-file-lines",
            "title": "Missing Meta Description",
            "description": "No meta description detected. It influences click-through rates from search results.",
            "impact": "Critical - Reduced CTR from SERPs",
            "solution": "Add a compelling meta description (120-160 characters) with a call-to-action",
            "code_example": '<meta name="description" content="Your compelling description here...">',
            "priority": "critical",
            "effort": "Low",
            "roi": "High"
        })
    
    # Missing H1
    h1_count = headings.get("h1_count", 0)
    if h1_count == 0:
        recommendations["critical"].append({
            "id": "missing-h1",
            "category": "Content",
            "icon": "fa-heading",
            "title": "No H1 Tag Detected",
            "description": "Every page should have exactly one H1 to define its main topic.",
            "impact": "Critical - Confuses search engines about page topic",
            "solution": "Add exactly one <h1> tag per page with your main keyword",
            "code_example": "<h1>Your Main Topic Here</h1>",
            "priority": "critical",
            "effort": "Low",
            "roi": "High"
        })
    
    # Multiple H1s
    elif h1_count > 1:
        recommendations["high"].append({
            "id": "multiple-h1",
            "category": "Content",
            "icon": "fa-heading",
            "title": f"Multiple H1 Tags Detected ({h1_count})",
            "description": "Each page should have exactly one H1. Multiple H1s dilute topic focus.",
            "impact": "High - Dilutes thematic focus for search engines",
            "solution": "Keep only one H1 per page; use H2-H6 for subsections",
            "code_example": "<h1>Main Title</h1>\n<h2>Subsection 1</h2>\n<h2>Subsection 2</h2>",
            "priority": "high",
            "effort": "Medium",
            "roi": "High"
        })
    
    # Site not HTTPS
    if not technical.get("is_https"):
        recommendations["critical"].append({
            "id": "no-https",
            "category": "Technical",
            "icon": "fa-lock",
            "title": "Site Not Secure (Non-HTTPS)",
            "description": "Non-HTTPS sites are flagged as insecure by browsers and penalized by Google.",
            "impact": "Critical - Security warning + ranking penalty",
            "solution": "Install an SSL certificate and redirect all HTTP traffic to HTTPS",
            "code_example": "# HTTP to HTTPS redirect in .htaccess\nRewriteEngine On\nRewriteCond %{HTTPS} off\nRewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]",
            "priority": "critical",
            "effort": "Medium",
            "roi": "Critical"
        })
    
    # ==================== HIGH RECOMMENDATIONS ====================
    
    # Slow load time
    load_time = technical.get("load_time_ms", 0)
    if load_time > 3000:
        recommendations["high"].append({
            "id": "slow-load",
            "category": "Performance",
            "icon": "fa-gauge-high",
            "title": "Slow Page Load Time",
            "description": f"Page loads in {load_time/1000:.1f}s, above the recommended 3s threshold.",
            "impact": "High - Higher bounce rate, lower rankings",
            "solution": "Optimize images, enable caching, minify CSS/JS, use a CDN",
            "code_example": "<!-- Enable browser caching -->\n<IfModule mod_expires.c>\n  ExpiresActive On\n  ExpiresByType image/jpg \"access plus 1 year\"\n</IfModule>",
            "priority": "high",
            "effort": "Medium",
            "roi": "High"
        })
    
    # Missing viewport
    if not technical.get("has_viewport"):
        recommendations["high"].append({
            "id": "no-viewport",
            "category": "Mobile",
            "icon": "fa-mobile-screen",
            "title": "Missing Viewport Meta Tag",
            "description": "Without viewport tag, mobile rendering may be incorrect.",
            "impact": "High - Poor mobile experience + mobile ranking impact",
            "solution": "Add the viewport meta tag to your <head>",
            "code_example": '<meta name="viewport" content="width=device-width, initial-scale=1">',
            "priority": "high",
            "effort": "Low",
            "roi": "High"
        })
    
    # ==================== MEDIUM RECOMMENDATIONS ====================
    
    # Images without alt
    if missing_alt > 0:
        recommendations["medium"].append({
            "id": "missing-alt",
            "category": "Accessibility",
            "icon": "fa-image",
            "title": f"{missing_alt} Images Missing Alt Text",
            "description": f"{missing_alt} out of {total_images} images lack alt attributes, affecting accessibility and image SEO.",
            "impact": "Medium - Poor accessibility + missed image search traffic",
            "solution": "Add descriptive alt text to all images",
            "code_example": '<img src="image.jpg" alt="Descriptive text for the image">',
            "priority": "medium",
            "effort": "Medium",
            "roi": "Medium"
        })
    
    # Missing canonical
    if not meta_tags.get("canonical"):
        recommendations["medium"].append({
            "id": "missing-canonical",
            "category": "Technical",
            "icon": "fa-link",
            "title": "Missing Canonical URL",
            "description": "Without a canonical tag, duplicate content may dilute your page ranking.",
            "impact": "Medium - Risk of duplicate content penalties",
            "solution": "Add a canonical link to specify the preferred URL",
            "code_example": '<link rel="canonical" href="https://yoursite.com/preferred-url">',
            "priority": "medium",
            "effort": "Low",
            "roi": "Medium"
        })
    
    # Missing robots.txt
    if not technical.get("has_robots_txt"):
        recommendations["medium"].append({
            "id": "missing-robots",
            "category": "Technical",
            "icon": "fa-robot",
            "title": "Missing robots.txt File",
            "description": "The robots.txt file helps search engines crawl your site efficiently.",
            "impact": "Medium - May affect crawl efficiency",
            "solution": "Create a robots.txt file at the root of your website",
            "code_example": "User-agent: *\nAllow: /\nSitemap: https://yoursite.com/sitemap.xml",
            "priority": "medium",
            "effort": "Low",
            "roi": "Medium"
        })
    
    # Missing sitemap
    if not technical.get("has_sitemap"):
        recommendations["medium"].append({
            "id": "missing-sitemap",
            "category": "Technical",
            "icon": "fa-sitemap",
            "title": "Missing XML Sitemap",
            "description": "The sitemap helps search engines discover all your pages.",
            "impact": "Medium - Some pages may not be indexed",
            "solution": "Create and submit a sitemap.xml to search engines",
            "code_example": '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url>\n    <loc>https://yoursite.com/page</loc>\n  </url>\n</urlset>',
            "priority": "medium",
            "effort": "Medium",
            "roi": "Medium"
        })
    
    # ==================== LOW RECOMMENDATIONS ====================
    
    # Missing structured data
    if not technical.get("has_structured_data"):
        recommendations["low"].append({
            "id": "no-structured-data",
            "category": "Technical",
            "icon": "fa-code",
            "title": "No Structured Data Detected",
            "description": "Schema.org markup helps search engines understand your content better.",
            "impact": "Low - Missed opportunity for rich snippets",
            "solution": "Add JSON-LD structured data for your content type",
            "code_example": '<script type="application/ld+json">\n{\n  "@context": "https://schema.org",\n  "@type": "Article",\n  "headline": "Article Title"\n}\n</script>',
            "priority": "low",
            "effort": "Medium",
            "roi": "Low"
        })
    
    # Missing language attribute
    if not technical.get("has_lang"):
        recommendations["low"].append({
            "id": "no-lang",
            "category": "Accessibility",
            "icon": "fa-language",
            "title": "Missing Language Attribute",
            "description": "The <html> tag should specify the page language for accessibility and SEO.",
            "impact": "Low - Minor accessibility and international SEO impact",
            "solution": "Add the lang attribute to your <html> tag",
            "code_example": '<html lang="en">',
            "priority": "low",
            "effort": "Low",
            "roi": "Low"
        })
    
    # Missing favicon
    if not technical.get("has_favicon"):
        recommendations["low"].append({
            "id": "no-favicon",
            "category": "UX",
            "icon": "fa-image",
            "title": "Missing Favicon",
            "description": "The site has no favicon.",
            "impact": "Low - Minor impact on brand recognition",
            "solution": "Add a favicon to improve brand recognition",
            "code_example": '<link rel="icon" type="image/x-icon" href="/favicon.ico">',
            "priority": "low",
            "effort": "Low",
            "roi": "Low"
        })
    
    # ==================== STATISTICS ====================
    total_recommendations = (
        len(recommendations["critical"]) +
        len(recommendations["high"]) +
        len(recommendations["medium"]) +
        len(recommendations["low"])
    )
    
    return {
        "recommendations": recommendations,
        "summary": {
            "total": total_recommendations,
            "critical": len(recommendations["critical"]),
            "high": len(recommendations["high"]),
            "medium": len(recommendations["medium"]),
            "low": len(recommendations["low"]),
        },
        "quick_wins": [
            r for r in recommendations["critical"] + recommendations["high"]
            if r.get("effort") == "Low" and r.get("roi") in ["High", "Critical"]
        ],
        "priority_actions": [
            r for r in recommendations["critical"][:3]
        ] if recommendations["critical"] else []
    }


def format_recommendations_for_display(recommendations_data: Dict[str, Any]) -> str:
    """
    Format recommendations for text display
    
    Args:
        recommendations_data (Dict): Generated recommendations
        
    Returns:
        str: Formatted text for display
    """
    output = []
    summary = recommendations_data.get("summary", {})
    recommendations = recommendations_data.get("recommendations", {})
    
    output.append("=" * 60)
    output.append("📊 SEO RECOMMENDATIONS REPORT")
    output.append("=" * 60)
    output.append(f"\n📈 Summary:")
    output.append(f"   Total: {summary.get('total', 0)} recommendations")
    output.append(f"   🔴 Critical: {summary.get('critical', 0)}")
    output.append(f"   🟠 High: {summary.get('high', 0)}")
    output.append(f"   🟡 Medium: {summary.get('medium', 0)}")
    output.append(f"   🟢 Low: {summary.get('low', 0)}")
    
    if recommendations.get("critical"):
        output.append("\n" + "=" * 60)
        output.append("🔴 CRITICAL RECOMMENDATIONS (Immediate Action)")
        output.append("=" * 60)
        for rec in recommendations["critical"]:
            output.append(f"\n  [{rec.get('category')}] {rec.get('title')}")
            output.append(f"  📝 {rec.get('description')}")
            output.append(f"  💥 Impact: {rec.get('impact')}")
            output.append(f"  ✅ Solution: {rec.get('solution')}")
            output.append(f"  ⚡ Effort: {rec.get('effort')} | ROI: {rec.get('roi')}")
    
    if recommendations.get("high"):
        output.append("\n" + "=" * 60)
        output.append("🟠 HIGH RECOMMENDATIONS (High Priority)")
        output.append("=" * 60)
        for rec in recommendations["high"]:
            output.append(f"\n  [{rec.get('category')}] {rec.get('title')}")
            output.append(f"  📝 {rec.get('description')}")
            output.append(f"  💥 Impact: {rec.get('impact')}")
            output.append(f"  ✅ Solution: {rec.get('solution')}")
    
    if recommendations.get("medium"):
        output.append("\n" + "=" * 60)
        output.append("🟡 MEDIUM RECOMMENDATIONS (To Plan)")
        output.append("=" * 60)
        for rec in recommendations["medium"]:
            output.append(f"\n  [{rec.get('category')}] {rec.get('title')}")
            output.append(f"  📝 {rec.get('description')}")
            output.append(f"  ✅ Solution: {rec.get('solution')}")
    
    if recommendations.get("low"):
        output.append("\n" + "=" * 60)
        output.append("🟢 LOW RECOMMENDATIONS (Improvements)")
        output.append("=" * 60)
        for rec in recommendations["low"]:
            output.append(f"\n  [{rec.get('category')}] {rec.get('title')}")
            output.append(f"  📝 {rec.get('description')}")
            output.append(f"  ✅ Solution: {rec.get('solution')}")
    
    # Quick wins
    quick_wins = recommendations_data.get("quick_wins", [])
    if quick_wins:
        output.append("\n" + "=" * 60)
        output.append("⚡ QUICK WINS (Low Effort, High ROI)")
        output.append("=" * 60)
        for rec in quick_wins[:5]:
            output.append(f"  ✓ {rec.get('title')}")
    
    output.append("\n" + "=" * 60)
    
    return "\n".join(output)


# =============================
# TEST
# =============================
if __name__ == "__main__":
    # Test data
    test_meta = {
        "meta_tags": {
            "title": None,
            "title_length": 0,
            "description": None,
            "description_length": 0,
            "canonical": None,
        },
        "headings": {
            "h1": [],
            "h1_count": 0,
            "h2": ["Section 1"],
            "h2_count": 1,
        },
        "technical": {
            "load_time_ms": 4500,
            "is_https": False,
            "has_viewport": False,
            "has_lang": False,
            "has_robots_txt": False,
            "has_sitemap": False,
            "has_structured_data": False,
            "has_favicon": False,
        },
        "images": [
            {"src": "/img1.jpg", "alt": None, "has_alt": False, "is_lazy": False},
            {"src": "/img2.jpg", "alt": None, "has_alt": False, "is_lazy": False},
            {"_summary": {"total": 2, "missing_alt": 2, "lazy_loaded": 0}}
        ],
        "links": {
            "internal": [{"url": "/page1"}],
            "external": [{"url": "https://example.com", "is_nofollow": False}]
        }
    }
    
    test_scores = {
        "global_score": 25,
        "categories": {
            "technical": 20,
            "content": 30,
            "ux": 25,
            "popularity": 25
        }
    }
    
    recommendations = generate_recommendations(test_meta, test_scores)
    
    print(format_recommendations_for_display(recommendations))
    
    print("\n\n📊 JSON Output:")
    import json
    print(json.dumps(recommendations, indent=2, ensure_ascii=False))