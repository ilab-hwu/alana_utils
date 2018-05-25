#!/usr/bin/env python
# -*- coding: utf-8 -*-


import codecs
import re
import sys
from unidecode import unidecode
import os

# default paths to default profanity files
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PROFANITIES = os.path.join(_SCRIPT_DIR, 'profanities', 'profanities.txt')
DEFAULT_PROF_STRICT = os.path.join(_SCRIPT_DIR, 'profanities', 'profanities_strict.txt')


class SentenceFilter(object):
    """Filter for sentences -- profanity, length, punctuation-only."""

    def __init__(self, cfg):
        self.profanities = None
        if 'profanities' in cfg:
            # use default list for True
            self.profanities = self._load_profanities_list(
                DEFAULT_PROFANITIES if cfg['profanities'] is True else cfg['profanities'])
        self.max_length = cfg.get('max_length', -1)
        self.min_length = cfg.get('min_length', -1)
        self.ban_punct_only = cfg.get('ban_punct_only', False)

    def _load_profanities_list(self, filenames):
        if not isinstance(filenames, list):
            filenames = [filenames]
        profanities = []
        for filename in filenames:
            with codecs.open(filename, 'rb', 'UTF-8') as fh:
                profanities.extend(fh.readlines())
        pattern = r'\b(' + '|'.join([profanity.strip() for profanity in profanities]) + r')\b'
        return re.compile(pattern, re.IGNORECASE)

    class TagNums(object):
        """A helper class for numbering the occurrences of SSML + postprocessing tags in the text."""

        def __init__(self):
            self.counter = 0

        def __call__(self, match):
            self.counter += 1
            return 'XXXTAG%d' % self.counter

    def _protect_tags(self, sent):
        """Find and replace SSML + postprocessing tags."""
        tag_pattern = (r'(?:</?(?:prosody|amazon:effect|audio|emphasis|sub|say-as|break|p|phoneme|s|speak|w|audio)(?: [^>]*)?>|' +
                       r'\*(?:username|driver)\*)')
        tags = re.findall(tag_pattern, sent)
        sent = re.sub(tag_pattern, self.TagNums(), sent)
        return sent, tags

    class TagList(object):
        """A helper class for retrieving SSML + postprocessing tags from a list to insert them into the text."""

        def __init__(self, tags):
            self.counter = 0
            self.tags = tags

        def __call__(self, match):
            tag = self.tags[self.counter]
            self.counter += 1
            return tag

    def _return_tags(self, sent, tags):
        return re.sub(r'XXXTAG[0-9]+', self.TagList(tags), sent)

    def normalize_encoding(self, sent, check_tags=True):
        """Just fix encoding -- remove all non-ASCII characters, HTML tags, entities, URLs.
        @param sent: the sentence to normalize
        @param check_tags: protect SSML + postprocessing tags? (default: True)
        @return: the normalized sentence
        """
        # normalize unicode
        sent = unidecode(sent)
        if check_tags:
            sent, tags = self._protect_tags(sent)
        # remove URLs, HTML tags and entities, weird characters
        sent = re.sub(r'https? ?: ?/ ?/[^ ]*', '', sent)
        sent = re.sub(r'&(amp|lt|gt);', '', sent)
        sent = re.sub(r'< ?/? ?(strong|b|span|u|i|em|h[1-7]|li|ul|ol|div)(?: [^>]*)?>', '', sent)
        sent = re.sub(r'\[[^)]*\]', '', sent)  # delete all stuff in brackets
        sent = re.sub(r'\([^)]*\)', '', sent)  # delete all stuff in brackets
        sent = re.sub(r'[a-z.]*@[a-z.]*', '', sent)  # delete email adresses
        sent = re.sub(r'[^A-Za-z0-9\',;:!?.-]', ' ', sent)  # delete all but listed characters
        sent = re.sub(r' +', r' ', sent).strip()
        # return SSML+postprocessing tags
        if check_tags:
            sent = self._return_tags(sent, tags)
        return sent

    def filter_sentence(self, sent):
        """Normalize a sentence and pass it through the filter (profanity, length, punct-only).
        @param sent: the sentence to be filtered
        @return: normalized sentence, or None if it does not passed the filter
        """
        # normalize sentence
        sent, tags = self._protect_tags(sent)
        sent = self.normalize_encoding(sent, check_tags=False)

        # sentence contains profanities
        if self.profanities and re.search(self.profanities, sent):
            return None

        # sentence too long
        if self.max_length >= 0 and sent.count(' ') > self.max_length:  # TODO approximation
            return None
        # sentence too short
        if self.min_length >= 0 and sent.count(' ') < self.min_length - 1:
            return None
        # sentence only contains punctuation characters
        if self.ban_punct_only and re.match(r'^[ \',;:!?.-]*$', sent):
            return None

        # return SSML + postprocessing tags
        sent = self._return_tags(sent, tags)
        return sent

    def check_sentence(self, sent):
        """Check whether a given sentence passes the filter (profanity, length, punct-only).
        @param sent: the sentence to check
        @return: True/False indicating if the sentence passes the check.
        """
        return self.filter_sentence(sent) is not None


if __name__ == '__main__':

    sf = SentenceFilter({'profanities': True})

    stdin = codecs.getreader('UTF-8')(sys.stdin)
    stdout = codecs.getreader('UTF-8')(sys.stdout)

    for line in stdin:
        res = sf.filter_sentence(line)
        if res:
            print(res, "\n")
        else:
            print('<<REMOVED>>', "\n")
