"""Database models for the data cleaning application."""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class DataFile(db.Model):
    """Model for storing uploaded and processed files."""
    
    __tablename__ = "data_files"
    
    id = db.Column(db.Integer, primary_key=True)
    
    # File information
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False, unique=True)
    file_type = db.Column(db.String(10), nullable=False)  # csv, xlsx, parquet
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    
    # File category
    category = db.Column(db.String(20), nullable=False)  # 'input' or 'output'
    
    # Relationship to parent (for output files)
    parent_id = db.Column(db.Integer, db.ForeignKey("data_files.id"), nullable=True)
    parent = db.relationship("DataFile", remote_side=[id], backref="outputs")
    
    # Processing configuration (JSON stored as string)
    config_json = db.Column(db.Text, nullable=True)
    
    # Statistics
    row_count = db.Column(db.Integer, nullable=True)
    column_count = db.Column(db.Integer, nullable=True)
    columns_json = db.Column(db.Text, nullable=True)  # JSON list of column names
    
    # Processing status
    status = db.Column(db.String(20), default="pending")  # pending, processing, completed, failed
    error_message = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "original_filename": self.original_filename,
            "stored_filename": self.stored_filename,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "category": self.category,
            "parent_id": self.parent_id,
            "config_json": self.config_json,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "columns_json": self.columns_json,
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
        }
