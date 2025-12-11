# Mike Wazow-see :: Trini Feng, Rin Fukuoka, and Raven (Ruiwen) Tang

## Idea

Our project primarily aims to improve accessibility for colorblind and low vision individuals.

For this project, we have implemented a recoloring algorithm described in this research paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC8069325/. The recoloring algorithm aims to preserve the naturalness and contrast of the original image while also targeting certain colorblind conditions such as deuteranopia and protanopia. We have implemented all 4 modules of this algorithm, along with building visualizations and a frontend application interface that allows anyone to upload their own images and visualize the entire pipeline from start to finish of this algorithm.

## Project Structure

- `recoloring.ipynb`: Python notebook that contains our code for each module, along with visualizations and tests
- `recoloring.py`: Packaged Python file from `recoloring.ipynb` that allows for Python methods to be extracted into routes for the application
- `app.py`: Defined routes for the application, including routes for dichromat simulation and final output
- `test.ipynb`: Python notebook that contains our earliest iterations of basic color-swapping
- `output`: Folder that contains outputs of our first 2 iterations, RGB swapping and HSV swapping
- `images`: Contains dichromat simulations of our input images under deuteranopia and protanopia, as well as original source images and various visualizations of these source images as they travel through the pipeline
- `data`: Contains a CSV file of different wavelength points to compute confusion line equations (needed for Module 2)
- `app_data`: Contains input and output files that are processed through the application interface - that is, if a user uploads an image, their image will be uploaded to `app_data`, and the output will also be uploaded to `app_data`
- `app`: Contains files for building the application interface, made with React and Next.js

## Running the App

First start the backend Flask server that contains our Python routes for image recoloring. This can be done by calling `python app.py`. The server should run on localhost:5000.

Next start the React Next.js app, which calls routes from the backend:

```cd app
npm install
npm run dev
```

## Original Planned Iterations

Our first thoughts: we thought we could accomplish this via techniques including contrast boosting, color swapping (specifically to target the most common forms of colorblindness, and, in later iterations, to accommodate less common conditions), and texture overlays on certain regions to improve visual differentiation. In later iterations, we'd focus on text and sign extraction and subsequent enlargement, and generating alt image descriptions. We'd start with explicit maps and diagrams, then still images, and then perhaps video and live image feeds.

- [X] Color swapping within RGB space on maps/diagrams, based on Aakash Agrawal's [Medium blog post](https://medium.com/data-science/color-swapping-techniques-in-image-processing-fe594b3ca31a)
- [X] Color swapping within HSV space on maps/diagrams to control for saturation and brightness, based on Aakash Agrawal's [Medium blog post](https://medium.com/data-science/color-swapping-techniques-in-image-processing-fe594b3ca31a)
- [ ] Use of color range binary masks on maps/diagrams to target specific color swaps, based on Aakash Agrawal's [Medium blog post](https://medium.com/data-science/color-swapping-techniques-in-image-processing-fe594b3ca31a)
- [ ] Expansion of color swapping functionality to real world photos
- [ ] Colorblind-friendly specific swapping techniques (prioritizing protanomaly, protanopia, deuteranomaly, and deueteranopia - conditions, which affect > 1% of pop, based around reds/greens) on maps/diagrams
- [ ] Colorblind-friendly specific swapping techniques (prioritizing protanomaly, protanopia, deuteranomaly, and deueteranopia - conditions, which affect > 1% of pop, based around reds/greens) on real world photos
- [ ] Implementation of contrast boosting methods on maps/diagrams
- [ ] Implementation of contrast boosting methods on real world photos
- [ ] Use of text identification techniques within maps/diagrams
- [ ] Text enlargement replacement within maps/diagrams
- [ ] Use of text identification techniques within real world photos
- [ ] Text enlargement replacement within real world photos
- [ ] Use of sign identification techniques within real world photos
- [ ] Sign enlargement within real world photos
- [ ] Texture overlay on targeted areas within maps/diagrams
- [ ] Texture overlay on targeted areas within real world photos
- [ ] Alt text generation for real world photos
- [ ] Accommodation of less common forms of colorblindness in maps/diagrams and real world photos
- [ ] Audio functionality to play out alt text
- [ ] Expansion of color swapping functionality to videos
- [ ] Colorblind-friendly specific swapping techniques on videos
- [ ] Implementation of contrast boosting methods on videos
- [ ] Use of text identification techniques within videos
- [ ] Text enlargement replacement within videos
- [ ] Use of sign identification techniques within videos
- [ ] Sign enlargement within real videos
- [ ] Texture overlay on targeted areas within videos
- [ ] Alt text generation for videos
- [ ] Expansion of color swapping functionality to live image feeds
- [ ] Colorblind-friendly specific swapping techniques on live image feeds
- [ ] Implementation of contrast boosting methods on live image feeds
- [ ] Use of text identification techniques within live image feeds
- [ ] Text enlargement replacement within live image feeds
- [ ] Use of sign identification techniques within live image feeds
- [ ] Sign enlargement within live image feeds
- [ ] Texture overlay on targeted areas within live image feeds
- [ ] Alt text generation for live image feeds
- [ ] User functionality to select their vision needs and customized outputs
- [ ] Accommodation of additional vision conditions (cataracts, glaucoma, low vision, sunlight on screen, night shift mode)
