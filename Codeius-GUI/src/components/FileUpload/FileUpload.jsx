import React, { useState, useRef } from 'react';
import { uploadFile, deleteUploadedFile } from '../../services/api';
import './FileUpload.css';

const FileUpload = ({ onFileSelect, onFilesChange }) => {
  const [files, setFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const droppedFiles = Array.from(e.dataTransfer.files);
    await handleFiles(droppedFiles);
  };

  const handleFileInput = async (e) => {
    const selectedFiles = Array.from(e.target.files);
    await handleFiles(selectedFiles);
  };

  const handleFiles = async (newFiles) => {
    setUploading(true);
    const successfullyUploaded = [];

    for (const file of newFiles) {
      try {
        const formData = new FormData();
        formData.append('file', file);

        const result = await uploadFile(formData);
        
        successfullyUploaded.push({
          id: Date.now() + Math.random(),
          name: file.name,
          size: file.size,
          type: result.type || 'unknown'
        });
      } catch (error) {
        console.error(`Failed to upload ${file.name}:`, error);
        alert(`Failed to upload ${file.name}: ${error.message}`);
      }
    }

    if (successfullyUploaded.length > 0) {
      const updatedFiles = [...files, ...successfullyUploaded];
      setFiles(updatedFiles);
      if (onFilesChange) {
        onFilesChange(updatedFiles);
      }
    }

    setUploading(false);
  };

  const removeFile = async (index, fileName) => {
    try {
      await deleteUploadedFile(fileName);
      const updatedFiles = files.filter((_, i) => i !== index);
      setFiles(updatedFiles);
      if (onFilesChange) {
        onFilesChange(updatedFiles);
      }
    } catch (error) {
      console.error(`Failed to delete ${fileName}:`, error);
      alert(`Failed to delete ${fileName}`);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="file-upload-container">
      {files.length > 0 && (
        <div className="uploaded-files">
          {files.map((file, index) => (
            <div key={index} className="file-chip">
              <span className="file-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
                  <polyline points="13 2 13 9 20 9"></polyline>
                </svg>
              </span>
              <span className="file-name">{file.name}</span>
              <span className="file-size">{formatFileSize(file.size)}</span>
              <button
                className="remove-file-btn"
                onClick={() => removeFile(index, file.name)}
                title="Remove file"
                disabled={uploading}
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}

      <div
        className={`file-drop-zone ${isDragging ? 'dragging' : ''} ${uploading ? 'uploading' : ''}`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={() => !uploading && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={handleFileInput}
          style={{ display: 'none' }}
          disabled={uploading}
        />
        <div className="drop-zone-content">
          <span className="upload-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
            </svg>
          </span>
          <span className="upload-text">
            {uploading ? 'Uploading...' : isDragging ? 'Drop files here' : 'Click or drag files to attach'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default FileUpload;
