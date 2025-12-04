import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import scrappers.notice as notice_page
from datetime import datetime

URL = "https://www.ifb.edu.br/"
DOMAIN = urlparse(URL).netloc

print(f"Tentando conectar ao site: {URL}...")

def filter_IFB_Links(links):
    return set(
        [link for link in links if urlparse(link).netloc == DOMAIN and not "#" in link]
    )

def list_page_links(base_url):       
    links = []
    try:
        response = requests.get(base_url, timeout=10)
        log_page_visit(base_url, success=response.status_code == 200)

        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "")
            if "text/html" in content_type:
                soup = BeautifulSoup(response.content, "html.parser")
                links_tags = soup.find_all("a")
                raw_links = [urljoin(base_url, link.get("href")) for link in links_tags]
                links = filter_IFB_Links(raw_links)
            else:
                log_page_visit(base_url, success=False, error_message="Content is not HTML")
    except requests.RequestException as e:
        print(f"Erro ao acessar {base_url}: {e}")
        log_page_visit(base_url, success=False, error_message=str(e))

    return links

def log_page_visit(url, success=True, error_message=""):
    timestamp = datetime.now().isoformat()
    log_path = "logs/crawler_log.txt"
    log_content = f"{timestamp} - Status: {'Success' if success else 'Error'} - URL: {url}"
    if not success:
        log_content += f" - Error Message: {error_message}"
    log_content += "\n"
    try:
        with open(log_path, "a") as log_file:
            log_file.write(log_content)
    except IOError as e:
        print(f"Erro ao escrever no arquivo de log: {e}")


def crawl_IFB_domain(initial_url, max_pages_to_crawl=1000):
    visited_urls = set()
    urls_to_visit = [initial_url]
    enqueued_urls = set(urls_to_visit)

    while urls_to_visit and len(visited_urls) < max_pages_to_crawl:
        ## pop(0) define uma fila (BFS) pop() define uma pilha (DFS)
        url_being_visited = urls_to_visit.pop(0)
        if url_being_visited in visited_urls:
            continue

        links = list_page_links(url_being_visited)

        for link in links:
            if(link not in visited_urls and link not in enqueued_urls):
                urls_to_visit.append(link)
                enqueued_urls.add(link)
        
        visited_urls.add(url_being_visited)
    return visited_urls

visited_pages = crawl_IFB_domain(URL, max_pages_to_crawl=100000)
print(f"Páginas visitadas: {visited_pages}")

class IFBPage:
    def __init__(self, url, content, page_type):
        self.url = url
        self.content = content
        self.page_type = page_type
    ## def classify_page(url):
pages = []