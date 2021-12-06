#!/usr/bin/python
"""
:brief: Extract all tag attributes from xml and convert to JSON

"""
import datetime


FILE_SIZE = 100000000
import xml.sax.handler
import json
import sys

class Indexer(xml.sax.handler.ContentHandler):
    def __init__(self, data_path="", index_path=""):
        self.parser = xml.sax.make_parser()
        self.parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        self.parser.setContentHandler(self)
        self.attributes = {}
        self.file_num = 0
        self.path = data_path
        self.index_path = index_path
        self.index = {}
        self.index_size = 0
        self.attribute_name = ['AcceptedAnswerId', 'AnswerCount', 'Body', 'CommentCount',
                'CreationDate', 'FavoriteCount', 'Id', 'LastActivityDate', 'LastEditDate', 
                'LastEditorDisplayName', 'LastEditorUserId', 'OwnerUserId', 'PostTypeId', 'Score',
                'Tags', 'Title', 'ViewCount', 'PostId', 'RelatedPostId', 'LinkTypeId', 'TagName',
                'Count', 'ExcerptPostId', 'WikiPostId', 'Reputation', 'DisplayName', 'EmailHash', 'LastAccessDate',
                'AboutMe', 'rel', 'Views', 'UpVotes', 'DownVotes', 'UserId', 'Name', 'Date']

    def startElement(self, name, attrs):
        if name == 'row':
            for name in self.attribute_name:
                try:
                    attr = attrs.getValue(name)
                    self.attributes[name] = attr
                except KeyError:
                    pass

    def endElement(self, name):
        if name == 'row':
            self.index_content()
            self.attributes = {}

    def characters(self, content):
        pass

    def parse_data(self):
        self.parser.parse(self.path)
        self.dump_remaining()

    def dump_remaining(self):
        if self.index_size > 0:
            self.dump_file()

    def dump_file(self):
        with open(f'{self.index_path}/post_{self.file_num}.json', 'w') as f:
            json.dump(self.index, f)
    
    def init_file(self):
        self.file_num += 1
        self.index = {}
        self.index_size = 0

    def index_content(self):
        
        self.index[self.attributes['Id']] = self.attributes
        for key, value in self.attributes.items():
            try:
                self.index_size += len(key) + len(value)
            except:
                pass

        if self.index_size >= FILE_SIZE:
            self.dump_file()
            self.init_file()

if __name__ == "__main__":
    begin = datetime.datetime.now()
    indexer = Indexer(data_path=sys.argv[1], index_path=sys.argv[2])
    indexer.parse_data()
    print(datetime.datetime.now() - begin)