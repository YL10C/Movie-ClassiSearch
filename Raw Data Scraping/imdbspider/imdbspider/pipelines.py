from scrapy.exporters import JsonLinesItemExporter
import os
import pandas as pd


class ImdbspiderPipeline:

    def open_spider(self, spider):
        self.file = open('output.jsonl', 'ab')
        self.exporter = JsonLinesItemExporter(self.file)
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)

        id = item['id']
        processed_url = f"https://www.imdb.com/title/{id}/"
        df = pd.DataFrame([{'url': processed_url}])
        file_exists = os.path.exists('processed_url.tsv')
        df.to_csv('processed_url.tsv', sep='\t', index=False, header=not file_exists,  mode='a')
        return item

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()


