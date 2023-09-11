# AT Detection System Prototype

This directory contains the prototype tool created based on the AT detection system presented at CCS'23. The tool accepts a URL as input, visits the corresponding website, and displays the model's predictions for the external JS resources.

## Table of Contents

- [Getting Started](#getting-started)
	- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Output](#output)
- [Contribution & Citing](#contribution--citing)
- [Additional Notes](#additional-notes)

## Getting Started

### Setup and Installation

1. **Compile Chromium**: You must compile the Chromium browser using the provided patch. The necessary patch can be found in the `chromium` directory and the instruction to build Chromium can be found [here](https://chromium.googlesource.com/chromium/src/+/main/docs/building_old_revisions.md). Ensure to patch V8 before compiling. After compilation, include the path to the compiled `Chromium` in `run-puppeteer.js`
2. **Dependencies**: Install the necessary dependencies:
   - For Node.js dependencies: `npm install` (based on `package.json`).
   - For Python dependencies: `pip install -r requirements.txt`.
3. **Deep Learning Model**: Ensure you have `nlplay` set up for the deep learning model. Instructions can be found in the main page of the repository.
4. **Filter Lists**: Place your filter lists in the `lists` directory. Ensure to include the correct names in `run-puppeteer.js`.
5. **Models**: The required models can be downloaded from [here](https://drive.google.com/file/d/1tfZ7a74qyAnQAazRMl3LovuEHmUl1YgD/view?usp=share_link). Once downloaded, unzip them and place them in an `artifacts` directory. An example of using models is provided in `classify.py`.

### Tested Environment

- Python 3.9.16.
- Node.js v14.17.6.
- Operating System: Ubuntu 18.04.4 LTS 

## Usage

After setup and installation, run the following command:

```bash
./run.sh [URL]
```

## Output

The tool will output a table detailing:

- List of JS resources.
- Predicted label for each JS resource.
- Result based on the filter list.

## Contribution & Citing

If you utilize this tool in your research or work, please ensure you cite our conference paper. 

## Additional Notes

- This tool is a prototype and may undergo further refinements.
- For any issues, feedback, or questions, please contact the authors of the paper.