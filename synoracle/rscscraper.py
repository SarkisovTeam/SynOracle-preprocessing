"""
A module containing tools to scrape article HTMLs, figures, and SI documents for text and data mining.

Author: Joe Manning (@jrhmanning, joseph.manning@manchester.ac.uk)
Date: Nov 2022

Classes:
RSCScraper - the main class for scraping formation from the RSC

Exceptions:
CredentialError - an error raised when permissions are denied during scraping
"""
from selenium import webdriver
from time import sleep
from selenium.common.exceptions import NoSuchElementException
import errno, os


def CredentialError(Exception): pass


class RSCScraper:
    """
    A class for scraping research articles and associated data from the Royal Society of Chemistry.
    Creates a selenium webdriver for navigating around the RSC website, and goes through steps to download:
    - HTML-formatted article text
    - low-res images from the article
    - text-based SI documents

    Credentials for log-in (if-needed) are provided through individual membership IDs and passwords (not provided).

    Key methods:
    : _check_credentials: determines if member login is requires
    : _login: logs in to the RSC for downloading, using provided member credentials as a dictionary
    : _extract_text: scrapes the HTML representation of the article and stores it as the self.rawHTML class variable
    : _extract_images_to_dict: sequentially extracts the binary code and caption text for each image in the particle, storing them as a dictionary at self.image_dict
    : _get_SI: downloads SI files if they have a compatible file format
    : _doi_string: produces a withows path-safe abbreviation of the DOI to act as a unique paper identifier
    : _prepare_directory: Creates a directory tree for outputting the gathered data to the system
    : extract_from_doi: Does all the above in one place.

    """

    def __init__(self, outputdir: str=None, driver: webdriver=None) -> None:
        """
        Instantiates the class and webdriver.
        :param outputdir: the path to your directory for paper outputs. TODO: change to handle Path objects too
        :param driver: provide your own, in case you're not using the default driver
        """
        self.options = webdriver.ChromeOptions()
        self.SI_keys = ['PDF', 'pdf', 'DOCX', 'docx']
        if not outputdir:
            self.outputdir = './RSCScraper_output/'
        else:
            self.outputdir = outputdir

        if not driver:
            self._instantiate_driver()
        else:
            self.driver=driver

    def _instantiate_driver(self):
        """ Makes a simple ChromeDriver"""
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.implicitly_wait(2)

    def _check_credentials(self, url: str=None) -> bool:
        """
        Attempts ot access an RSC paper to test if login is required. Defaults to a random non-open access example.
        :param url: the URL of the paper in question
        :return: True if no log in is required, else False
        """
        if not url:
            working_url = "https://pubs.rsc.org/en/content/articlelanding/2009/cp/b823233d/unauth"
        else:
            working_url = url

        self.driver.get(working_url)
        try:
            self.driver.find_element_by_partial_link_text("Article HTML")
            return True
        except NoSuchElementException:
            return False

    def _login(self, username: str, password: str, url: str=None):
        """
        Logs in to the RSC using your membership credentials
        :param username: Your RSC username
        :param password: Your RSC password
        :param url: The paper's URL, defaults to a random example
        :return: None
        """
        if not url:
            working_url = "https://pubs.rsc.org/en/content/articlelanding/2009/cp/b823233d/unauth"
        else:
            working_url = url
        print(working_url)
        self.driver.get(working_url)
        try:
            self.driver.find_element_by_partial_link_text("Sign in").click()
            self.driver.find_element_by_id("SubscriberLoginData_UserName").send_keys(username)
            self.driver.find_element_by_id("SubscriberLoginData_Password").send_keys(password)
            self.driver.find_element_by_xpath(
                "//*[@id='maincontent']/div[2]/div/div[1]/section[1]/div/div/form/input").click()
            sleep(4)
            self.driver.find_element_by_xpath("//*[@id='DownloadOption']/div/a[2]")
            print('Login attempt successful!')
        except NoSuchElementException:
            sleep(2)
            try:
                self.driver.find_element_by_xpath("//*[@id='DownloadOption']/div/a[2]")
            except NoSuchElementException:
                print('No HTML file option found, skipping!')
                raise
            print('Login attempt failed! Perhaps you\'re already logged in?')

    def _extract_text(self, url: str):
        """
        Downloads the page source as HTMl. To funciton for later stages of the workflow, this should be the "View
        HTML" page, not the landing page
        :param url: the URL of the paper; no default
        :return: None
        """
        self.driver.find_element_by_xpath("//*[@id='DownloadOption']/div/a[2]").click()
        sleep(2)
        self.rawHTML = self.driver.page_source

    def _extract_images_to_dict(self, url: str):
        """
        Loops through all images in the article, signified by the "image_table" html tag.
        Extracts image binaries and captions to a dictionary, for saving to file.
        Saves it as the self.image_dict variable.

        WARNING: does not clear the image dictionary if it already exists.
        TODO: decide if I need to change image_dict instantiation
        :param url: the URL of the paper; no default
        :return: None
        """
        try:
            self.image_dict
        except AttributeError:
            self.image_dict = {}

        images = self.driver.find_elements_by_class_name('image_table')

        for count, img_table in enumerate(images, 1):

            try:
                self.image_dict[count]

            except KeyError:
                self.image_dict[count] = {}

            img_holder = img_table.find_element_by_class_name('imgHolder')
            img_id = img_holder.get_attribute('id')

            img = img_holder.find_element_by_xpath(f"//*[@id='{img_id}']//img")
            src = img.get_attribute('src')

            ss = img.screenshot_as_png
            self.image_dict[count]['src'] = src
            self.image_dict[count]['image'] = ss

            try:
                img_caption = img_table.find_element_by_class_name('image_title')
                self.image_dict[count]['caption'] = img_caption.text
            except NoSuchElementException: # The case of chemical structures, for example
                print(f"image caption {count} of {len(images)} not found!")
                self.image_dict[count]['caption'] = 'None'

    def _get_SI(self, url: str):
        """
        Checks for SI documents with matching file extensions and downloads them.
        I think there's a line somewhere which sets the default download destination to the target directory
        TODO: Confirm _get_SI is not just filling up your downloads folder
        :param url: the URL of the paper; no default
        :return: None
        """
        try:
            SI_elements = self.driver.find_elements_by_xpath('//*[@id="divAbout"]/div[2]/ul/li/a')
            matching_elements = []
            for i in SI_elements:
                working = [y for y in self.SI_keys if y in i.text]
                if len(working) > 0:
                    matching_elements.append(i)
            print([i.text for i in matching_elements])
            for i in matching_elements:
                i.click()
                sleep(2)
            print(f'{len(matching_elements)} SI file(s) downloaded!')

        except NoSuchElementException:
            print('No SI found!')

    def _doi_string(self):
        """ Returns a cleaned version of the DOI for use as a paper unique ID in the file tree"""
        return self.DOI.split('/')[-1].replace('.', '')

    def _prepare_directory(self) -> str:
        """
        Creates directories for outputting images, SI and the manuscript to file.
        Useful if you're wanting to keep images with the manuscript.
        :return: the location of the outputfolder, as a string
        """
        doi_str = self._doi_string()
        try:
            os.makedirs(f'{self.outputdir}/{doi_str}/figs/')
            os.makedirs(f'{self.outputdir}/{doi_str}/paragraphs/')
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        return f'{self.outputdir}/{doi_str}/'

    def extract_from_doi(self, doi: str, username:str=None, password: str=None, output_type: str='Full'):
        """
        Combined workflow to download a paper from the RSC given a specific DOI.
        TODO: add functionality for different modes of scraping (with images and SI or not)
        :param doi: the DOI of the article you want to download
        :param username: your username for the RSC
        :param password: your password for the RSC
        :param output_type: flag for if you want one folder per paper, or one folder with lots of papers in only
        :return: None
        """
        self.DOI = doi
        self.url = f'https://doi.org/{self.DOI}'
        out_dir = self._prepare_directory()

        self._instantiate_driver()

        self.options.add_experimental_option('prefs', {
            "download.default_directory": out_dir,  # Change default directory for downloads
            # "download.prompt_for_download": False, #To auto download the file
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True  # It will not show PDF directly in chrome
        })
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')  # Last I checked this was necessary.

        logged_in = self._check_credentials()
        if not logged_in:
            self._login(username=username, password=password)
            sleep(1)
            logged_in = self._check_credentials()

        if not logged_in:
            raise CredentialError('Cannot login to RSC!')

        print(self.DOI.split('/')[0])
        assert self.DOI.split('/')[0] == '10.1039'  # confirms it's an RSC paper

        self._extract_text(self.url)
        self.image_dict = {}
        try:

            self._extract_images_to_dict(self.url)
            self.driver.back()
        except NoSuchElementException:
            sleep(5)
            try:
                self._extract_images_to_dict(self.url)
                self.driver.back()
            except NoSuchElementException:
                raise
        sleep(2)
        self._get_SI(self.url)

        with open(f'{out_dir}/raw.html', 'w', encoding='utf-8') as f:
            f.write(self.rawHTML)
        # with open(f'{out_dir}/soup.txt', 'w', encoding='utf-8') as f:
        #    f.write(self.soup)
        print(f'Output main text to file at {out_dir}!')
        with open(f'{out_dir}/fig_captions.csv', 'w', encoding='utf-8') as f:
            keys = list(self.image_dict.keys())
            values = [self.image_dict[i]['caption'] for i in keys]
            f.write('\n'.join([f'fig. {k}\t {v}' for k, v in zip(keys, values)]))

        for k, v in self.image_dict.items():
            with open(f'{out_dir}/figs/fig{k}.png', 'wb') as f:
                f.write(v['image'])
        self.driver.close()


if __name__ == '__main__':
    pass
