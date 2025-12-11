from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS, cross_origin
import recoloring
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "app_data"

@app.route('/app_data/<path:filename>')
@cross_origin()
def app_data(filename):
    return send_from_directory('app_data', filename)

@app.route("/dichromat_simul", methods=["POST"])
@cross_origin()
def dichromat_simul_route():
    if "image" not in request.files:
        return {"error": "No file uploaded"}, 400
    
    file = request.files["image"]

    blindness = request.args.get("blindness")
    blindness_param = recoloring.deutan

    if blindness == "protan":
        blindness_param = recoloring.protan

    # Save input image - only allows for unique filenames
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    # Output path
    output_path = recoloring.get_output_path(input_path, "_dichromat_simul_" + recoloring.blindness_str(blindness_param))

    recoloring.dichromat_simul_img(input_path, blindness_param)

    # Return the processed file
    return send_file(output_path, mimetype="image/png")

@app.route("/rep_colors", methods=["POST"])
@cross_origin()
def rep_colors_route():
    if "image" not in request.files:
        return {"error": "No file uploaded"}, 400
    
    file = request.files["image"]

    # Save input image - only allows for unique filenames
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    # Output path
    output_path = recoloring.get_output_path(input_path, "_rep_color")

    # cube_slength hardcoded at 5
    recoloring.rep_color_visualization(input_path, 5)

    # Return the processed file
    return send_file(output_path, mimetype="image/png")

@app.route("/output", methods=["POST"])
@cross_origin()
def output_route():
    if "image" not in request.files:
        return {"error": "No file uploaded"}, 400
    
    file = request.files["image"]

    # Save input image - only allows for unique filenames
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    blindness = request.args.get("blindness")
    blindness_param = recoloring.deutan
    if blindness == "protan":
        blindness_param = recoloring.protan

    recoloring.visualize_process(input_path, blindness_param)

    # Output path
    output_paths = []
    output_paths.append(recoloring.get_output_path(input_path, "_cluster_to_cluster_translated_" + recoloring.blindness_str(blindness_param)))
    output_paths.append(recoloring.get_output_path(input_path, "_rep_color"))
    output_paths.append(recoloring.get_output_path(input_path, "_separated_conf_rep_color_" + recoloring.blindness_str(blindness_param)))
    output_paths.append(recoloring.get_output_path(input_path, "_separated_nonconf_rep_color_" + recoloring.blindness_str(blindness_param)))
    output_paths.append(recoloring.get_output_path(input_path, "_nonconf_cluster_" + recoloring.blindness_str(blindness_param)))
    output_paths.append(recoloring.get_output_path(input_path, "_conf_cluster_" + recoloring.blindness_str(blindness_param)))
    output_paths.append(recoloring.get_output_path(input_path, "_key_conf_color_w_cardinality_" + recoloring.blindness_str(blindness_param)))
    output_paths.append(recoloring.get_output_path(input_path, "_pre_trans_confusion_lines_" + recoloring.blindness_str(blindness_param)))
    output_paths.append(recoloring.get_output_path(input_path, "_col_trans_luminance_" + recoloring.blindness_str(blindness_param)))
    output_paths.append(recoloring.get_output_path(input_path, "_cluster_to_cluster_translated_dichromt_simul_" + recoloring.blindness_str(blindness_param)))

    urls = [request.host_url + path.replace("\\", "/") for path in output_paths]

    # Return the processed file
    return jsonify({ "urls": urls })


if __name__ == "__main__":
    app.run(debug=True)