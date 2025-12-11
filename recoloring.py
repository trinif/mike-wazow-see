from PIL import Image
import math
import numpy as np
import skfuzzy as fuzz
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import heapq
from scipy.optimize import differential_evolution
import colour

# # COLOR SPACE TRANSFORMATION FUNCTIONS

# %%
def convertRgbToXyz(rgb):
     M =  [0.41242371206635076, 0.21265606784927693, 0.019331987577444885,
	       0.3575793401363035, 0.715157818248362, 0.11919267420354762,
	       0.1804662232369621, 0.0721864539171564, 0.9504491124870351]
     
     R = rgb[0] / 255
     G = rgb[1] / 255
     B = rgb[2] / 255
     # if colorProfile is sRGB
     R = math.pow(((R + 0.055) / 1.055), 2.4) if R > 0.04045 else R / 12.92
     G = math.pow(((G + 0.055) / 1.055), 2.4) if G > 0.04045 else G / 12.92
     B = math.pow(((B + 0.055) / 1.055), 2.4) if B > 0.04045 else B / 12.92
     # gamma correction
     X = R * M[0] + G * M[3] + B * M[6]
     Y = R * M[1] + G * M[4] + B * M[7]
     Z = R * M[2] + G * M[5] + B * M[8]
     xyz = (X, Y, Z)
     return xyz

def convertXyzToXyy(o):
    n = o[0] + o[1] + o[2]
    if n == 0:
        # X y Y
        return (0, 0, o[1])
    # X y Y
    return (o[0] / n, o[1] / n, o[1])

# following rough pseudocode from https://www.easyrgb.com/en/math.php
def convertXyzToRgb(xyz):

    x = xyz[0]
    y = xyz[1]
    z = xyz[2]

    r = 3.2406 * x - 1.5372 * y - 0.4986 * z
    g = -0.9689 * x + 1.8758 * y + 0.0415 * z
    b = 0.0557 * x - 0.2040 * y + 1.0570 * z

    if r > 0.0031308:
        r = 1.055 * (r ** (1 / 2.4)) - 0.055
    else:
        r = 12.92 * r
    if g > 0.0031308:
        g = 1.055 * (g ** (1 / 2.4)) - 0.055
    else:
        g = 12.92 * g
    if b > 0.0031308:
        b = 1.055 * (b ** (1 / 2.4)) - 0.055
    else:
        b = 12.92 * b
    
    return (max(0, min(1, r)) * 255, max(0, min(1, g)) * 255, max(0, min(1, b)) * 255)

# following rough pseudocode from https://www.easyrgb.com/en/math.php
def convertXyyToXyz(o):
    x = o[0]
    y = o[1]
    Y = o[2]
    if y == 0:
        return (0, 0, 0)
    X = (x * Y) / y
    Z = ((1 - x - y) * Y) / y
    return (X, Y, Z)

# translate from rgb to l, alpha, beta color space
# https://kaizoudou.com/from-rgb-to-lab-color-space/
# http://www.brucelindbloom.com/index.html?Math.html
def convertXyzToLab(xyz, Xr = 0.95047, Yr = 1.0, Zr =1.08883):
    epsilon = 0.008856
    kappa = 903.3

    X, Y, Z = xyz
    xr = X / Xr
    yr = Y / Yr
    zr = Z / Zr

    def f(t):
        return np.cbrt(t) if t > epsilon else (kappa * t + 16) / 116
    
    fx = f(xr)
    fy = f(yr)
    fz = f(zr)

    L = 116 * fy - 16
    a = 500 * (fx - fy)
    b = 200 * (fy - fz)
    return (L, a, b)

def convertLabToXyz(lab, Xr = 0.95047, Yr = 1.0, Zr =1.08883):
    epsilon = 0.008856
    kappa = 903.3

    L, a, b = lab

    fy = (L + 16) / 116
    fx = a / 500 + fy
    fz = fy - b / 200

    xr = fx**3 if fx**3 > epsilon else (116 * fx - 16) / kappa
    yr = ((L + 16)/116)**3 if L > kappa * epsilon else L / kappa
    zr = fz**3 if fz**3 > epsilon else (116 * fz - 16) / kappa
    X = xr * Xr
    Y = yr * Yr
    Z = zr * Zr
    return (X, Y, Z)

def convertRgbToLab(color_rgb):
    xyz = convertRgbToXyz(color_rgb)
    lab = convertXyzToLab(xyz)
    return lab

def convertLabToRgb(color_lab):
    xyz = convertLabToXyz(color_lab)
    rgb = convertXyzToRgb(xyz)
    return rgb

# DICHROMAT SIMULATION

# find dichromat simulation of the color (using translated JavaScript code from https://github.com/skratchdot/color-blind)
# takes in rgb code as a three element tuple, returns rgb code of the color a dichromat sees (as a three element tuple)

class blinder:
    def __init__(self, x, y, m, y1):
        self.x = x
        self.y = y
        self.m = m
        self.yi = y1

protan = blinder(0.7465, 0.2535, 1.273463, -0.073894)
deutan = blinder(1.4, -0.4, 0.968437, 0.003331)

def dichromat_simul(rgb, blinder_param, anomalize=False): # toggle anomalize to get protanomaly instead of protanopia or deuteranomaly instead of deuteranopia
# exports.Blind = function (rgb, type, anomalize) {
	# z, v, n,
	#line, c, slope,
	# yi, dx, dy,
	#dX, dY, dZ,
	#dR, dG, dB,
	#_r, _g, _b,
	#ngx, ngz, M,
	#adjust
	
	# if (type === "achroma") { // D65 in sRGB
	# 	z = rgb.R * 0.212656 + rgb.G * 0.715158 + rgb.B * 0.072186;
	# 	z = {R: z, G: z, B: z};
	# 	if (anomalize) {
	# 		v = 1.75;
	# 		n = v + 1;
	# 		z.R = (v * z.R + rgb.R) / n;
	# 		z.G = (v * z.G + rgb.G) / n;
	# 		z.B = (v * z.B + rgb.B) / n;
	# 	}
	# 	return z;
	# }
	
    line = blinder_param # protan or deutan
    
    # c = Xyy
    Xyy = convertXyzToXyy(convertRgbToXyz(rgb))

	# The confusion line is between the source color and the confusion point
    slope = (Xyy[1] - line.y) / (Xyy[0] - line.x)
    yi = Xyy[1] - Xyy[0] * slope; # slope, and y-intercept (at x=0)
    # Find the change in the x and y dimensions (no Y change)
    dx = (line.yi - yi) / (slope - line.m)
    dy = (slope * dx) + yi
    dY = 0
	# Find the simulated colors XYZ coords
    colorX = dx * Xyy[1] / dy
    colorY = Xyy[1]
    colorZ = (1 - (dx + dy)) * Xyy[1] / dy
    z = (colorX, colorY, colorZ) 

    
	# Calculate difference between sim color and neutral color
    ngx = 0.312713 * Xyy[1] / 0.329016 # find neutral grey using D65 white-point
    ngz = 0.358271 * Xyy[1] / 0.329016
    dX = ngx - z[0]
    dZ = ngz - z[2]
	# find out how much to shift sim color toward neutral to fit in RGB space
    M = [
	3.240712470389558, -0.969259258688888, 0.05563600315398933,
	-1.5372626602963142, 1.875996969313966, -0.2039948802843549,
	-0.49857440415943116, 0.041556132211625726, 1.0570636917433989]

    dR = dX * M[0] + dY * M[3] + dZ * M[6] # convert d to linear RGB
    dG = dX * M[1] + dY * M[4] + dZ * M[7]
    dB = dX * M[2] + dY * M[5] + dZ * M[8]

    if dR == 0:
        dR = 0.00000000000000000000000001
    if dG == 0:
        dG = 0.00000000000000000000000001
    if dB == 0:
        dB = 0.00000000000000000000000001    

    R = z[0] * M[0] + z[1] * M[3] + z[2] * M[6] # convert z to linear RGB
    G = z[0] * M[1] + z[1] * M[4] + z[2] * M[7]
    B = z[0] * M[2] + z[1] * M[5] + z[2] * M[8]

    _r = ((0 if R < 0 else 1) - R) / dR
    _g = ((0 if G < 0 else 1) - G) / dG
    _b = ((0 if B < 0 else 1) - B) / dB
    _r = 0 if (_r > 1 or _r < 0) else _r
    _g = 0 if (_g > 1 or _g < 0) else _g
    _b = 0 if (_b > 1 or _b < 0) else _b

    adjust = _r if _r > _g else _g
    if (_b > adjust):
        adjust = _b
          
	# shift proportionally...
    R += adjust * dR
    G += adjust * dG
    B += adjust * dB
	# apply gamma and clamp simulated color...
    gammaCorrection = 2.2
    R = 255 * (
    0 if R <= 0 else 
    (1 if R >= 1 else 
    math.pow(R, 1 / gammaCorrection)))

    B = 255 * (
    0 if B <= 0 else 
    (1 if B >= 1 else 
    math.pow(B, 1 / gammaCorrection)))

    G = 255 * (
    0 if G <= 0 else 
    (1 if G >= 1 else 
    math.pow(G, 1 / gammaCorrection)))
	
    if (anomalize):
        v = 1.75
        n = v + 1
        R = (v * R + rgb[0]) / n
        G = (v * G + rgb[1]) / n
        B = (v * B + rgb[2]) / n
	
    rgb = (R, G, B)
    return rgb

# KEY COLOR EXTRACTION
# ## Note: All operations completed in RGB color space

# Module 1: Key Color Extraction (all operations completed in RGB color space)

# break image up into grouped color bins
# find representative colors (mean of all colors) of each bin
# find pixel count of each bin
# takes in image path as a string and cube_slength, returns list of representative colors and mapping from each representative color to the pixel count of the bin it represents
# cube_slength recommended interval: [5, 10]
def rep_colors(img_path, cube_slength):

    # set up color bins
    num_chan_bins = math.ceil(255 / cube_slength)
    # maps from lower bound (3-element tuple) of cube
    # to a list of colors 
    bins_to_colors = dict()

    # maps each rep-color (3- element tuple) to all pixel (rgb + xy)
    rep_color_to_pixels = dict()

    try:
        # open image within RGB color space
        with Image.open(img_path) as img:
            img = img.convert('RGB')
            width, height = img.size

            # for each pixel
            for y in range(height):
                for x in range(width):
                    rgb_val = img.getpixel((x, y))
                    low_r_bound = int(rgb_val[0] / num_chan_bins)
                    low_g_bound = int(rgb_val[1] / num_chan_bins)
                    low_b_bound = int(rgb_val[2] / num_chan_bins)
                    if (low_r_bound, low_g_bound, low_b_bound) in bins_to_colors:
                        bins_to_colors[(low_r_bound, low_g_bound, low_b_bound)].append((rgb_val, (x, y)))
                    else:
                        bins_to_colors[(low_r_bound, low_g_bound, low_b_bound)] = [(rgb_val, (x, y))]

            rep_colors = []
            rep_c_to_px_count = dict()

            # iterate through bins, find rep color of each one
            # and populate representative-color-to-pixel-count dictionary
            for bin in bins_to_colors:
                color_list = bins_to_colors[bin]
                avg_red = 0
                avg_green = 0
                avg_blue = 0
                # for c in color_list:
                for (c, xy) in color_list:
                    avg_red += c[0] / len(color_list)
                    avg_green += c[1] / len(color_list)
                    avg_blue += c[2] / len(color_list)
                # avg_red = int(avg_red)
                # avg_green = int(avg_green)
                # avg_blue = int(avg_blue)
                if avg_red > 255:
                    avg_red = 255
                if avg_green > 255:
                    avg_green = 255
                if avg_blue > 255:
                    avg_blue = 255
                rep_colors.append((avg_red, avg_green, avg_blue))
                rep_c_to_px_count[(avg_red, avg_green, avg_blue)] = len(color_list)
                rep_color_to_pixels[(avg_red, avg_green, avg_blue)] = color_list

            return rep_colors, rep_c_to_px_count, rep_color_to_pixels

    except FileNotFoundError:
        print("Image file not found at " + img_path)
    except Exception as e:
        print(f"An error occurred: {e}")

# find distance between representative color and dichromat simulation - if the distance is greater than some delta (20-30), they are confusing
# separate colors of the image into 2 sets: Ca (confusing) and Cb (non confusing)
# takes in two lists (representative colors and dichromat colors), where corresponding ones are at the same respective indices
# also takes in a float delta, which represents the maximum distance where two colors may be confused
# returns set of confusing colors and set of non-confusing colors
# delta recommended interval: [20, 30]
def sep_confusing(rep_color_list, dichromat_color_list, delta):
    # sets
    confusing_colors = set()
    non_confusing_colors = set()
    # loop over colors
    for rep_color, dichromat_color in zip(rep_color_list, dichromat_color_list):
        # get distance
        distance = 0
        for i in range(3):
            # squared difference of each RGB channel
            distance += (rep_color[i] - dichromat_color[i]) ** 2
        
        if math.sqrt(distance) < delta:
            non_confusing_colors.add(rep_color)
        else:
            confusing_colors.add(rep_color)
    
    return confusing_colors, non_confusing_colors

# run fuzzy clustering on both sets to get key colors
# takes in a set of colors and number of clusters n
# returns set of n key colors from the given set, and dictionary mapping from cluster centers to cluster members
def fuzzy_clustering(color_set, n):
    # fuzzy expects (features, samples) so transpose the set of colors
    color_list = list(color_set)
    data = np.array(color_list).T
    # m = 1.7
    m = 1.5
    error = 1e-5
    maxiter = 2000
    centers, partitioned_matrix, _, _, _, _, _ = fuzz.cluster.cmeans(
        data, c=n, m=m, error=error, maxiter=maxiter, init=None
    )
    centers.tolist()

    # return cluster centers
    cluster_set = set()
    for c in centers:
        cluster_set.add((float(c[0]), float(c[1]), float(c[2])))

    # map from cluster centers to cluster members
    centers_to_members = dict()
    cluster_assignments = np.argmax(partitioned_matrix, axis=0)
    for i in range(len(color_list)):
        if tuple(centers[cluster_assignments[i]].tolist()) in centers_to_members:
            centers_to_members[tuple(centers[cluster_assignments[i]].tolist())].append(color_list[i])
        else:
            centers_to_members[tuple(centers[cluster_assignments[i]].tolist())] = [color_list[i]]

    return set(centers_to_members.keys()), centers_to_members

# takes in dictionary mapping from representative colors to bin pixel counts
# and dictionary mapping from cluster centers to cluster members
# returns dictionary mapping from cluster centers to cardinalities
def compute_cluster_cardinalities(rep_c_to_px_count, centers_to_members):
    center_cardinalities = dict()
    for center in centers_to_members:
        # sum bin pixel counts of representative colors in the cluster
        cardinality = 0
        for member in centers_to_members[center]:
            cardinality += rep_c_to_px_count[member]
        if cardinality > 0:
            center_cardinalities[center] = cardinality
        else:
            centers_to_members.pop(center)
    return center_cardinalities, set(centers_to_members.keys())

def create_cluster_to_pixel_mapping(rep_colors_to_pixel, cluster_c_to_rep_col):
    cluster_to_pixel = dict()
    
    for cluster_center, rep_color_list in cluster_c_to_rep_col.items():
        pixel_list = []
        for rep_col in rep_color_list:
            if rep_col in rep_colors_to_pixel:
                pixel_list.extend(rep_colors_to_pixel[rep_col])
            else:
                print(f"Warning {rep_col} not found")

        cluster_to_pixel[cluster_center] = pixel_list
    return cluster_to_pixel

# put it all together for module 1 !!!!
# takes in image file path as string, cube side length for color binning, delta, blindness_param (deutan or protan), m = number of key confusing colors we want, and n = number of key nonconfusing colors we want
# returns set of key confusing colors, set of key nonconfusing colors, dictionary of confusing cardinalities (each confusing key color mapped to its cardinality), and dictionary of nonconfusing cardinalities (each nonconfusing key color mapped to its cardinality)
def module_1(img_path, cube_slength, delta, blindness_param, m, n):
    rep_color_list, rep_c_to_px_count, rep_colors_to_pixel = rep_colors(img_path, cube_slength)
    dichromat_color_list = [dichromat_simul(c, blindness_param) for c in rep_color_list] # can switch between protan and deutan argument
    confusing_color_set, nonconfusing_color_set = sep_confusing(rep_color_list, dichromat_color_list, delta)
    # print(confusing_color_set)
    # print(nonconfusing_color_set)
    key_c_colors, confusing_clusters = fuzzy_clustering(confusing_color_set, m)
    key_nc_colors, nonconfusing_clusters = fuzzy_clustering(nonconfusing_color_set, n)
    conf_cardinalities, key_c_colors = compute_cluster_cardinalities(rep_c_to_px_count, confusing_clusters)
    nonconf_cardinalities, key_nc_colors = compute_cluster_cardinalities(rep_c_to_px_count, nonconfusing_clusters)
    cluster_to_pixel = create_cluster_to_pixel_mapping(rep_colors_to_pixel, confusing_clusters)
    return key_c_colors, key_nc_colors, conf_cardinalities, nonconf_cardinalities, cluster_to_pixel, confusing_clusters, nonconfusing_clusters

# KEY COLOR TRANSLATION

# inputs
# key_c_colors: set of key confusing colors
# key_nc_colors: set of key non-confusing colors
# key_c_colors_cardinality_dict
# key_nc_colors_cardinality_dict

# outputs
# key_c_colors_xy_dict
# key_nc_colors_xy_dict
# confusing_colors_heap
# non_confusing_colors_heap

# map sets of key colors from rgb -> xyz -> xyY -> projected xy-plane to get chromaticity diagram
# x -> hue, y -> colorfulness, Y -> relative luminance
# equations (5) - (10) in the paper
# dictionary mapping each rgb key color to its value in xy plane
def rgb_to_xy(color_rgb):
    xyz = convertRgbToXyz(color_rgb)
    xyY = convertXyzToXyy(xyz)
    return (xyY[0], xyY[1])

# Make a priority queue, using the Python heapq,
# keyed on the decreasing order of cardinalities (so each element in the queue is a 2 value tuple,
# where the first value is the negative value of the cardinality and the second value is the RGB cluster center color)
def make_priority_queue(key_color_set, cardinality_dict):
    heap = []
    for key_color in key_color_set:
        cardinality = cardinality_dict[key_color]
        heapq.heappush(heap, (-cardinality, key_color))
    return heap

# confusion lines are formed by a copunctal and a spectrum locus point at a specific wavelength
# spectrum loci points are obtained from a csv from CIE
# csv format: lambda wavelength, x, y, z - only care about x and y

# returns list of xy coordinate tuples, hardcoded from fixed wavelengths
def confusion_lines(copunctal):
    spec_loci = pd.read_csv('data/CIE_1931_spectrum_loci.csv')

    # x and y are columns 1 and 2 respectively

    selected_lines = []

    # pull from fixed wavelengths, given by the graph in the research paper
    # protan
    if copunctal == (0.747, 0.253):
        wavelengths = [390, 405, 420, 445, 470, 474, 478, 481, 485, 487, 490, 493, 495, 497, 500, 504, 508, 529, 550]
    # deutan
    else:
        wavelengths = [390, 450, 480, 485, 488, 490, 495, 498, 500, 503, 507, 512, 520, 528, 700]

    for wavelength in wavelengths:
        row = spec_loci.loc[spec_loci.iloc[:, 0] == wavelength].iloc[0]

        # get x and y values, extracted from numpy values
        result = (row.iloc[1].item(), row.iloc[2].item())
        selected_lines.append(result)

    return selected_lines

# takes in xy coordinates of copunctal, color, and locus
# returns distance from color to the line that passes through copunctal and locus
def dist(copunctal, color, spec_locus):
    # distance is defined in the paper
    (cp_x, cp_y) = copunctal
    (c_x, c_y) = color
    (x0, y0) = spec_locus

    return abs((cp_x - x0) * (y0 - c_y) - (x0 - c_x) * (cp_y - y0)) / math.sqrt((cp_x - x0) ** 2 + (cp_y - y0) ** 2)

# takes in xy coordinate of color, the list of all confusion lines, and the copunctal
# returns xy coordinate of the spectrum locus point representing the closest confusion line to the color
def closest_confusion_line(color, confusion_lines, copunctal):
    # confusion line is the spectrum locus point
    # init variables to store closest line and closest distance
    closest_line = confusion_lines[0]
    closest_distance = dist(copunctal, color, confusion_lines[0])
    # iterate through confusion lines and update closest line and distance as needed
    for confusion_line in confusion_lines:
        distan = dist(copunctal, color, confusion_line)
        if distan < closest_distance:
            closest_line = confusion_line
            closest_distance = distan
    
    return closest_line

# take in confusing key colors and non-confusing key colors
# and returns a confusion line map which is a tuple of
# list of confusing colors on the line and 
# line of nonconfusing colors on the line
# all in xy space
def map_colors_to_confusion_lines(confusing_key_colors, nonconfusing_key_colors, confusion_lines, copunctal):
    confusion_lines_map = {}
    
    # mapping is confusion lines to a tuple of confusing key colors list and nonconfusing key colors list
    for confusing in confusing_key_colors:
        closest_line = closest_confusion_line(confusing, confusion_lines, copunctal)
        if closest_line not in confusion_lines_map:
            confusion_lines_map[closest_line] = ([], [])
        
        confusion_lines_map[closest_line][0].append(confusing)

    for nonconfusing in nonconfusing_key_colors:
        closest_line = closest_confusion_line(nonconfusing, confusion_lines, copunctal)
        if closest_line not in confusion_lines_map:
            confusion_lines_map[closest_line] = ([], [])
        
        confusion_lines_map[closest_line][1].append(nonconfusing)
    
    return confusion_lines_map

# iterate through map, create list of colors that need to be translated
# take in confusion line to confusing and non-confusing colors map, heaps for confusing and non-confusing colors
# all in xy space
# returns list of colors that need to be translated
def prep_colors_for_translation(confusion_map, c_colors_heap_xy):
    colors_to_translate = []


    for confusion_line in confusion_map:
        (confusing, non_confusing) = confusion_map[confusion_line]

        confusing = set(confusing)
        # at least 2 confusing colors and no non-confusing colors
        if len(confusing) >= 2 and len(non_confusing) == 0:
            # keep color with lowest rank on confusion line
            # translate the others
            found_lowest_rank = False
            for i in range(len(c_colors_heap_xy)):
                if c_colors_heap_xy[i][1] in confusing and not found_lowest_rank:
                    found_lowest_rank = True
                elif c_colors_heap_xy[i][1] in confusing and found_lowest_rank:
                    colors_to_translate.append(c_colors_heap_xy[i][1])
        
        # at least one non-confusing color and some number of confusing colors
        if len(non_confusing) >= 1 and len(confusing) > 0:
            # translate all colors
            colors_to_translate.extend(confusing)
    
    return colors_to_translate

# takes in confusing and non-confusing key colors in xy space, number of confusing lines, and copuntal point for either blindness type
# returns list of colors in xy space that needs to be translated
def map_confusion_lines(confusing_key_colors, nonconfusing_key_colors, c_colors_heap_xy, copunctal_type):

    # Get confusion lines
    cf = confusion_lines(copunctal_type)

    # map confusion lines to lists of confusing key colors and non-confusing key colors
    # can change to protan_copunctal in args
    confusion_lines_to_colors_map = map_colors_to_confusion_lines(confusing_key_colors, nonconfusing_key_colors, cf, copunctal_type)

    # create set of confusing lines that are unoccupied
    non_occupied_confusion_lines = set(cf) - set(confusion_lines_to_colors_map.keys())

    # check which colors need to be translated
    colors_to_translate = prep_colors_for_translation(confusion_lines_to_colors_map, c_colors_heap_xy)

    return colors_to_translate, non_occupied_confusion_lines

# y coordinate of the spectrum locus point
def project_onto_line(curr_color_point, closest_line_point, copunctal_point):
    (cp_x, cp_y) = copunctal_point
    (cl_x, cl_y) = closest_line_point
    (cc_x, cc_y) = curr_color_point

    # slope of the confusion line
    m = (cl_y - cp_y) / (cl_x - cp_x)
    # y-intercept of the confusion line
    b = cp_y - m * cp_x

    # perpendicular slope & perpendicular y-intercept
    m_perp = -1 / m
    b_perp = cc_y - m_perp * cc_x

    # x coordinate of the projection point (using 2 equations)
    x_proj = (b_perp - b) / (m - m_perp)
    # y coordinate of the projection point
    y_proj = m * x_proj + b

    return (x_proj, y_proj)

# takes set of colors to translate, the heap of confusing colors in xy space, list of confusion lines not occupied yet, and copunctual point and
# return a dictionary mapping colors in original location to mapped location in xy space
def translate_colors(colors_to_translate, c_colors_heap_xy, non_occupied_confusion_lines, copunctal):
    color_translation_map = dict()

    colors_to_translate_copy = colors_to_translate[:]
    
    # iterate on each color in the order of cardinality
    for i in range(len(c_colors_heap_xy)):
        if c_colors_heap_xy[i][1] in colors_to_translate_copy:
            color = c_colors_heap_xy[i][1]
            # find closest non-occupied confusion line
            closest_line_point = closest_confusion_line(color, list(non_occupied_confusion_lines), copunctal)
 
            # project color point onto this line
            new_color_point = project_onto_line(color, closest_line_point, copunctal)
            color_translation_map[color] = new_color_point
            
            # delete line from non-occupied set
            non_occupied_confusion_lines.remove(closest_line_point)
            # delete color from colors to translate set
            colors_to_translate_copy.remove(color)
    
    return color_translation_map

# takes in RGB tuples (key colors, key nonconf colors) and dicts mapping from key colors (as RGB) to their cardinalities, confusing and non-confusing
# as well as the number of confusion lines we want, and copunctal coordinates
def module_2(key_c_colors, key_nc_colors, key_c_colors_cardinality_dict, key_nc_colors_cardinality_dict, copunctal):
    # use case
    key_c_colors_xy_dict = dict()
    key_nc_colors_xy_dict = dict()
    key_c_colors_xy_xyy_dict = dict()
    key_nc_colors_xy_xyy_dict = dict()
    for c in key_c_colors:
        key_c_colors_xy_dict[c] = rgb_to_xy(c)
        key_c_colors_xy_xyy_dict[rgb_to_xy(c)] =  convertXyzToXyy(convertRgbToXyz(c))
    for c in key_nc_colors:
        key_nc_colors_xy_dict[c] = rgb_to_xy(c)
        key_nc_colors_xy_xyy_dict[rgb_to_xy(c)] =  convertXyzToXyy(convertRgbToXyz(c))
    # heap of rgb key colors
    confusing_colors_heap = make_priority_queue(key_c_colors, key_c_colors_cardinality_dict)
    non_confusing_colors_heap = make_priority_queue(key_nc_colors, key_nc_colors_cardinality_dict)
    
    # need to cast to xy from RGB
    key_c_colors_xy = set()
    for c in key_c_colors:
        key_c_colors_xy.add(rgb_to_xy(c))
    key_nc_colors_xy = set()
    for c in key_nc_colors:
        key_nc_colors_xy.add(rgb_to_xy(c))

    # cast key colors heap to RGB
    c_colors_heap_xy = []
    for i in range(len(confusing_colors_heap)):
        heapq.heappush(c_colors_heap_xy, (confusing_colors_heap[i][0], rgb_to_xy(confusing_colors_heap[i][1])))
        # heapq.heappush(confusing_colors_heap, (c_colors_heap_xy[i][0], rgb_to_xy(c_colors_heap_xy[i][1])))
    
    colors_to_translate, non_occupied_confusion_lines = map_confusion_lines(key_c_colors_xy, key_nc_colors_xy, c_colors_heap_xy, copunctal)
 
    # translate colors
    color_translation_map = translate_colors(colors_to_translate, c_colors_heap_xy, non_occupied_confusion_lines, copunctal)

    return confusing_colors_heap, non_confusing_colors_heap, key_c_colors_xy_dict, key_nc_colors_xy_dict, key_c_colors_xy_xyy_dict, key_nc_colors_xy_xyy_dict, colors_to_translate, color_translation_map

# same inputs as module_1() method, as well as num confusion lines
# links module 1 to module 2
def modules_1_and_2(img_path, cube_slength, delta, blindness_param, m, n):
    copunctal = (0.747, 0.253)
    if blindness_param == deutan:
        copunctal = (1.08, -0.8)
    key_c_colors, key_nc_colors, conf_cardinalities, nonconf_cardinalities, _, _, _ = module_1(img_path, cube_slength, delta, blindness_param, m, n)
    conf_heap, nonconf_heap, key_c_xy_dict, key_nc_xy_dict, key_c_xyy_dict, key_nc_xyy_dict, colors_to_translate, color_translation_map = module_2(key_c_colors, key_nc_colors, conf_cardinalities, nonconf_cardinalities, copunctal)

# # KEY COLOR OPTIMIZATION

# find error function based on difference between confusing and nonconfusing colors
def compute_e1(luminances, key_c_rgb_colors_list, key_c_xy_colors_list, rec_key_c_xy_colors_list, key_nc_colors, blindness_param):
    e1 = 0
    for i in range(len(key_c_xy_colors_list)):
        for nconf_color in key_nc_colors:
            conf_rgb_color = key_c_rgb_colors_list[i]
            conf_xy_color = key_c_xy_colors_list[i]
            rec_conf_color = rec_key_c_xy_colors_list[i]
            luminance = luminances[i]
            # original distance between RGBs of confusing color and non-confusing color
            orig_dist = math.sqrt((conf_rgb_color[0] - nconf_color[0]) ** 2 + (conf_rgb_color[1] - nconf_color[1]) ** 2 + (conf_rgb_color[2] - nconf_color[2]) ** 2)
            # dichromat distance between simulated RGBs of RECOLORED confusing color and nonconfusing color
            rec_c_color_rgb = convertXyzToRgb(convertXyyToXyz((rec_conf_color[0], rec_conf_color[1], luminance)))
            sim_rec_c_color = dichromat_simul(rec_c_color_rgb, blindness_param)
            sim_nc_color = dichromat_simul(nconf_color, blindness_param)
            sim_rec_dist = math.sqrt((sim_rec_c_color[0] - sim_nc_color[0]) ** 2 + (sim_rec_c_color[1] - sim_nc_color[1]) ** 2 + (sim_rec_c_color[2] - sim_nc_color[2]) ** 2)

            e1 += abs(orig_dist - sim_rec_dist) / (len(key_c_xy_colors_list) * len(key_nc_colors))
    return e1

# find error function based on difference between pairs of confusing colors
def compute_e2(luminances, key_c_rgb_colors_list, key_c_xy_colors_list, rec_key_c_xy_colors_list, blindness_param):
    e2 = 0
    for i in range(len(key_c_xy_colors_list)):
        for j in range(len(key_c_xy_colors_list)):
            # original distance between RGBs of 2 confusing colors
            orig_dist = math.sqrt((key_c_rgb_colors_list[i][0] - key_c_rgb_colors_list[j][0]) ** 2 + (key_c_rgb_colors_list[i][1] - key_c_rgb_colors_list[j][1]) ** 2 + (key_c_rgb_colors_list[i][2] - key_c_rgb_colors_list[j][2]) ** 2)
            # dichromat distance between simulated RGBs of RECOLORED confusing color and nonconfusing color
            rec_i_color_rgb = convertXyzToRgb(convertXyyToXyz((rec_key_c_xy_colors_list[i][0], rec_key_c_xy_colors_list[i][1], luminances[i])))
            sim_rec_i_color = dichromat_simul(rec_i_color_rgb, blindness_param)
            rec_j_color_rgb = convertXyzToRgb(convertXyyToXyz((rec_key_c_xy_colors_list[j][0], rec_key_c_xy_colors_list[j][1], luminances[j])))
            sim_rec_j_color = dichromat_simul(rec_j_color_rgb, blindness_param)
            sim_rec_dist = math.sqrt((sim_rec_i_color[0] - sim_rec_j_color[0]) ** 2 + (sim_rec_i_color[1] - sim_rec_j_color[1]) ** 2 + (sim_rec_i_color[2] - sim_rec_j_color[2]) ** 2)

            e2 += abs(orig_dist - sim_rec_dist) / (len(key_c_xy_colors_list) ** 2)
    return e2

def compute_e3(luminances, key_c_rgb_colors_list, rec_key_c_xy_colors_list):
    e3 = 0
    for i in range(len(key_c_rgb_colors_list)):
        orig_color_rgb = key_c_rgb_colors_list[i]
        rec_color_rgb = convertXyzToRgb(convertXyyToXyz((rec_key_c_xy_colors_list[i][0], rec_key_c_xy_colors_list[i][1], luminances[i])))
        e3 += math.sqrt((orig_color_rgb[0] - rec_color_rgb[0]) ** 2 + (orig_color_rgb[1] - rec_color_rgb[1]) ** 2 + (orig_color_rgb[2] - rec_color_rgb[2]) ** 2) / len(key_c_rgb_colors_list)
    return e3

def objective_function(x, key_c_rgb_colors_list, key_c_xy_colors_list, rec_key_c_xy_colors_list, key_nc_colors, blindness_param, lam=0.2):
    luminances = x.tolist()
    e1 = compute_e1(luminances, key_c_rgb_colors_list, key_c_xy_colors_list, rec_key_c_xy_colors_list, key_nc_colors, blindness_param)
    e2 = compute_e2(luminances, key_c_rgb_colors_list, key_c_xy_colors_list, rec_key_c_xy_colors_list, blindness_param)
    e3 = compute_e3(luminances, key_c_rgb_colors_list, rec_key_c_xy_colors_list)
    return e1 + e2 + lam * e3

def module_3(key_c_xy_dict, key_c_xyy_dict, color_translation_map, key_nc_colors, blindness_param, lam=0.2):
    # list of key confusing rgb colors in order
    key_c_rgb_colors_list = []
    # list of key confusing xy colors in order
    key_c_xy_colors_list = []
    # list of original luminances for key confusing colors in order
    luminances = []
    # list of recolored key confusing colors (xy) in order
    rec_key_c_xy_colors_list = []
    for c in key_c_xy_dict:
        key_c_rgb_colors_list.append(c)
        key_c_xy_colors_list.append(key_c_xy_dict[c])
        luminances.append(key_c_xyy_dict[key_c_xy_dict[c]][2])
        if key_c_xy_dict[c] in color_translation_map:
            rec_key_c_xy_colors_list.append(color_translation_map[key_c_xy_dict[c]])
        else:
            rec_key_c_xy_colors_list.append(key_c_xy_dict[c])
    init_luminances = np.array(luminances)
    additional_args = (key_c_rgb_colors_list, key_c_xy_colors_list, rec_key_c_xy_colors_list, key_nc_colors, blindness_param, lam)
    result = differential_evolution(
        func=objective_function,
        bounds=[(0, 100) for _ in range(len(init_luminances))],
        args=additional_args,
        maxiter=100,
        popsize=20,
        mutation=0.8,
        recombination=0.6
    )
    optimized_luminances = result.x.tolist()
    print(optimized_luminances)
    orig_rgb_to_rec_rgb_dict = dict()
    for i in range(len(key_c_rgb_colors_list)):
        orig_rgb = key_c_rgb_colors_list[i]
        rec_xy = rec_key_c_xy_colors_list[i]
        rec_rgb = convertXyzToRgb(convertXyyToXyz((rec_xy[0], rec_xy[1], optimized_luminances[i])))
        orig_rgb_to_rec_rgb_dict[orig_rgb] = rec_rgb
    return orig_rgb_to_rec_rgb_dict

# # CLUSTER TO CLUSTER COLOR TRANSLATION

def find_close_key(d, target, eps=1e-3):
    tx, ty, tz = target
    for k in d.keys():
        x, y, z = k
        if abs(x - tx) < eps and abs(y - ty) < eps and abs(z - tz) < eps:
            return k
    print(f"not found: {target}")
    return None

# take in orig_to_recolored_key_colors_map, which stores the mapping from orig cluster center -> recolored cluster centers
# and cluster_to_pixels_map, a mapping from orig cluster center -> all pixels in that cluster (both rgb color and its pixel location xy)
# and the image path
# performs cluster_to_cluster_transfer_color on pixels that needs to be translated and outputs the resulting image
def module_4(orig_to_recolored_key_colors_map, cluster_to_pixels_map, img_path):

    img = Image.open(img_path)
    img = img.convert("RGB")


    for key_color in orig_to_recolored_key_colors_map:
        # centroid of original cluster
        orig_centroid = key_color
        orig_centroid_lab = convertRgbToLab(orig_centroid)

        # centroid of recolored cluster 
        recolored_centroid = orig_to_recolored_key_colors_map[key_color] 
        recolored_centroid_lab = convertRgbToLab(recolored_centroid)


        cluster_key = find_close_key(cluster_to_pixels_map, key_color, 0.01)
        for orig_pixel in cluster_to_pixels_map[cluster_key]:
        #for orig_pixel in cluster_to_pixels_map[key_color]:
            rgb, xy = orig_pixel
            # rgb -> lab
            orig_pixel_lab = convertRgbToLab(rgb)
            # recolor
            # recolored_pixel_lab = orig_pixel_lab - orig_centroid_lab + recolored_centroid_lab
            recolored_pixel_lab = (
                orig_pixel_lab[0] - orig_centroid_lab[0] + recolored_centroid_lab[0],
                orig_pixel_lab[1] - orig_centroid_lab[1] + recolored_centroid_lab[1],
                orig_pixel_lab[2] - orig_centroid_lab[2] + recolored_centroid_lab[2],
                )
            
            # lab -> rgb
            recolored_pixel_rgb = convertLabToRgb(recolored_pixel_lab)
            
            # set pixel in image to recolored_pixel_rgb
            r, g, b = recolored_pixel_rgb
            rgb = int(round(r)), int(round(g)), int(round(b)) 
            img.putpixel(xy, rgb)
    return img

# # VISUALIZATION

img_paths = ["images/original/crystal_lake_il_map.jpeg", "images/original/foliage.jpg", "images/original/nyc_map.jpg",
             "images/original/penn_map.png"]

# PARAMETERS TO USE
cube_slength = 5
delta = 25
n = 9
m = 9
lam = 0.2

# tag is in form of file name ("_dichromat_simul")
def get_output_path(input_path, tag):
    img_period_idx = input_path.index(".")
    output_img_path = input_path[:img_period_idx] + tag + input_path[img_period_idx:]
    return output_img_path

def blindness_str(blindness_param):
    if blindness_param == deutan:
        return "deutan"
    else:
        return "protan"

def visualize_process(image_path, blindness_param):
    def dichromat_simul_img(img_path, blindness_param):
        try:
            img = Image.open(img_path)
            width, height = img.size
            for y in range(height):
                for x in range(width):
                    original_rgb = img.getpixel((x, y))
                    new_pixel = dichromat_simul(original_rgb, blindness_param)
                    img.putpixel((x, y), (int(new_pixel[0]), int(new_pixel[1]), int(new_pixel[2])))
            
            img.show()
            blindness = blindness_str(blindness_param)
            output_img_path = get_output_path(img_path, "_dichromat_simul_" + blindness)
            img.save(output_img_path)
        except FileNotFoundError:
            print("Image file not found at " + img_path)
        except Exception as e:
            print("An error occurred: " + e)

    def rep_color_visualization(image_path):
        rep_color_list, _, _ = rep_colors(image_path, cube_slength)
        norm_c_colors = [(r/255, g/255, b/255) for r, g, b in rep_color_list]

        img = np.array(Image.open(image_path))

        cols = math.ceil(math.sqrt(len(norm_c_colors)))                   
        rows = math.ceil(math.sqrt(len(norm_c_colors)))

        fig, ax = plt.subplots(figsize=(40, 40))

        ax.set_xlim(0, cols)
        ax.set_ylim(0, rows)
        ax.set_aspect('equal')
        ax.axis('off')

        for i, color in enumerate(norm_c_colors):
            row = rows - 1 - (i // cols)      
            col = i % cols

            circle = patches.Circle((col + 0.5, row + 0.5), 0.4, color=color)
            ax.add_patch(circle)

        output_path = get_output_path(image_path, "_rep_color")
        print(output_path)
        plt.savefig(output_path)

    def separated_rep_color_visualization(image_path, blindness_param):
        rep_color_list, _, _ = rep_colors(image_path, cube_slength) # pyright: ignore[reportUndefinedVariable]
        dichromat_color_list = [dichromat_simul(c, blindness_param) for c in rep_color_list]
        confusing_color_set, nonconfusing_color_set = sep_confusing(rep_color_list, dichromat_color_list, delta)

        norm_c_colors = [(r/255, g/255, b/255) for r, g, b in confusing_color_set] # normalize to 0–1
        norm_nc_colors = [(r/255, g/255, b/255) for r, g, b in nonconfusing_color_set]

        img = np.array(Image.open(image_path))

        # confusing representative colors

        c_cols = math.ceil(math.sqrt(len(norm_c_colors)))                   
        c_rows = math.ceil(math.sqrt(len(norm_nc_colors)))

        fig, ax = plt.subplots(figsize=(40, 40))

        ax.set_xlim(0, c_cols)
        ax.set_ylim(0, c_rows)
        ax.set_aspect('equal')
        ax.axis('off')

        plt.title("Confusing Representative Colors", fontsize=40)

        for i, color in enumerate(norm_c_colors):
            row = c_rows - 1 - (i // c_cols)      
            col = i % c_cols

            circle = patches.Circle((col + 0.5, row + 0.5 + 5), 0.4, color=color)
            ax.add_patch(circle)

        plt.tight_layout(rect=[0, 0, 1, 0.95])
        output_path = get_output_path(image_path, "_separated_conf_rep_color_" + blindness_str(blindness_param))
        plt.savefig(output_path)

        nc_cols = math.ceil(math.sqrt(len(norm_nc_colors)))
        nc_rows = math.ceil(math.sqrt(len(norm_nc_colors)))
        fig, ax = plt.subplots(figsize=(40, 40))

        ax.set_xlim(0, nc_cols)
        ax.set_ylim(0, nc_rows)
        ax.set_aspect('equal')
        ax.axis('off')

        plt.title("Nonconfusing Representative Colors", fontsize=40)

        # nonconfusing representative colors
        for i, color in enumerate(norm_nc_colors):
            row = nc_rows - 1 - (i // nc_cols)      
            col = i % nc_cols

            circle = patches.Circle((col + 0.5, row + 0.5), 0.4, color=color)
            ax.add_patch(circle)

        plt.tight_layout(rect=[0, 0, 1, 0.95])
        output_path = get_output_path(image_path, "_separated_nonconf_rep_color_" + blindness_str(blindness_param))
        plt.savefig(output_path)

    dichromat_simul_img(image_path, blindness_param)
    rep_color_visualization(image_path)
    separated_rep_color_visualization(image_path, blindness_param)

    key_c_colors, key_nc_colors, conf_cardinalities, nonconf_cardinalities, cluster_to_pixel, conf_clusters, nonconf_clusters = module_1(image_path, cube_slength, delta, blindness_param, m, n)

    copunctal = (0.747, 0.253)
    if blindness_param == deutan:
        copunctal = (1.08, -0.8)
    conf_heap, nonconf_heap, key_c_xy_dict, key_nc_xy_dict, key_c_xyy_dict, key_nc_xyy_dict, colors_to_translate, color_translation_map = module_2(key_c_colors, key_nc_colors, conf_cardinalities, nonconf_cardinalities, copunctal)

    orig_rgb_to_rec_rgb_dict = module_3(key_c_xy_dict, key_c_xyy_dict, color_translation_map, key_nc_colors, blindness_param, lam=0.2)
   
    # normalize RGB colors to [0, 1]
    def normalize_color(color):
        return (color[0] / 255, color[1] / 255, color[2] / 255)

    # create the plot
    fig, ax = plt.subplots(figsize=(10, 35))

    ax.axis("off")

    large_bubble_radius = 0.2
    small_bubble_radius = 0.025

    y_offset = 0 # vertical offset to space out each group

    for idx, (key_color, clustered_colors) in enumerate(nonconf_clusters.items()):
        k_color = normalize_color(key_color)
        
        # plot the main large bubble
        ax.add_patch(plt.Circle((0.5, y_offset), large_bubble_radius, color=k_color))

        # plot the small bubbles
        for j, clus_color in enumerate(clustered_colors):
            cl_color = normalize_color(clus_color)
            # small bubbles surrounding the main bubble
            angle = np.linspace(0, 2 * np.pi, len(clustered_colors), endpoint=False)[j]
            x_offset = 0.25 * np.cos(angle)
            y_offset_small = 0.25 * np.sin(angle)
            ax.add_patch(plt.Circle((0.5 + x_offset, y_offset + y_offset_small), small_bubble_radius, color=cl_color))

        # move down the plot for the next main color
        y_offset -= 0.6

    padding = 0.2  # padding around bubbles
    max_offset = large_bubble_radius + 0.13 + small_bubble_radius + padding

    ax.set_xlim(0.5 - max_offset, 0.5 + max_offset)  
    ax.set_ylim(y_offset - max_offset, 1 + max_offset) 
    ax.set_aspect('equal')

    output_path = get_output_path(image_path, "_nonconf_cluster_" + blindness_str(blindness_param))
    plt.savefig(output_path, bbox_inches='tight')

    plt.tight_layout()

    # create the plot
    fig, ax = plt.subplots(figsize=(10, 35))

    ax.axis("off")

    large_bubble_radius = 0.2
    small_bubble_radius = 0.025

    y_offset = 0 # vertical offset to space out each group

    for idx, (key_color, clustered_colors) in enumerate(conf_clusters.items()):
        k_color = normalize_color(key_color)
        
        # plot the main large bubble
        ax.add_patch(plt.Circle((0.5, y_offset), large_bubble_radius, color=k_color))

        # plot the small bubbles
        for j, clus_color in enumerate(clustered_colors):
            cl_color = normalize_color(clus_color)
            # small bubbles surrounding the main bubble
            angle = np.linspace(0, 2 * np.pi, len(clustered_colors), endpoint=False)[j]
            x_offset = 0.25 * np.cos(angle)
            y_offset_small = 0.25 * np.sin(angle)
            ax.add_patch(plt.Circle((0.5 + x_offset, y_offset + y_offset_small), small_bubble_radius, color=cl_color))

        # move down the plot for the next main color
        y_offset -= 0.6

    padding = 0.2  # padding around bubbles
    max_offset = large_bubble_radius + 0.13 + small_bubble_radius + padding

    ax.set_xlim(0.5 - max_offset, 0.5 + max_offset)  
    ax.set_ylim(y_offset - max_offset, 1 + max_offset) 
    ax.set_aspect('equal')

    output_path = get_output_path(image_path, "_conf_cluster_" + blindness_str(blindness_param))
    plt.savefig(output_path, bbox_inches='tight')

    plt.tight_layout()


    # key colors cardinality visualization
    img = np.array(Image.open(image_path))
    fig, ax = plt.subplots(1, 2, figsize=(8, 5), gridspec_kw={'width_ratios': [4, 1]})
    fig.suptitle("Key Confusing Colors Extracted, with their Cluster Cardinalities")

    # Show image
    ax[0].imshow(img)
    ax[0].axis('off')

    # show color dots
    ax[1].axis('off')
    ax[1].set_aspect('equal', 'box')

    # for i, color in enumerate(norm_c_colors):
    for i, color in enumerate(conf_cardinalities):
        norm_color = color[0] / 255, color[1] / 255, color[2] / 255
        circle = patches.Circle((0.5, len(conf_cardinalities)-i-0.5), 0.4, color=norm_color)
        ax[1].add_patch(circle)
        ax[1].text(0.7, len(conf_cardinalities)-i-0.5, conf_cardinalities[color], va='center', ha='left', fontsize=12)
       
    ax[1].set_xlim(0, 1)
    ax[1].set_ylim(0, len(conf_cardinalities))


    plt.tight_layout()
    output_path = get_output_path(image_path, "_key_conf_color_w_cardinality_" + blindness_str(blindness_param))
    plt.savefig(output_path)



    # confusion lines visualization
    # pre-translation plot
    fig, ax = colour.plotting.plot_chromaticity_diagram_CIE1931(
        show_diagram_colours=True, 
        show_spectral_locus=True,
        standalone=False
    )

    for (r, g, b), (x, y) in key_c_xy_dict.items():
        plt.plot(x, y, 'o', color='black', markersize=8)

    for (x, y) in colors_to_translate:
        plt.plot(x, y, 'o', color='white', markersize=8, markeredgecolor='black')

    for (r, g, b), (x, y) in key_nc_xy_dict.items():
        plt.plot(x, y, 'o', color='gray', markersize=8, markeredgecolor='black')

    conf_lines = confusion_lines(copunctal)

    for conf_line in conf_lines:
        ax.plot((conf_line[0], copunctal[0]), (conf_line[1], copunctal[1]), 'b-') # 'b-' for black solid line

    # display the plot
    plt.title("Key Colors & Confusion Lines (white dots = confusing key colors that need to be translated; black = confusing key colors that don't need translation, gray = nonconfusing key colors)")
    plt.tight_layout()
    output_path = get_output_path(image_path, "_pre_trans_confusion_lines_" + blindness_str(blindness_param))
    plt.savefig(output_path)

    fig, ax = colour.plotting.plot_chromaticity_diagram_CIE1931(
        show_diagram_colours=True, 
        show_spectral_locus=True,
        standalone=False
    )

    for (r, g, b), (x, y) in key_c_xy_dict.items():
        if (x, y) not in colors_to_translate:
            plt.plot(x, y, 'o', color='black', markersize=8)

    for (r, g, b), (x, y) in key_nc_xy_dict.items():
        plt.plot(x, y, 'o', color='gray', markersize=8, markeredgecolor='black')

    for (x, y) in colors_to_translate:
        translated_x, translated_y = color_translation_map[(x, y)]
        plt.plot(translated_x, translated_y, 'o', color='white', markersize=8, markeredgecolor='black')

    conf_lines = confusion_lines(copunctal)

    for conf_line in conf_lines:
        ax.plot((conf_line[0], copunctal[0]), (conf_line[1], copunctal[1]), 'b-') # 'b-' for blue solid line

    # display the plot
    plt.title("Key Confusing Colors & Confusion Lines (white dots = key confusing colors that have been translated, black = key confusing colors that were not translated, gray = nonconfusing key colors)")
    plt.tight_layout()
    output_path = get_output_path(image_path, "_post_trans_confusion_lines_" + blindness_str(blindness_param))
    plt.savefig(output_path)


    orig_colors = []
    first_attempt_rec_colors = []
    luminance_adj_rec_colors = []
    for rgb_color in orig_rgb_to_rec_rgb_dict:
        orig_colors.append(rgb_color)
        xy_color = key_c_xy_dict[rgb_color]
        if xy_color in color_translation_map:
            first_attempt_rec_xy = color_translation_map[xy_color]
            first_attempt_rec_rgb = convertXyzToRgb(convertXyyToXyz((first_attempt_rec_xy[0], first_attempt_rec_xy[1], key_c_xyy_dict[xy_color][2])))
            first_attempt_rec_colors.append(first_attempt_rec_rgb)
        else:
            first_attempt_rec_colors.append(rgb_color)
        luminance_adj_rec_colors.append(orig_rgb_to_rec_rgb_dict[rgb_color])


    cols = [orig_colors, first_attempt_rec_colors, luminance_adj_rec_colors]
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_facecolor('lightblue')
    for i, col in enumerate(cols):
        for j, color in enumerate(col):
            circ = patches.Circle((i + 3.6, len(col)-j-0.5), 0.4, color=(color[0]/255, color[1]/255, color[2]/255), edgecolor='black')
            ax.add_patch(circ)


    ax.set_xlim(0, len(orig_colors))
    ax.set_ylim(0, len(orig_colors))
    ax.set_xticks([])
    ax.set_yticks([])

    plt.title("Original Key Confusing Colors (left), Translated (middle), Optimized for Naturalness (right)")

    plt.gca().invert_yaxis()
    output_path = get_output_path(image_path, "_col_trans_luminance_" + blindness_str(blindness_param))
    plt.savefig(output_path)

    # final image output
    output_image = module_4(orig_rgb_to_rec_rgb_dict, cluster_to_pixel, image_path)
    # visualize some tests
    output_path = get_output_path(image_path, "_cluster_to_cluster_translated_" + blindness_str(blindness_param))
    output_image.save(output_path)


    # dichromat simulation
    dichromat_img = output_image.copy()
    width, height = output_image.size
    for y in range(height):
        for x in range(width):
            original_rgb = output_image.getpixel((x, y))
            new_pixel = dichromat_simul(original_rgb, blindness_param)
            dichromat_img.putpixel((x, y), (int(new_pixel[0]), int(new_pixel[1]), int(new_pixel[2])))
   
    output_path = get_output_path(image_path, "_cluster_to_cluster_translated_dichromt_simul_" + blindness_str(blindness_param))
    dichromat_img.save(output_path)

# ## Dichromat Simulation Visualization

# refactored
# takes in image path as string and color blindness type
# renders image under dichromat simulation
def dichromat_simul_img(img_path, blindness_param):
    try:
        img = Image.open(img_path)
        width, height = img.size
        for y in range(height):
            for x in range(width):
                original_rgb = img.getpixel((x, y))
                new_pixel = dichromat_simul(original_rgb, blindness_param)
                img.putpixel((x, y), (int(new_pixel[0]), int(new_pixel[1]), int(new_pixel[2])))
        
        img.show()
        blindness = blindness_str(blindness_param)
        output_img_path = get_output_path(img_path, "_dichromat_simul_" + blindness)
        img.save(output_img_path)
    except FileNotFoundError:
        print("Image file not found at " + img_path)
    except Exception as e:
        print("An error occurred: " + e)

# ## Key Color Extraction Visualization
# refactored
# visualizes an image, with all the representative colors arranged in a column to the right of the image
# takes in image path as string and side length of color bin cubes
def rep_color_visualization(image_path):
    rep_color_list, _, _ = rep_colors(image_path, cube_slength)
    norm_c_colors = [(r/255, g/255, b/255) for r, g, b in rep_color_list]

    img = np.array(Image.open(image_path))

    cols = math.ceil(math.sqrt(len(norm_c_colors)))                   
    rows = math.ceil(math.sqrt(len(norm_c_colors)))

    fig, ax = plt.subplots(figsize=(40, 40))

    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_aspect('equal')
    ax.axis('off')

    for i, color in enumerate(norm_c_colors):
        row = rows - 1 - (i // cols)      
        col = i % cols

        circle = patches.Circle((col + 0.5, row + 0.5), 0.4, color=color)
        ax.add_patch(circle)

    output_path = get_output_path(image_path, "_rep_color")
    print(output_path)
    plt.savefig(output_path)
    plt.show()

# visualizes an image, with representative colors separated into confusing and non-confusing columns to the right of the image
# takes in image path as string, side length of color bin cubes, and blindness parameter
def separated_rep_color_visualization(image_path, blindness_param):
    rep_color_list, _, _ = rep_colors(image_path, cube_slength) # pyright: ignore[reportUndefinedVariable]
    dichromat_color_list = [dichromat_simul(c, blindness_param) for c in rep_color_list]
    confusing_color_set, nonconfusing_color_set = sep_confusing(rep_color_list, dichromat_color_list, delta)

    norm_c_colors = [(r/255, g/255, b/255) for r, g, b in confusing_color_set] # normalize to 0–1
    norm_nc_colors = [(r/255, g/255, b/255) for r, g, b in nonconfusing_color_set]

    img = np.array(Image.open(image_path))

    # confusing representative colors

    c_cols = math.ceil(math.sqrt(len(norm_c_colors)))                   
    c_rows = math.ceil(math.sqrt(len(norm_nc_colors)))

    fig, ax = plt.subplots(figsize=(40, 40))

    ax.set_xlim(0, c_cols)
    ax.set_ylim(0, c_rows)
    ax.set_aspect('equal')
    ax.axis('off')

    plt.title("Confusing Representative Colors", fontsize=40)

    for i, color in enumerate(norm_c_colors):
        row = c_rows - 1 - (i // c_cols)      
        col = i % c_cols

        circle = patches.Circle((col + 0.5, row + 0.5 + 5), 0.4, color=color)
        ax.add_patch(circle)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    output_path = get_output_path(image_path, "_separated_conf_rep_color_" + blindness_str(blindness_param))
    plt.savefig(output_path)
    plt.show()

    nc_cols = math.ceil(math.sqrt(len(norm_nc_colors)))
    nc_rows = math.ceil(math.sqrt(len(norm_nc_colors)))
    fig, ax = plt.subplots(figsize=(40, 40))

    ax.set_xlim(0, nc_cols)
    ax.set_ylim(0, nc_rows)
    ax.set_aspect('equal')
    ax.axis('off')

    plt.title("Nonconfusing Representative Colors", fontsize=40)

    # nonconfusing representative colors
    for i, color in enumerate(norm_nc_colors):
        row = nc_rows - 1 - (i // nc_cols)      
        col = i % nc_cols

        circle = patches.Circle((col + 0.5, row + 0.5), 0.4, color=color)
        ax.add_patch(circle)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    output_path = get_output_path(image_path, "_separated_nonconf_rep_color_" + blindness_str(blindness_param))
    plt.savefig(output_path)
    plt.show()

# visualizes nonconfusing color clusters
# takes in image path as string, blindness parameter
def nonconf_cluster_visualization(image_path, blindness_param):
    rep_color_list, _, _ = rep_colors(image_path, cube_slength)
    dichromat_color_list = [dichromat_simul(c, blindness_param) for c in rep_color_list]
    confusing_color_set, nonconfusing_color_set = sep_confusing(rep_color_list, dichromat_color_list, delta)
    _, nonconf_clusters = fuzzy_clustering(nonconfusing_color_set, n)

    # normalize RGB colors to [0, 1]
    def normalize_color(color):
        return (color[0] / 255, color[1] / 255, color[2] / 255)

    # create the plot
    fig, ax = plt.subplots(figsize=(10, 35))

    ax.axis("off")

    large_bubble_radius = 0.6
    small_bubble_radius = 0.025

    y_offset = 0 # vertical offset to space out each group

    for idx, (key_color, clustered_colors) in enumerate(nonconf_clusters.items()):
        k_color = normalize_color(key_color)
        
        # plot the main large bubble
        ax.add_patch(plt.Circle((0.5, y_offset), large_bubble_radius, color=k_color))

        # plot the small bubbles
        for j, clus_color in enumerate(clustered_colors):
            cl_color = normalize_color(clus_color)
            # small bubbles surrounding the main bubble
            angle = np.linspace(0, 2 * np.pi, len(clustered_colors), endpoint=False)[j]
            x_offset = 0.7 * np.cos(angle)
            y_offset_small = 0.7 * np.sin(angle)
            ax.add_patch(plt.Circle((0.5 + x_offset, y_offset + y_offset_small), small_bubble_radius, color=cl_color))

        # move down the plot for the next main color
        y_offset -= 1.6

    padding = 0  # padding around bubbles
    max_offset = large_bubble_radius + 0.13 + small_bubble_radius + padding

    ax.set_xlim(0.5 - max_offset, 0.5 + max_offset)  
    ax.set_ylim(y_offset + 0.6, max_offset) 
    ax.set_aspect('equal')

    output_path = get_output_path(image_path, "_nonconf_cluster_" + blindness_str(blindness_param))
    plt.savefig(output_path)

    plt.tight_layout()
    plt.show()

# visualizes nonconfusing color clusters
# takes in image path as string, blindness parameter
def conf_cluster_visualization(image_path, blindness_param):
    rep_color_list, _, _ = rep_colors(image_path, cube_slength)
    dichromat_color_list = [dichromat_simul(c, blindness_param) for c in rep_color_list]
    confusing_color_set, nonconfusing_color_set = sep_confusing(rep_color_list, dichromat_color_list, delta)
    _, conf_clusters= fuzzy_clustering(confusing_color_set, m)

    # normalize RGB colors to [0, 1]
    def normalize_color(color):
        return (color[0] / 255, color[1] / 255, color[2] / 255)

    # create the plot
    fig, ax = plt.subplots(figsize=(10, 35))

    ax.axis("off")

    large_bubble_radius = 0.6
    small_bubble_radius = 0.025

    y_offset = 0 # vertical offset to space out each group

    for idx, (key_color, clustered_colors) in enumerate(conf_clusters.items()):
        k_color = normalize_color(key_color)
        
        # plot the main large bubble
        ax.add_patch(plt.Circle((0.5, y_offset), large_bubble_radius, color=k_color))

        # plot the small bubbles
        for j, clus_color in enumerate(clustered_colors):
            cl_color = normalize_color(clus_color)
            # small bubbles surrounding the main bubble
            angle = np.linspace(0, 2 * np.pi, len(clustered_colors), endpoint=False)[j]
            x_offset = 0.7 * np.cos(angle)
            y_offset_small = 0.7 * np.sin(angle)
            ax.add_patch(plt.Circle((0.5 + x_offset, y_offset + y_offset_small), small_bubble_radius, color=cl_color))

        # move down the plot for the next main color
        y_offset -= 1.6

    padding = 0  # padding around bubbles
    max_offset = large_bubble_radius + 0.13 + small_bubble_radius + padding

    ax.set_xlim(0.5 - max_offset, 0.5 + max_offset)  
    ax.set_ylim(y_offset + 0.6, max_offset) 
    ax.set_aspect('equal')

    output_path = get_output_path(image_path, "_conf_cluster_" + blindness_str(blindness_param))
    plt.savefig(output_path)

    plt.tight_layout()
    plt.show()

def key_conf_color_w_cardinality(img_path, blindness_param):


    key_c_colors, key_nc_colors, conf_cardinalities, nonconf_cardinalities, _, _, _ = module_1(img_path, cube_slength, delta, blindness_param, m, n)
    
    norm_c_colors = [(r/255, g/255, b/255) for r, g, b in conf_cardinalities]  # normalize to 0–1


    img = np.array(Image.open(img_path))


    fig, ax = plt.subplots(1, 2, figsize=(8, 5), gridspec_kw={'width_ratios': [4, 1]})
    fig.suptitle("Key Confusing Colors Extracted, with their Cluster Cardinalities")


    # Show image
    ax[0].imshow(img)
    ax[0].axis('off')


    # show color dots
    ax[1].axis('off')
    ax[1].set_aspect('equal', 'box')


    # for i, color in enumerate(norm_c_colors):
    for i, color in enumerate(conf_cardinalities):
        norm_color = color[0] / 255, color[1] / 255, color[2] / color
        circle = patches.Circle((0.5, len(conf_cardinalities)-i-0.5), 0.4, color=norm_color)
        ax[1].add_patch(circle)
        ax[1].text(0.7, len(conf_cardinalities)-i-0.5, conf_cardinalities[color], va='center', ha='left', fontsize=12)
       
    ax[1].set_xlim(0, 1)
    ax[1].set_ylim(0, len(conf_cardinalities))


    plt.tight_layout()
    output_path = get_output_path(img_path, "_key_conf_color_w_cardinality_" + blindness_str(blindness_param))
    plt.savefig(output_path)
    plt.show()

# ## Key Color Translation Visualization

def color_translation_visualization(img_path, blindness_param):
    copunctal = (0.747, 0.253)
    if blindness_param == deutan:
        copunctal = (1.08, -0.8)
    key_c_colors, key_nc_colors, conf_cardinalities, nonconf_cardinalities, _, _, _ = module_1(img_path, cube_slength, delta, blindness_param, m, n)
    conf_heap, nonconf_heap, key_c_xy_dict, key_nc_xy_dict, key_c_xyy_dict, key_nc_xyy_dict, colors_to_translate, color_translation_map = module_2(key_c_colors, key_nc_colors, conf_cardinalities, nonconf_cardinalities, copunctal)

    # pre-translation plot
    fig, ax = colour.plotting.plot_chromaticity_diagram_CIE1931(
        show_diagram_colours=True, 
        show_spectral_locus=True,
        standalone=False
    )

    for (r, g, b), (x, y) in key_c_xy_dict.items():
        plt.plot(x, y, 'o', color='black', markersize=8)

    for (x, y) in colors_to_translate:
        plt.plot(x, y, 'o', color='white', markersize=8, markeredgecolor='black')

    for (r, g, b), (x, y) in key_nc_xy_dict.items():
        plt.plot(x, y, 'o', color='gray', markersize=8, markeredgecolor='black')

    conf_lines = confusion_lines(copunctal)

    for conf_line in conf_lines:
        ax.plot((conf_line[0], copunctal[0]), (conf_line[1], copunctal[1]), 'b-') # 'b-' for black solid line

    # display the plot
    plt.title("Key Colors & Confusion Lines (white dots = confusing key colors that need to be translated; black = confusing key colors that don't need translation, gray = nonconfusing key colors)")
    plt.tight_layout()
    output_path = get_output_path(img_path, "_pre_trans_confusion_lines_" + blindness_str(blindness_param))
    plt.savefig(output_path)
    plt.show()

    fig, ax = colour.plotting.plot_chromaticity_diagram_CIE1931(
        show_diagram_colours=True, 
        show_spectral_locus=True,
        standalone=False
    )

    for (r, g, b), (x, y) in key_c_xy_dict.items():
        if (x, y) not in colors_to_translate:
            plt.plot(x, y, 'o', color='black', markersize=8)

    for (r, g, b), (x, y) in key_nc_xy_dict.items():
        plt.plot(x, y, 'o', color='gray', markersize=8, markeredgecolor='black')

    for (x, y) in colors_to_translate:
        translated_x, translated_y = color_translation_map[(x, y)]
        plt.plot(translated_x, translated_y, 'o', color='white', markersize=8, markeredgecolor='black')

    conf_lines = confusion_lines(copunctal)

    for conf_line in conf_lines:
        ax.plot((conf_line[0], copunctal[0]), (conf_line[1], copunctal[1]), 'b-') # 'b-' for blue solid line

    # display the plot
    plt.title("Key Confusing Colors & Confusion Lines (white dots = key confusing colors that have been translated, black = key confusing colors that were not translated, gray = nonconfusing key colors)")
    plt.tight_layout()
    output_path = get_output_path(img_path, "_post_trans_confusion_lines_" + blindness_str(blindness_param))
    plt.savefig(output_path)
    plt.show()

def color_translation_and_luminance_adjustment_visualization(img_path, blindness_param):
    copunctal = (0.747, 0.253)
    if blindness_param == deutan:
        copunctal = (1.08, -0.8)


    key_c_colors, key_nc_colors, conf_cardinalities, nonconf_cardinalities, _, _, _ = module_1(img_path, cube_slength, delta, blindness_param, m, n)
    conf_heap, nonconf_heap, key_c_xy_dict, key_nc_xy_dict, key_c_xyy_dict, key_nc_xyy_dict, colors_to_translate, color_translation_map = module_2(key_c_colors, key_nc_colors, conf_cardinalities, nonconf_cardinalities, copunctal)
    orig_rgb_to_rec_rgb_dict = module_3(key_c_xy_dict, key_c_xyy_dict, color_translation_map, key_nc_colors, blindness_param, lam=0.2)


    orig_colors = []
    first_attempt_rec_colors = []
    luminance_adj_rec_colors = []
    for rgb_color in orig_rgb_to_rec_rgb_dict:
        orig_colors.append(rgb_color)
        xy_color = key_c_xy_dict[rgb_color]
        if xy_color in color_translation_map:
            first_attempt_rec_xy = color_translation_map[xy_color]
            first_attempt_rec_rgb = convertXyzToRgb(convertXyyToXyz((first_attempt_rec_xy[0], first_attempt_rec_xy[1], key_c_xyy_dict[xy_color][2])))
            first_attempt_rec_colors.append(first_attempt_rec_rgb)
        else:
            first_attempt_rec_colors.append(rgb_color)
        luminance_adj_rec_colors.append(orig_rgb_to_rec_rgb_dict[rgb_color])


    cols = [orig_colors, first_attempt_rec_colors, luminance_adj_rec_colors]
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_facecolor('lightblue')
    for i, col in enumerate(cols):
        for j, color in enumerate(col):
            circ = patches.Circle((i + 3.6, len(col)-j-0.5), 0.4, color=(color[0]/255, color[1]/255, color[2]/255), edgecolor='black')
            ax.add_patch(circ)


    ax.set_xlim(0, len(orig_colors))
    ax.set_ylim(0, len(orig_colors))
    ax.set_xticks([])
    ax.set_yticks([])

    plt.title("Original Key Confusing Colors (left), Translated (middle), Optimized for Naturalness (right)")

    plt.gca().invert_yaxis()
    output_path = get_output_path(img_path, "_col_trans_luminance_" + blindness_str(blindness_param))
    plt.savefig(output_path)
    plt.show()

# # Cluster to Cluster Transfer Visualization

def cluster_to_cluster_translation_visualization(img_path, blindness_param):
    copunctal = (0.747, 0.253)
    if blindness_param == deutan:
        copunctal = (1.08, -0.8)


    key_c_colors, key_nc_colors, conf_cardinalities, nonconf_cardinalities, cluster_to_pixel, _, _ = module_1(img_path, cube_slength, delta, blindness_param, m, n)
    conf_heap, nonconf_heap, key_c_xy_dict, key_nc_xy_dict, key_c_xyy_dict, key_nc_xyy_dict, colors_to_translate, color_translation_map = module_2(key_c_colors, key_nc_colors, conf_cardinalities, nonconf_cardinalities, copunctal)
    orig_rgb_to_rec_rgb_dict = module_3(key_c_xy_dict, key_c_xyy_dict, color_translation_map, key_nc_colors, blindness_param, lam=0.2)
    output_image = module_4(orig_rgb_to_rec_rgb_dict, cluster_to_pixel, img_path)


    # visualize some tests
    output_path = get_output_path(img_path, "_cluster_to_cluster_translated_" + blindness_str(blindness_param))
    output_image.save(output_path)


    # dichromat simulation
    dichromat_img = output_image.copy()
    width, height = output_image.size
    for y in range(height):
        for x in range(width):
            original_rgb = output_image.getpixel((x, y))
            new_pixel = dichromat_simul(original_rgb, blindness_param)
            dichromat_img.putpixel((x, y), (int(new_pixel[0]), int(new_pixel[1]), int(new_pixel[2])))
   
    output_path = get_output_path(img_path, "_cluster_to_cluster_translated_dichromt_simul_" + blindness_str(blindness_param))
    dichromat_img.save(output_path)


