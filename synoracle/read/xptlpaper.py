"""
A module containing tools to do high-level text mining on complete scientific articles.
Primarily uses ChemDataExtractor and its functionality.
Additionally uses the surface area/pore volume mining scripts from Smit/Kim groups.

Author: Joe Manning (@jrhmanning, joseph.manning@manchester.ac.uk)
Date: Nov 2022

Classes:
ExperimentalPaper - the main class containing the ChemDataExtractor Document object and useful analysis methods/other data

Exceptions:
InvalidInputError - Raised if no manuscript cna be found (as either an XML or HTML file)
InputFileContentError - Raised if the file exists, but no usable manuscript/info was found therein
SynthesisParseError - Raised if no data could be found from the Smit/Kim code. Defunct?
"""

import logging
import pathlib
from .propertyreaders.html_PV_extract import smit_PV_extract
from .propertyreaders.html_SA_extract import smit_find_sa
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


class SynthesisParseError(Exception): pass

class ExperimentalPaper:
    """
    A class containing all the key methods for text mining a full manuscript.

    Key methods:
    : produce_property_dataframe: Applies the Kim/Smit surface area mining code to the article
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

    # def locate_inputs(self, source_paragraph, source_directory):
    #     paragraph_path = pathlib.Path(source_paragraph)
    #     self.doi_suffix = paragraph_path.stem
    #     if not paragraph_path.is_file():
    #         raise InvalidInputError(f"Cannot find extracted synthesis paragraph for paper {self.doi_suffix} (file: {paragraph_path})")
    #     logging.info('Paper found with DOI suffix: {0}'.format(self.doi_suffix))
    #     sourcedir = paragraph_path.parent.absolute()
    #     self.find_paper(self.doi_suffix, sourcedir, filetype)
    #     #self.load_xml(self.doi_suffix, sourcedir)
    #     # with open(source_paragraph, encoding='utf-8') as f:
    #     #     self.raw_text = f.read()
    #     # if len(self.raw_text) == 0:
    #     #     raise InputFileContentError(f'Empty procedure txt file loaded in!')
    #     logging.info('Paper loaded in from {0} \n'.format(paragraph_path.parts[-1]))

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


    # Defunct?
    # def load_xml(self, source_paragraph, sourcedir):
    #     """
    #
    #     :param source_paragraph:
    #     :param sourcedir:
    #     :return:
    #     """
    #     from lxml import etree
    #     from lxml.etree import XMLSyntaxError
    #     xml_filename = sourcedir / (source_paragraph + '.xml')
    #     if not xml_filename.is_file():
    #         raise InvalidInputError(f"Cannot find extracted xml actions for paper {self.doi_suffix}")
    #     with open(xml_filename, 'rb') as f:
    #         raw = f.read()
    #     try:
    #         self.working_xml = etree.fromstring(raw)
    #     except XMLSyntaxError as e:
    #         logging.error('Cannot read extracted xml actions for paper {0}'.format(self.doi_suffix))
    #         raise InputFileContentError
    #     logging.info('XML loaded in from {0}'.format(xml_filename.parts[-1]))

    property_read_dict = {
        'SA': smit_find_sa,
        'PV': smit_PV_extract
    }

    def produce_property_dataframe(self, property:str = 'SA') -> pd.DataFrame:
        """
        Creates a Pandas dataframe of all identified properties within the manuscript, using the Kim/Smit TDM method
        :param property: Which property to search for, used as a dictionary lookup in property_read_dict
        :return: A DataFrame containing all identified quantities
        """
        assert property in self.property_read_dict.keys()
        prop_frame = self.property_read_dict[property](self.manuscript_name)

        if len(prop_frame) < 1:
            logging.warning(f'Warning! No {property} data identified!')
            prop_frame = pd.DataFrame(columns={0: 'Name', 1: 'Measurement', 2:'Value', 3:'unit'})
            # raise SynthesisParseError(f"Could not find any surface area data included!")
        else:
            pass
            # prop_string, prop_frame = self.report_prop(property)
        logging.info(prop_frame)
        logging.info('--------------------------')
        return prop_frame

    # Defunct?
    # def report_prop(self, property:str = 'SA'):
    #     try:
    #         self.SSA
    #     except AttributeError:
    #         self.SSA = smit_find_sa(self.manuscript)
    #
    #     output_str = ''
    #
    #     if len(self.SSA) > 0:
    #         SA_frame = pd.DataFrame(self.SSA).rename({0: 'Name', 1: 'SSA type', 2: 'Specific surface area', 3: 'unit'},
    #                                                  axis=1)
    #         logging.debug(SA_frame)
    #         for framework in self.targets:
    #             valid_SA = SA_frame['Name'].str.contains(framework)
    #             SA_str = f'{framework}: '
    #             if len(valid_SA) == 0:
    #                 SA_str += 'Not identified'
    #             elif len(valid_SA) > 1:
    #                 SA_str += 'Ambiguous (multiple values identified);\n\t' + ', '.join(
    #                     [x.to_string(index=False).replace('\n', '') for _, x in SA_frame[valid_SA].iterrows()])
    #             elif len(valid_SA) == 1:
    #                 SA_str += f"{SA_frame['Specific surface area'][valid_SA]} {SA_frame['unit'][valid_SA]} ({SA_frame['SSA type'][valid_SA]})"
    #             else:
    #                 SA_str += 'Unparseable (check your inputs!)'
    #
    #             output_str += SA_str
    #             output_str += '\n'
    #
    #     else:
    #         for framework in self.targets:
    #             output_str += f'{framework} (no surface data)\n'
    #         null_data = {
    #             'Name': {0: np.nan},
    #             'SSA type': {0: np.nan},
    #             'Specific surface Area': {0: np.nan},
    #             'unit': {0: np.nan}
    #         }
    #         SA_frame = pd.DataFrame(null_data)
    #         print(SA_frame)
    #         # SA_frame = pd.DataFrame(columns = {0: 'Name', 1:'SSA type', 2:'Specific surface area', 3:'unit'})
    #     return output_str, SA_frame

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
                #print(self.cde_doc.elements[c].cems)
                # print(f"\t\t\033[1m Number of identified chemical entities: {len(d.elements[c].cems)}\033[0m")
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