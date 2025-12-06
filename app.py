from flask import Flask, request, jsonify, send_file
from flask_cors import CORS, cross_origin
import recoloring
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "app_data"

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

    # Run your notebook logic
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

    # Output path
    output_path = recoloring.get_output_path(input_path, "_cluster_to_cluster_translated_" + recoloring.blindness_str(blindness_param))

    recoloring.cluster_to_cluster_translation_visualization(input_path, blindness_param)

    # Return the processed file
    return send_file(output_path, mimetype="image/png")

# @app.route("/add", methods=["GET"])
# def add_route():
#     a = float(request.args.get("a"))
#     b = float(request.args.get("b"))
#     result = mylogic.add(a, b)
#     return jsonify({"result": result})


# @app.route("/greet", methods=["POST"])
# def greet_route():
#     data = request.get_json()
#     name = data.get("name")
#     result = mylogic.greet(name)
#     return jsonify({"message": result})


if __name__ == "__main__":
    app.run(debug=True)