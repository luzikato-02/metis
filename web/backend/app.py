"""Flask application factory and main entry point."""

import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

# Add parent directory to path for data_cleaning import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from data_cleaning import DataCleaner, DataCleaningConfig, read_input_file, write_output_file

from config import config
from models import DataFile, db


def create_app(config_name: str = "default") -> Flask:
    """Create and configure the Flask application."""
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    CORS(app, origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"])
    db.init_app(app)
    
    # Ensure directories exist
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    Path(app.config["OUTPUT_FOLDER"]).mkdir(parents=True, exist_ok=True)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Register routes
    register_routes(app)
    
    return app


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def register_routes(app: Flask) -> None:
    """Register all application routes."""
    
    @app.route("/api/health", methods=["GET"])
    def health_check():
        """Health check endpoint."""
        return jsonify({"status": "healthy", "message": "Data Cleaning API is running"})
    
    @app.route("/api/files", methods=["GET"])
    def list_files():
        """List all files with optional filtering."""
        category = request.args.get("category")  # 'input' or 'output'
        
        query = DataFile.query.order_by(DataFile.created_at.desc())
        
        if category:
            query = query.filter_by(category=category)
        
        files = query.all()
        return jsonify({"files": [f.to_dict() for f in files]})
    
    @app.route("/api/files/<int:file_id>", methods=["GET"])
    def get_file(file_id: int):
        """Get file details by ID."""
        file = DataFile.query.get_or_404(file_id)
        return jsonify({"file": file.to_dict()})
    
    @app.route("/api/files/<int:file_id>/data", methods=["GET"])
    def get_file_data(file_id: int):
        """Get file data as JSON for datatable display."""
        file = DataFile.query.get_or_404(file_id)
        
        # Determine file path
        if file.category == "input":
            file_path = Path(app.config["UPLOAD_FOLDER"]) / file.stored_filename
        else:
            file_path = Path(app.config["OUTPUT_FOLDER"]) / file.stored_filename
        
        if not file_path.exists():
            return jsonify({"error": "File not found on disk"}), 404
        
        try:
            # Read file
            df = read_input_file(file_path)
            
            # Pagination
            page = request.args.get("page", 1, type=int)
            per_page = request.args.get("per_page", 50, type=int)
            per_page = min(per_page, 500)  # Max 500 rows per page
            
            total_rows = len(df)
            total_pages = (total_rows + per_page - 1) // per_page
            
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            
            # Get page data
            page_df = df.iloc[start_idx:end_idx]
            
            # Convert to records, handling NaN values
            records = json.loads(page_df.to_json(orient="records", date_format="iso"))
            
            return jsonify({
                "columns": list(df.columns),
                "data": records,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total_rows": total_rows,
                    "total_pages": total_pages,
                },
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    @app.route("/api/files/<int:file_id>/download", methods=["GET"])
    def download_file(file_id: int):
        """Download a file."""
        file = DataFile.query.get_or_404(file_id)
        
        if file.category == "input":
            file_path = Path(app.config["UPLOAD_FOLDER"]) / file.stored_filename
        else:
            file_path = Path(app.config["OUTPUT_FOLDER"]) / file.stored_filename
        
        if not file_path.exists():
            return jsonify({"error": "File not found"}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=file.original_filename,
        )
    
    @app.route("/api/files/<int:file_id>", methods=["DELETE"])
    def delete_file(file_id: int):
        """Delete a file."""
        file = DataFile.query.get_or_404(file_id)
        
        # Delete physical file
        if file.category == "input":
            file_path = Path(app.config["UPLOAD_FOLDER"]) / file.stored_filename
        else:
            file_path = Path(app.config["OUTPUT_FOLDER"]) / file.stored_filename
        
        if file_path.exists():
            file_path.unlink()
        
        # Delete associated output files
        for output in file.outputs:
            output_path = Path(app.config["OUTPUT_FOLDER"]) / output.stored_filename
            if output_path.exists():
                output_path.unlink()
            db.session.delete(output)
        
        db.session.delete(file)
        db.session.commit()
        
        return jsonify({"message": "File deleted successfully"})
    
    @app.route("/api/upload", methods=["POST"])
    def upload_file():
        """Upload a new file."""
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files["file"]
        
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename, app.config["ALLOWED_EXTENSIONS"]):
            return jsonify({"error": "File type not allowed"}), 400
        
        # Generate unique filename
        original_filename = file.filename
        file_ext = original_filename.rsplit(".", 1)[1].lower()
        stored_filename = f"{uuid.uuid4().hex}.{file_ext}"
        
        # Save file
        upload_path = Path(app.config["UPLOAD_FOLDER"]) / stored_filename
        file.save(upload_path)
        
        # Get file info
        file_size = upload_path.stat().st_size
        
        try:
            # Read file to get metadata
            df = read_input_file(upload_path)
            row_count = len(df)
            column_count = len(df.columns)
            columns_json = json.dumps(list(df.columns))
        except Exception as e:
            # Remove file if we can't read it
            upload_path.unlink()
            return jsonify({"error": f"Could not read file: {str(e)}"}), 400
        
        # Create database record
        data_file = DataFile(
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_type=file_ext,
            file_size=file_size,
            category="input",
            row_count=row_count,
            column_count=column_count,
            columns_json=columns_json,
            status="completed",
        )
        
        db.session.add(data_file)
        db.session.commit()
        
        return jsonify({"file": data_file.to_dict()}), 201
    
    @app.route("/api/process/<int:file_id>", methods=["POST"])
    def process_file(file_id: int):
        """Process (clean) an input file."""
        input_file = DataFile.query.get_or_404(file_id)
        
        if input_file.category != "input":
            return jsonify({"error": "Can only process input files"}), 400
        
        # Get configuration from request
        config_data = request.get_json() or {}
        
        # Build DataCleaningConfig
        cleaning_config = DataCleaningConfig(
            rpm_max=config_data.get("rpm_max", 10000),
            efficiency_min=config_data.get("efficiency_min", 75.0),
            efficiency_max=config_data.get("efficiency_max", 100.0),
            spindles_per_side=config_data.get("spindles_per_side", 84),
            shift_hours=config_data.get("shift_hours", 8.0),
            drop_multi_style_shifts=config_data.get("drop_multi_style_shifts", True),
        )
        
        # Read input file
        input_path = Path(app.config["UPLOAD_FOLDER"]) / input_file.stored_filename
        
        try:
            df_raw = read_input_file(input_path)
            
            # Clean data
            cleaner = DataCleaner(config=cleaning_config)
            df_clean = cleaner.clean(df_raw)
            
            # Generate output filename
            output_ext = config_data.get("output_format", input_file.file_type)
            output_stored_filename = f"{uuid.uuid4().hex}.{output_ext}"
            output_path = Path(app.config["OUTPUT_FOLDER"]) / output_stored_filename
            
            # Write output file
            write_output_file(df_clean, output_path)
            
            # Create output file record
            output_file = DataFile(
                original_filename=f"cleaned_{input_file.original_filename.rsplit('.', 1)[0]}.{output_ext}",
                stored_filename=output_stored_filename,
                file_type=output_ext,
                file_size=output_path.stat().st_size,
                category="output",
                parent_id=input_file.id,
                config_json=json.dumps(config_data),
                row_count=len(df_clean),
                column_count=len(df_clean.columns),
                columns_json=json.dumps(list(df_clean.columns)),
                status="completed",
                processed_at=datetime.utcnow(),
            )
            
            db.session.add(output_file)
            db.session.commit()
            
            return jsonify({
                "message": "File processed successfully",
                "input_file": input_file.to_dict(),
                "output_file": output_file.to_dict(),
                "stats": {
                    "input_rows": len(df_raw),
                    "output_rows": len(df_clean),
                    "rows_removed": len(df_raw) - len(df_clean),
                },
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500


# Create app instance
app = create_app(os.environ.get("FLASK_ENV", "development"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
