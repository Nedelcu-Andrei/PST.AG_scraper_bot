# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pandas as pd
from datetime import datetime


class JoinScraperPipeline:
    def process_item(self, item, spider):
        return item


class XlsxNameFormatPipeline:
    """
    Pipeline to save the spider output to a XLSX file.
    """
    def __init__(self):
        self.items = []

    def process_item(self, item, spider):
        self.items.append(item)
        return item

    def close_spider(self, spider):
        # Create a DataFrame from the items
        df = pd.DataFrame(self.items)

        # Define the output file name and sheet name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{spider.name}_{timestamp}.xlsx"
        sheet_name = spider.name

        df_col_ord = ['page_url', 'category', 'title', 'reward_amount',
                      'associated_organizations',
                      'associated_locations', 'about', 'image_urls', 'date_of_birth']

        # Write the DataFrame to the XLSX file
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False, columns=df_col_ord)

        spider.log(f'Saved {len(self.items)} items to {filename} (sheet: {sheet_name})')


class JsonNameFormatPipeline:
    """
    Pipeline to save spider output to a JSON file.
    """
    def __init__(self):
        self.items = []

    def process_item(self, item, spider):
        self.items.append(item)
        return item

    def close_spider(self, spider):
        # Create a DataFrame from the items and set column order
        df_col_ord = ['page_url', 'category', 'title', 'reward_amount', 'associated_organizations',
                      'associated_locations', 'about', 'image_urls', 'date_of_birth']
        df = pd.DataFrame(self.items, columns=df_col_ord)

        # Time format
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Define the filename and write the DataFrame to JSON
        filename = f"{spider.name}_{timestamp}.json"
        df.to_json(filename, orient='records')

        spider.log(f'Saved {len(self.items)} items as JSON to {filename}.')
