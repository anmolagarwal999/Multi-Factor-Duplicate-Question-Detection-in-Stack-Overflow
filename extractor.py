#!/usr/bin/python
import datetime

import config

## <row Id="777711" PostTypeId="1" AcceptedAnswerId="777721" CreationDate="2009-04-22T15:07:54.137" Score="0" 
# ViewCount="175" 
# Body="&lt;blockquote&gt;&#xA;  &lt;p&gt;Duplicate:&#xA;  &lt;a href=&quot;http://stackoverflow.com/questions/163434/are-nulls-in-a-relational-database-okay&quot;&gt;http://stackoverflow.com/questions/163434/are-nulls-in-a-relational-database-okay&lt;/a&gt;&lt;/p&gt;&#xA;&lt;/blockquote&gt;&#xA;&#xA;&lt;p&gt;
# I dodged a heated debate concerning nulls in the database today.&#xA;My opinion is that null is an excellent indicator of unspecified values. Every one else in the team, that has an opinion, thinks zero and empty strings are the way to go.&lt;/p&gt;&#xA;&#xA;&lt;p&gt;Are they lazy or am I to strict?&lt;/p&gt;&#xA;" 
# OwnerUserId="21761" LastEditorUserId="44389" LastEditorDisplayName="" LastEditDate="2009-04-22T15:10:22.710" LastActivityDate="2009-04-22T15:11:00.667" 
# ClosedDate="2009-04-22T15:11:06.530" Title="Is null harmful? [Duplicate]" Tags="&lt;asp.net&gt;&lt;sql&gt;&lt;database&gt;&lt;null&gt;" AnswerCount="4" CommentCount="1" />

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

        if self.index_size >= config.FILE_SIZE:
            self.dump_file()
            self.init_file()

if __name__ == "__main__":
    begin = datetime.datetime.now()
    indexer = Indexer(data_path=sys.argv[1], index_path=sys.argv[2])
    indexer.parse_data()
    print(datetime.datetime.now() - begin)