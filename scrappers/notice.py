import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def find_html_text(soup, tag, class_name):
    element = soup.find(tag, class_=class_name)
    return element.get_text(strip=True) if element else None


def get_date(date_str):
    date_str = date_str.replace("Última atualização em", "")
    date_str = date_str.split(":")[-1].strip()
    return date_str


def get_campus(soup):
    breadcrumbs = soup.find_all("a", class_="pathway")
    if len(breadcrumbs) > 1:
        return breadcrumbs[1].get_text(strip=True)
    return None


def find_category(soup):
    # Processo Seletivo
    notice_description = soup.find_all("p")
    for p in notice_description:
        if "processo seletivo" in p.get_text(strip=True).lower():
            return "Processo Seletivo"
    return None


def find_attachments(soup, base_url):
    valid_attachments = []
    if soup.find("caption", string="Anexos:"):
        attachments_tags = soup.find_all("a", class_="at_url")
        file_extensions = (
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".txt",
            ".zip",
        )

        # Lista de anexos com base na extensão de arquivos
        valid_attachments = [
            {
                "title": att.get_text(strip=True),
                "url": urljoin(base_url, att.get("href")),
            }
            for att in attachments_tags
            if att.get("href") and att.get("href").endswith(file_extensions)
        ]

    return valid_attachments


def scrape_notice_page(page_url):
    try:
        response = requests.get(page_url)

        if response.status_code == 200:
            page_soup = BeautifulSoup(response.content, "html.parser")

            notice_info = {
                "title": find_html_text(page_soup, "h1", "documentFirstHeading"),
                "campus": get_campus(page_soup),
                "type": find_category(page_soup),
                "attachments": find_attachments(page_soup, page_url),
                "datas": {
                    "publicacao": get_date(
                        find_html_text(page_soup, "span", "documentPublished")
                    ),
                    "criacao": get_date(
                        find_html_text(page_soup, "span", "documentCreated")
                    ),
                    "modificacao": get_date(
                        find_html_text(page_soup, "span", "documentModified")
                    ),
                },
            }
            return notice_info
        else:
            print(f"Failed to load page. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return None


# test = scrape_notice_page(
#     "https://ifb.edu.br/saosebastiao/35444-portador-de-diploma-e-transferencia-em-cursos-tecnicos-e-superiores-resultado-final"
# )
# print(json.dumps(test, indent=4))
