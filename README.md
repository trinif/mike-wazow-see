# mike-wazow-see

## Idea

Our project primarily aims to improve accessibility for colorblind and low vision individuals. We will accomplish this via techniques including contrast boosting, color swapping (specifically to target the most common forms of colorblindness, and, in later iterations, to accommodate less common conditions), and texture overlays on certain regions to improve visual differentiation. In later iterations, we'll focus on text and sign extraction and subsequent enlargement, and generating alt image descriptions. In terms of iterating on input formats, we will start with explicit maps and diagrams, then still images, and then perhaps video and live image feeds. Another possible extension is enabling users to select what type of vision they have, so we can better prioritize their needs.

## Planned Iterations
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
