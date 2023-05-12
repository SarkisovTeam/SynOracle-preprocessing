<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->




<!-- PROJECT LOGO -->

[//]: # (<br />)

[//]: # (<div align="center">)

[//]: # (  <a href="https://github.com/github_username/repo_name">)

[//]: # (    <img src="images/logo.png" alt="Logo" width="80" height="80">)

[//]: # (  </a>)

<h3 align="center">Synthetic Oracle</h3>
<div>
  <p align="center">
    A python-based tool for parsing and interpreting experimental synthesis reports.
    <br />
    <a href="https://github.com/jrhmanning/SynOracle/doc"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/jrhmanning/SynOarcle/demo">View Demo</a>
    ·
    <a href="https://github.com/jrhmanning/SynOracle/issues">Report Bug</a>
    ·
    <a href="https://github.com/jrhmanning/SynOracle/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

[//]: # ([![Product Name Screen Shot][product-screenshot]]&#40;https://example.com&#41;)

A Python-based tool to extract process-like synthesis procedures from chemical descriptions of synthesis procedures. This module describes workflows to:
1. Find synthesis reports in the literature
2. Automatically download the paper text
3. Identify paragraphs likely containing synthesis procedures
4. Extracting a sequence of synthesis actions from each paragraph
5. Sorting and organising this information into useful data for further analysis or laboratory recreation of the synthesis 

This workflow relies heavily on previously published text mining tools like [ChemDataExtractor 2.1](http://www.chemdataextractor2.org/) and [ChemicalTagger](https://chemicaltagger.ch.cam.ac.uk/), alongside various tools for data postprocessing including [pandas](https://pandas.pydata.org/), [pint](https://pint.readthedocs.io/en/stable/), and [pubchempy](https://pubchempy.readthedocs.io/en/latest/).

<!-- Here's a blank template to get started: To avoid retyping too much info. Do a search and replace with your text editor for the following: `github_username`, `repo_name`, `twitter_handle`, `linkedin_username`, `email_client`, `email`, `project_title`, `project_description` -->

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

Although most of the tools used for this package are python-native, a couple of supplementary software packages are required to install a local copy of Synthetic Oracle on your machine.

### Prerequisites

ChemicalTagger is written in Java, requiring both the precompiled .jar executable (provided) and a native installation of java to run it. 
You can get java directly from Oracle (e.g. [here](https://www.oracle.com/uk/java/technologies/downloads/#java17)), enabling later execution of ChemicalTagger from the command line like so:
  ```sh
  java chemicalTagger-1.6-SNAPSHOT-jar-with-dependencies-file.jar "inputfile.txt" "outputfile.xml"
  ```

Similarly, ChemDataExtractor requires a C++ compiler to be installed, which does not come prepackaged with Windows. Windows C++ build tools can be similarly obtained free from Microsoft (e.g. [here](https://visualstudio.microsoft.com/downloads/)).

Finally, scraping papers from publishers like the RSC requires a webdriver application for python-driven webpage loading. Common examples are [Chromedriver](https://chromedriver.chromium.org/downloads) and [Geckodriver](https://github.com/mozilla/geckodriver/releases), which must be downloaded directly and added to your system `PATH`. One common issue with Chromedriver especially is that it must match the currently installed version of Chrome on the computer - if Google automatically updates to a newer version, you will have to manually update Chromedriver to continue working.

Once these are installed, the remaining packages can be installed through pip with the following command:

   ```sh
   pip install -r requirements.txt
   ```

### Installation

1. Clone the repository
   ```sh
   git clone https://github.com/jrhmanning/SynOracle.git
   ```
2. Install pip requirements (preferable in a fresh python environment)
   ```sh
   pip install -r requirements.txt
   ```
3. Obtain credentials for text mining from [Elsevier](https://dev.elsevier.com/), if required.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

To build a database of published syntheses for a given material, a six-step workflow is required, which will be briefly described here. Jupyter notebooks are provided with example code for ZIF-8, for your convenience.

1. Locate papers using `elsapy` and your self-defined keywords
2. Download a corpus of papers from each publisher identified
3. Extract plain text synthesis paragraphs from each paper downloaded
4. Process the paragraphs into hierarchical XML sequences, and extract sequential information to dataframes
5. Cross-reference extracted data against chemical databases to calculate quantities in standardised units
6. Summarise and analyse the identified sequences for further analysis

Each of these steps are discussed in detail in the documentation and demo. For convenience, minimum working examples for each step are provided below. 

### Finding papers


### Downloading papers
<!-- Generally speaking, each publisher has their own internal rules for text and data mining (TDM), including unique file formats for each individual paper as well as unique methods of accessing them. This document won’t provide an exhaustive guide (which can be found elsewhere) but will attempt to give an overview of the field using case studies from some of the largest chemical publishers. In general, there are three different strategies to perform TDM through a publisher – by interfacing with a human, with the publisher’s website directly, or with an online REST API, or. Each of these methods is contingent on your institution having a subscription with the publisher in question, which you check by trying to manually access the paper using your institutional login. --> 


### Identifying synthesis paragraphs

### Extracting hierarchical data from paragraphs

### Cross-referencing chemical information extracted

### Analysing data trends



<!-- Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_
-->
<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [ ] Identification of MOFID to automatically identify chemical constraints on synthesis
- [ ] Quality metrics for synthesis parsing
- [ ] Generating material-by-material synthesis reports with summary data and details, à la David Fairen-Jiminez' [MOFexplorer](http://aam.ceb.cam.ac.uk/mofexplorer.html)
    - [ ] Define steps to build a plotly dashboard
    - [ ] Put them in here

See the [open issues](https://github.com/github_username/repo_name/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Joe Manning - [@jrhmanning](https://twitter.com/jrhmanning) - joseph.manning@manchester.ac.uk

<!-- Project Link: [https://github.com/github_username/repo_name](https://github.com/github_username/repo_name) -->

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* []()
* []()
* []()

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/github_username/repo_name.svg?style=for-the-badge
[contributors-url]: https://github.com/github_username/repo_name/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/github_username/repo_name.svg?style=for-the-badge
[forks-url]: https://github.com/github_username/repo_name/network/members
[stars-shield]: https://img.shields.io/github/stars/github_username/repo_name.svg?style=for-the-badge
[stars-url]: https://github.com/github_username/repo_name/stargazers
[issues-shield]: https://img.shields.io/github/issues/github_username/repo_name.svg?style=for-the-badge
[issues-url]: https://github.com/github_username/repo_name/issues
[license-shield]: https://img.shields.io/github/license/github_username/repo_name.svg?style=for-the-badge
[license-url]: https://github.com/github_username/repo_name/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/linkedin_username
[product-screenshot]: images/screenshot.png
[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
[Next-url]: https://nextjs.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 