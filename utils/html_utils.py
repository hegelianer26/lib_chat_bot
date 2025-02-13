from bs4 import BeautifulSoup

async def clean_html_content(html_content):
    """Remove HTML tags but preserve emojis and basic formatting like newlines and paragraphs"""
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, 'html.parser')

    for tag in soup.find_all(['br', 'p', 'div']):
        tag.insert_before('\n')
        tag.insert_after('\n')

    text = soup.get_text(separator='\n')

    return text.strip()