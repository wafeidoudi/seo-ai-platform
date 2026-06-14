# backend/app/services/meta.py
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import urllib3
import time
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

async def crawl_website(url: str):
    """
    Crawler un site web et extraire toutes les données SEO
    
    Args:
        url (str): URL du site à analyser
        
    Returns:
        dict: Données complètes pour le frontend
    """
    start_time = time.time()
    
    async with httpx.AsyncClient(timeout=20, verify=False) as client:
        response = await client.get(url)
    
    load_time_ms = int((time.time() - start_time) * 1000)
    html = response.text
    html_size_kb = round(len(html.encode('utf-8')) / 1024, 2)
    
    soup = BeautifulSoup(html, "html.parser")
    
    # ==================== META TAGS ====================
    title = soup.title.string.strip() if soup.title else None
    title_length = len(title) if title else 0
    
    description = None
    desc_tag = soup.find("meta", attrs={"name": "description"})
    if desc_tag:
        description = desc_tag.get("content")
    description_length = len(description) if description else 0
    
    keywords = None
    keywords_tag = soup.find("meta", attrs={"name": "keywords"})
    if keywords_tag:
        keywords = keywords_tag.get("content")
    
    canonical = None
    canonical_tag = soup.find("link", rel="canonical")
    if canonical_tag:
        canonical = canonical_tag.get("href")
    
    # Open Graph tags
    og_title = None
    og_desc = None
    og_image = None
    
    og_title_tag = soup.find("meta", property="og:title")
    if og_title_tag:
        og_title = og_title_tag.get("content")
    
    og_desc_tag = soup.find("meta", property="og:description")
    if og_desc_tag:
        og_desc = og_desc_tag.get("content")
    
    og_image_tag = soup.find("meta", property="og:image")
    if og_image_tag:
        og_image = og_image_tag.get("content")
    
    # Robots meta
    robots_meta = soup.find("meta", attrs={"name": "robots"})
    has_robots = robots_meta is not None
    
    # Viewport
    viewport = soup.find("meta", attrs={"name": "viewport"})
    has_viewport = viewport is not None
    
    # Language
    html_tag = soup.find("html")
    has_lang = html_tag and html_tag.get("lang") is not None
    
    # Charset
    has_charset = soup.find("meta", attrs={"charset"}) is not None
    
    # ==================== HEADINGS ====================
    headings = {
        "h1": [h.get_text(strip=True) for h in soup.find_all("h1")],
        "h2": [h.get_text(strip=True) for h in soup.find_all("h2")],
        "h3": [h.get_text(strip=True) for h in soup.find_all("h3")],
        "h4": [h.get_text(strip=True) for h in soup.find_all("h4")],
        "h5": [h.get_text(strip=True) for h in soup.find_all("h5")],
        "h6": [h.get_text(strip=True) for h in soup.find_all("h6")],
    }
    
    # ==================== IMAGES ====================
    images = soup.find_all("img")
    image_list = []
    missing_alt_count = 0
    lazy_loaded_count = 0
    
    for img in images:
        src = img.get("src")
        alt = img.get("alt")
        loading = img.get("loading")
        is_lazy = loading == "lazy"
        has_alt = alt is not None and alt.strip() != ""
        
        if not has_alt:
            missing_alt_count += 1
        if is_lazy:
            lazy_loaded_count += 1
        
        image_list.append({
            "src": src,
            "alt": alt,
            "has_alt": has_alt,
            "is_lazy": is_lazy
        })
    
    # Add summary object (frontend expects this)
    image_list.append({
        "_summary": {
            "total": len(image_list),
            "missing_alt": missing_alt_count,
            "lazy_loaded": lazy_loaded_count
        }
    })
    
    # ==================== LINKS ====================
    internal_links = []
    external_links = []
    
    domain = urlparse(url).netloc
    
    for link in soup.find_all("a", href=True):
        href = link.get("href")
        full_url = urljoin(url, href)
        is_nofollow = link.get("rel") and "nofollow" in link.get("rel", [])
        
        link_data = {
            "url": full_url,
            "text": link.get_text(strip=True),
            "is_nofollow": is_nofollow
        }
        
        if domain in urlparse(full_url).netloc:
            internal_links.append(link_data)
        else:
            external_links.append(link_data)
    
    # ==================== TECHNICAL CHECKS ====================
    
    # HTTPS
    is_https = url.startswith("https://")
    
    # robots.txt
    robots_url = urljoin(url, "/robots.txt")
    try:
        async with httpx.AsyncClient() as client:
            robots = await client.get(robots_url)
        has_robots_txt = robots.status_code == 200
    except:
        has_robots_txt = False
    
    # sitemap.xml
    sitemap_url = urljoin(url, "/sitemap.xml")
    try:
        async with httpx.AsyncClient() as client:
            sitemap = await client.get(sitemap_url)
        has_sitemap = sitemap.status_code == 200
        sitemap_total_urls = 0
        sitemap_last_modified = None
        
        if has_sitemap:
            # Parse sitemap to count URLs
            sitemap_soup = BeautifulSoup(sitemap.text, "xml")
            urls = sitemap_soup.find_all("url")
            sitemap_total_urls = len(urls)
            
            # Get last modified date
            last_mod = sitemap_soup.find("lastmod")
            if last_mod:
                sitemap_last_modified = last_mod.get_text()
    except:
        has_sitemap = False
        sitemap_total_urls = 0
        sitemap_last_modified = None
    
    # Structured Data (JSON-LD)
    structured_data_scripts = soup.find_all("script", type="application/ld+json")
    has_structured_data = len(structured_data_scripts) > 0
    
    # Favicon
    favicon = soup.find("link", rel=lambda x: x and "icon" in x.lower())
    has_favicon = favicon is not None
    
    # Word Count
    text = soup.get_text()
    word_count = len(text.split())
    
    # Render Blocking Resources
    scripts = soup.find_all("script", src=True)
    styles = soup.find_all("link", rel="stylesheet")
    
    # ==================== RAW DATA RESULT ====================
    data = {
        "url": url,
        "meta_tags": {
            "title": title,
            "title_length": title_length,
            "description": description,
            "description_length": description_length,
            "keywords": keywords,
            "canonical": canonical,
            "robots": robots_meta.get("content") if robots_meta else None,
            "og_title": og_title,
            "og_description": og_desc,
            "og_image": og_image,
        },
        
        "headings": {
            "h1": headings["h1"],
            "h1_count": len(headings["h1"]),
            "h2": headings["h2"],
            "h2_count": len(headings["h2"]),
            "h3": headings["h3"],
            "h3_count": len(headings["h3"]),
            "h4": headings["h4"],
            "h5": headings["h5"],
            "h6": headings["h6"],
            "has_proper_hierarchy": len(headings["h1"]) == 1 and len(headings["h2"]) > 0
        },
        
        "images": image_list,
        
        "links": {
            "internal": internal_links,
            "external": external_links,
            "broken": []  # À implémenter avec vérification de status code
        },
        
        "technical": {
            "load_time_ms": load_time_ms,
            "html_size_kb": html_size_kb,
            "word_count": word_count,
            "is_https": is_https,
            "has_viewport": has_viewport,
            "has_lang": has_lang,
            "has_charset": has_charset,
            "has_robots_txt": has_robots_txt,
            "robots_txt_url": "/robots.txt" if has_robots_txt else None,
            "has_sitemap": has_sitemap,
            "sitemap_url": "/sitemap.xml" if has_sitemap else None,
            "sitemap_total_urls": sitemap_total_urls,
            "sitemap_last_modified": sitemap_last_modified,
            "has_structured_data": has_structured_data,
            "has_favicon": has_favicon,
            "charset": soup.find("meta", attrs={"charset"}).get("charset") if soup.find("meta", attrs={"charset"}) else None,
        },
        
        "performance": {
            "scripts_count": len(scripts),
            "stylesheets_count": len(styles),
            "render_blocking_scripts": len([s for s in scripts if not s.get("async") and not s.get("defer")]),
            "render_blocking_styles": len(styles)
        }
    }
    
    return data


# Test rapide
if __name__ == "__main__":
    import asyncio
    
    async def test():
        result = await crawl_website("https://example.com")
        print("URL:", result["url"])
        print("Title:", result["meta_tags"]["title"])
        print("Load Time:", result["technical"]["load_time_ms"], "ms")
        print("HTTPS:", result["technical"]["is_https"])
        print("Images:", result["images"][-1]["_summary"])  # Summary object
    
    asyncio.run(test())