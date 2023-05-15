"""
A module containing tools to do high-level text mining on complete scientific articles.
Primarily uses ChemDataExtractor and its functionality.

Author: Joe Manning (@jrhmanning, joseph.manning@manchester.ac.uk)
Date: Nov 2022

Classes:
ExperimentalPaper - the main class containing the ChemDataExtractor Document object and useful analysis methods/other data

Exceptions:
InvalidInputError - Raised if no manuscript cna be found (as either an XML or HTML file)
InputFileContentError - Raised if the file exists, but no usable manuscript/info was found therein
"""

import logging
import pathlib

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Union
from chemdataextractor import Document
from chemdataextractor.doc import Sentence, Paragraph
from itertools import tee
import re
from typing import Tuple

# create logger
logger = logging.getLogger('simple_example.txt')
logger.setLevel(logging.INFO)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
logger.addHandler(ch)


class InvalidInputError(Exception): pass


class InputFileContentError(Exception): pass


class ExperimentalPaper:
    """
    A class containing all the key methods for text mining a full manuscript.

    Key methods:
    : create_cde_doc: Creates a ChemDataExtractor document for later analysis
    : count_quantities: Performs a regex and part-of-speech search on a sentence in the CDE document
    : count_all_quantities: Performs count_quantities on all sentences within a paragraph
    : identify_key_paragraphs: Uses count_all_quantities to identify likely synthesis paragraphs within the paper
    : output_paragraphs: Writes the raw text of paragraphs identified by identify_key_paragraphs to file

    """
    def __init__(self, paper_identifier: str, source_directory: Union[str, Path] = Path('./')):
        """
        Locates and imports all the raw paper files when given an identifier and location
        :param paper_identifier: The unique paper identifier - either an Elsevier PII or sanitised DOi
        :param source_directory: The folder where the paper is in
        """

        # First locate the files you need, and check they're imported properly:
        logging.info('Gathering initial files:\n----------------------')
        self.source_directory = Path(source_directory)
        self.paper_id = paper_identifier

        try:
            logging.info('Trying to read in manuscript as an html file')
            filename = self.source_directory / (paper_identifier + '.html')
            self._find_paper(filename)
        except InvalidInputError:
            logging.info('Manuscript not found as a html file, trying again as an xml.')
            try:
                filename = self.source_directory / (paper_identifier + '.xml')
                self._find_paper(filename)
            except InvalidInputError:
                logging.info('Manuscript not found as an xml or html file!')
                raise

        logging.info('Files processed, ready to extract information\n-------------------------------------')

    def _find_paper(self, manuscript_name: str):
        """
        Loads in the paper manuscript given a specific file name
        :param manuscript_name: The manuscript's file name
        :return: none
        """
        if not manuscript_name.is_file():
            raise InvalidInputError(f"Cannot find source manuscript! (name given: {manuscript_name})")
        with open(manuscript_name, 'r', encoding='utf-8') as f:
            self.manuscript = f.read()
            if len(self.manuscript) == 0:
                raise InputFileContentError('Empty manuscript file loaded in!')
        self.manuscript_name = manuscript_name
        logging.info('Manuscript loaded in from {0}'.format(manuscript_name))

    def create_cde_doc(self):
        """ Creates a ChemDataExtractor document of the manuscript for analysis"""
        try:
            self.manuscript
        except:
            raise InvalidInputError('No manuscript loaded!')
        with open(self.manuscript_name, 'rb') as f:
            self.cde_doc = Document.from_file(f)

    # region cde ancillary functions
    def _pairwise(self, iterable):
        "s -> (s0,s1), (s1,s2), (s2, s3), ..."
        a, b = tee(iterable)
        next(b, None)
        return zip(a, b)

    def count_quantities(self, sentence: Sentence) -> Tuple[list, int]:
        """
        Finds likely physical quantities within a sentence.
        Makes use of ChemDataExtrctor POS tagging to identify  (CD, NN) word pairs.
        Then uses Regex to pattern-match the second item int he pair against a specific physical unit.
        TODO: simplify the output data format to just be a list (and confirm quantitycounter = len(list))
        TODO: check that there's no issues with mismatched parentheses in the tokens/sentence.
        :param sentence: the POS-tagged sentence
        :return: A tuple of the individual regex matches for units and the total amount identified
        """
        output_strings = []
        cu_m = r'(((C|c)ubic met(er(s?)?|re(s?)?))|(\b(m|M)3)|(\b(M|m)et(er(s?)?|re(s?)?) cube(d?)))'
        lit = r'(((L|l)((itre(s?)?)|(iter(s?)?)))|(dm3)|(((c|C)ubic) (D|d)ecimet(er(s?)?|re(s?)?))|(((D|d)ecimet((er(s?)?|re(s?)?)) (cube(d?))))|\b(l|L)\b)(?=[^L-])'
        ml = r'(((m|M)(L|l))|(M|m)illilit(re(s?)?|er(s?))|(c|C)m3|(C|c)ubic centimet(er(s?)?|re(s?)?)|\b(C|c)entimet(er(s?)?|re(s?)?) cube(d?))'
        ul = r'(\b((u|U|μ|µ)(L|l)\b)|(M|m)icrolit(re(s?)?|er(s?))|(m|M)m3|(C|c)ubic millimet(er(s?)?|re(s?)?)|\b(M|m)illimet(er(s?)?|re(s?)?) cube(d?))'
        mol = r'((m?)(M|m)(ol)(e(s)?)?)'
        conc = r'((m|n|μ)?(M|molar)\b)'
        gram = r'(\b(m|M|k|K|n|μ)?(g|G)(ram(s)?)?)'
        equiv = r'(e|E)quiv(alent?)(s?)'
        excess = r'(E|e)xcess'
        all_units = [cu_m, lit, ml, ul, mol, gram, equiv, excess, conc]
        text = [j[0] for j in sentence.pos_tagged_tokens]
        tags = [j[1] for j in sentence.pos_tagged_tokens]

        quantitycounter = 0
        for i in zip(self._pairwise(tags), self._pairwise(text)):
            if i[0] == ('CD', 'NN') or i[0] == ('CD', 'NNS'):
                if any([re.match(x, i[1][1]) for x in all_units]):
                    try:
                        working = re.compile(rf'{re.escape(i[1][0])}.{re.escape(i[1][1])}')

                    except:
                        print(i[1])
                        raise
                    output_strings.append(working)

                    quantitycounter += 1
        return output_strings, quantitycounter

    def count_all_quantities(self, paragraph: Paragraph) -> Tuple[list, int]:
        """
        Sequentially performs count_quantities on each sentence within a paragraph, and returns the
        TODO: tidy up outputs so it's just a list, not a tuple
        TODO: some kind of error handling to cope with empty Paragraphs?
        :param paragraph: a Paragraph of POS-tagged Sentence objects
        :return: A tuple of the individual regex matches for units and the total amount identified
        """
        total_counter = 0
        paragraph_strings = []
        for sentence in paragraph:
            logging.debug(sentence)
            sen_string, counter = self.count_quantities(sentence)
            total_counter += counter
            paragraph_strings.extend(sen_string)
        return paragraph_strings, total_counter

    # endregion

    def identify_key_paragraphs(self):
        """
        Iterates through the entire manuscript as a CDE document, counting chemical mentions and physical quantities.
        Creates a dictionary of candidate paragraphs in the form {paper paragraph index: paragraph.
        TODO: add in fnuctionality to see what has been identified within the output dict?
        :return: None
        """
        try:
            self.cde_doc
        except:
            raise InvalidInputError('No manuscript loaded!')

        self.candidate_paragraphs = {}

        for c, paragraph in enumerate(self.cde_doc.paragraphs):
            if len(paragraph.cems) > 2:

                names,quantities = self.count_all_quantities(paragraph)
                logging.debug(quantities, names)
                if quantities > 2:
                    self.candidate_paragraphs[c] = paragraph

    def output_paragraphs(self, output_dir: Union[str, Path]=None):
        """
        Prints out all of the identified synthesis pargraphs to individual text files for individual analysis.
        :param output_dir: The folder to print out the paragraph(s) to, defaults to the source directory
        :return: None
        """
        if not output_dir:
            output = Path(self.source_directory)
        else:
            output = Path(output_dir)

        for num, text in self.candidate_paragraphs.items():
            output_name = output / f'{self.paper_id}.{num}.txt'
            with open(output_name, 'w', encoding='utf-8') as f:
                f.write(text.text)