import aiohttp
from urllib.parse import quote

async def search_catalog(query, limit=5):
    base_url = "https://vufind.org/advanced_demo/api/v1/search"
    encoded_query = quote(query)
    url = f"{base_url}?lookfor={encoded_query}&type=AllFields&sort=relevance&page=1&limit={limit}&prettyPrint=false&lng=en"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    catalog_url = f"https://vufind.org/advanced_demo/Search/Results?lookfor={encoded_query}&type=AllFields"
                    return data, catalog_url
        return None, None
    except Exception as e:
        print(f"[vufind_service] Error searching catalog: {e}")
        return None, None

def format_catalog_record(record):
    title = record.get('title', 'Без названия').replace('/', '').strip()
    authors_data = record.get('authors', {}).get('primary', {})
    if isinstance(authors_data, dict):
        authors_list = list(authors_data.keys())
    elif isinstance(authors_data, list):
        authors_list = authors_data
    else:
        authors_list = []
    authors_str = ', '.join(authors_list)

    subject_collections = record.get('subjects', [])
    subject_strings = []
    for group in subject_collections:
        if isinstance(group, list):
            subject_strings.append(', '.join(group))
    subjects_str = '; '.join(subject_strings) if subject_strings else ''

    lines = [f"📚 {title}"]
    if authors_str:
        lines.append(f"👤 Авторы: {authors_str}")
    if subjects_str:
        lines.append(f"🏷 Темы: {subjects_str}")
    return "\n".join(lines)



# import requests
# from urllib.parse import quote

# def search_catalog(query, limit=5):
#     base_url = "https://vufind.org/advanced_demo/api/v1/search"
#     encoded_query = quote(query)
#     url = f"{base_url}?lookfor={encoded_query}&type=AllFields&sort=relevance&page=1&limit={limit}&prettyPrint=false&lng=en"
#     try:
#         response = requests.get(url)
#         if response.status_code == 200:
#             data = response.json()
#             catalog_url = f"https://vufind.org/advanced_demo/Search/Results?lookfor={encoded_query}&type=AllFields"
#             return data, catalog_url
#         return None, None
#     except Exception as e:
#         print(f"[vufind_service] Error searching catalog: {e}")
#         return None, None

# def format_catalog_record(record):
#     title = record.get('title', 'Без названия').replace('/', '').strip()
#     authors_data = record.get('authors', {}).get('primary', {})
#     if isinstance(authors_data, dict):
#         authors_list = list(authors_data.keys())
#     elif isinstance(authors_data, list):
#         authors_list = authors_data
#     else:
#         authors_list = []
#     authors_str = ', '.join(authors_list)

#     subject_collections = record.get('subjects', [])
#     subject_strings = []
#     for group in subject_collections:
#         if isinstance(group, list):
#             subject_strings.append(', '.join(group))
#     subjects_str = '; '.join(subject_strings) if subject_strings else ''

#     lines = [f"📚 {title}"]
#     if authors_str:
#         lines.append(f"👤 Авторы: {authors_str}")
#     if subjects_str:
#         lines.append(f"🏷 Темы: {subjects_str}")
#     return "\n".join(lines)
