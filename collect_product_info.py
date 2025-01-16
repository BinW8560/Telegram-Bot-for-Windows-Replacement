from itertools import product

import requests
from bs4 import BeautifulSoup
import re

product_dict = {}

# List to store products details
all_products = []

# URL of the target page
url_list = [
    "https://www.fensterdepot24.de/fenster.html",
   "https://www.fensterdepot24.de/fenster/holzfenster.html",
#"https://www.bew24-fenster.de/fenster-kaufen/kunststofffenster.html"

]

for url in url_list[:2]:
    # Send a GET request to fetch the HTML content
    response = requests.get(url)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all product elements
    products = soup.find_all("a", class_="product-item-link")

    # Update the dictionary with product names and URLs
    for product in products:
        product_name = product.get_text(strip=True)
        product_url = product["href"]
        product_dict[product_name] = product_url



for key, value in list(product_dict.items())[:]:
    # Send a GET request to fetch the HTML content
    response = requests.get(value)

    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    product_name = soup.find("meta", {"name": "title"}).get("content")

    print(f"URL {value}")

    # Get Price
    product_price = soup.find("span", class_=("price"))

    # Save Product Description in a Predefined Dictionary
    product_info = {
        "Produkt": "Nicht Verfügbar",
        "Material": "Nicht Verfügbar",
        "Preis [€]": "Nicht Verfügbar",
        "Bautiefe": "Nicht Verfügbar",
        "Farbe": "Nicht Verfügbar",
        "Standard Verglasung": "Nicht Verfügbar",
        "Standard Sicherheit": "Nicht Verfügbar",
        "Uf-Wert [W/M²K]": "Nicht Verfügbar",
        "Ug-Wert [W/M²K]": "Nicht Verfügbar",
        "Design": "Nicht Verfügbar",
        "Verfügbarkeit": "Nicht Bekannt",
        "Link": "Nicht Verfüger"
    }
    product_info["Link"] = value
    # Loop through each row of the table
    # Find the table on the page
    table = soup.find("table", class_="wmh-related-products")

    # Check if the table exists
    if table:
        try:
            product_rows = table.find_all("strong", class_="product-item-name")
            print(product_rows)
            # Process product rows

            # Find the index of the specific product
            product_index = None

            for index, row in enumerate(product_rows):
                print(f"Index: {index}")
                print(row)
                if "Dieser Artikel".lower() in row.text.lower():
                    print(f"Produkt Name: {product_name}")
                    print(f"Row Text: {row.text}")
                    product_index = index

                    # print(f"Product found at row index: {product_index}")
                    break

            # Extract related product information if the product is found
            related_products = table.find_all("tr")

            if product_index is not None:
                related_products = table.find_all("tr")[2:]
                for row in related_products:
                    cells = row.find_all("td")
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        if key == "":
                            key = "Verfügbarkeit"
                            value = cells[product_index + 1].get_text(strip=True)
                            product_info[key] = value
                            print(key, value)
                        else:
                            value = cells[product_index + 1].get_text(strip=True)
                            product_info[key] = value
            else:
                print("Product not found.")


            product_info["Produkt"] = product_name
            #product_info["Preis"] = product_price.text
            if product_price:
                # Use regex to extract numbers and replace comma with a dot
                price_text = re.sub(r'[^\d,]', '', product_price.text).replace(',', '.')
                product_info["Preis [€]"] = float(price_text)
            else:
                product_info["Preis"] = "Nicht Verfügbar"

            product_info["Uf-Wert [W/M²K]"] = float(product_info["Uf-Wert [W/M²K]"].replace(',', '.'))

            del product_info["Hersteller"]

            if "Holz" in product_info["Produkt"]:
                product_info["Farbe"] = "Standard-RAL-Farben"
                product_info["Material"] = "Holz"
            elif "Kunststofffenster" in product_info["Produkt"]:
                product_info["Material"] = "Kunststoff"
            elif "Kunststoff-Alu-Fenster" in product_info["Produkt"]:
                product_info["Material"] = "Kunststoff-Alu-Fenster"
            elif "Aluminiumfenster" in product_info["Produkt"]:
                product_info["Material"] = "Aluminiumfenster"
            elif "Holz-ALu-Fenster" or "Holz-Aluminium" in product_info["Produkt"]:
                product_info["Material"] = "Holz-Alu"

            print(product_info)

            # Save the Product Info to the List
            all_products.append(product_info)

        except AttributeError as e:
            print(f"Error processing product rows: {e}")

    else:
        print("Table not found on the page.")

# Save all Products Information in a Table
headers = list(all_products[0].keys())

column_widths = {header: max(len(header), max(len(str(product.get(header, ""))) for product in all_products)) for header in headers}

with open("products.txt", "w", encoding="utf-8") as file:
    # Write the headers
    header_line = " | ".join(f"{header:<{column_widths[header]}}" for header in headers)
    file.write(header_line + "\n")
    file.write("-" * len(header_line) + "\n")

    # Write each product's details
    for product in all_products:
        product_line = " | ".join(f"{str(product.get(header, '')):<{column_widths[header]}}" for header in headers)
        file.write(product_line + "\n")

print("\nProduct details saved to 'products.txt'.")
