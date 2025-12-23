# Mike Wazow-see :: Trini Feng, Rin Fukuoka, and Raven (Ruiwen) Tang

## Idea

Our project primarily aims to improve accessibility for colorblind and low vision individuals.

For this project, we have implemented a recoloring algorithm described in this research paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC8069325/. The recoloring algorithm aims to preserve the naturalness and contrast of the original image while also targeting certain colorblind conditions such as deuteranopia and protanopia. We have implemented all 4 modules of this algorithm, along with building visualizations and a frontend application interface that allows anyone to upload their own images and visualize the entire pipeline from start to finish of this algorithm.

You may additionally view our [demo slides](https://docs.google.com/presentation/d/1C5YwaGU5-nvOpAT-H2YtFaC06s2myP7fTpNEfzE6PEQ/edit?usp=sharing) and [demo video](https://drive.google.com/file/d/1RLyNNg66LSfCf7AUWUWiuM4ptX4tQIiE/view?usp=sharing).

## Project Structure

- `recoloring.ipynb`: Python notebook that contains our code for each module, along with visualizations and tests
- `recoloring.py`: Packaged Python file from `recoloring.ipynb` that allows for Python methods to be extracted into routes for the application
- `app.py`: Defined routes for the application, including routes for dichromat simulation and final output
- `test.ipynb`: Python notebook that contains our earliest iterations of basic color-swapping
- `output`: Folder that contains outputs of our first 2 iterations, RGB swapping and HSV swapping
- `images`: Contains dichromat simulations of our input images under deuteranopia and protanopia, as well as original source images and various visualizations of these source images as they travel through the pipeline. For the most interesting, finalized visual examples, you may peruse images/final_examples.
- `data`: Contains a CSV file of different wavelength points to compute confusion line equations (needed for Module 2)
- `app_data`: Contains input and output files that are processed through the application interface - that is, if a user uploads an image, their image will be uploaded to `app_data`, and the output will also be uploaded to `app_data`
- `app`: Contains files for building the application interface, made with React and Next.js
- `final_report.pdf`: A writeup covering our implementation, research, motivations, future work, member duties, and more relevant information in detail.

## Running the App

First start the backend Flask server that contains our Python routes for image recoloring. This can be done by calling `python app.py`. The server should run on localhost:5000.

Next start the React Next.js app, which calls routes from the backend:

```cd app
npm install
npm run dev
```

## Original Planned Iterations

Our first thoughts: we thought we could accomplish this via techniques including contrast boosting, color swapping (specifically to target the most common forms of colorblindness, and, in later iterations, to accommodate less common conditions), and texture overlays on certain regions to improve visual differentiation. In later iterations, we'd focus on text and sign extraction and subsequent enlargement, and generating alt image descriptions. We'd start with explicit maps and diagrams, then still images, and then perhaps video and live image feeds. This iteration process was later modified to more rigorously implement researched modules, as specified in the paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC8069325/.
