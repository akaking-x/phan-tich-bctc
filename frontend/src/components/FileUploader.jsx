import { useState, useRef, useCallback } from "react";
import { UploadCloud, FileText, X, AlertCircle } from "lucide-react";

export default function FileUploader({ onFileSelect, disabled }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState("");
  const inputRef = useRef(null);

  const validateFile = useCallback((file) => {
    if (!file) return "Vui long chon file.";
    if (!file.name.toLowerCase().endsWith(".xml")) {
      return "Chi chap nhan file dinh dang .xml (xuat tu HTKK).";
    }
    if (file.size > 50 * 1024 * 1024) {
      return "File qua lon (toi da 50MB).";
    }
    return null;
  }, []);

  const handleFile = useCallback(
    (file) => {
      setError("");
      const validationError = validateFile(file);
      if (validationError) {
        setError(validationError);
        setSelectedFile(null);
        return;
      }
      setSelectedFile(file);
      if (onFileSelect) onFileSelect(file);
    },
    [validateFile, onFileSelect]
  );

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        handleFile(e.dataTransfer.files[0]);
      }
    },
    [handleFile]
  );

  const handleChange = useCallback(
    (e) => {
      if (e.target.files && e.target.files[0]) {
        handleFile(e.target.files[0]);
      }
    },
    [handleFile]
  );

  const handleRemove = useCallback(() => {
    setSelectedFile(null);
    setError("");
    if (inputRef.current) inputRef.current.value = "";
    if (onFileSelect) onFileSelect(null);
  }, [onFileSelect]);

  const formatSize = (bytes) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  return (
    <div className="w-full">
      {/* Drop zone */}
      <div
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={() => !disabled && inputRef.current?.click()}
        className={`relative border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all duration-200
          ${disabled ? "opacity-50 cursor-not-allowed" : ""}
          ${
            dragActive
              ? "border-indigo-400 bg-indigo-50"
              : selectedFile
                ? "border-emerald-300 bg-emerald-50"
                : "border-gray-300 bg-gray-50 hover:border-indigo-300 hover:bg-indigo-50/50"
          }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".xml"
          onChange={handleChange}
          disabled={disabled}
          className="hidden"
        />

        {selectedFile ? (
          <div className="flex flex-col items-center">
            <div className="w-14 h-14 bg-emerald-100 rounded-full flex items-center justify-center mb-3">
              <FileText className="w-7 h-7 text-emerald-600" />
            </div>
            <p className="text-base font-medium text-gray-800">
              {selectedFile.name}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              {formatSize(selectedFile.size)}
            </p>
            {!disabled && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleRemove();
                }}
                className="mt-3 flex items-center gap-1 text-sm text-red-500 hover:text-red-700 transition-colors"
              >
                <X className="w-4 h-4" />
                Xoa file
              </button>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <div
              className={`w-14 h-14 rounded-full flex items-center justify-center mb-3
              ${dragActive ? "bg-indigo-100" : "bg-gray-200"}`}
            >
              <UploadCloud
                className={`w-7 h-7 ${dragActive ? "text-indigo-600" : "text-gray-500"}`}
              />
            </div>
            <p className="text-base font-medium text-gray-700">
              {dragActive
                ? "Tha file vao day..."
                : "Keo & tha file XML vao day"}
            </p>
            <p className="text-sm text-gray-400 mt-1">
              hoac{" "}
              <span className="text-indigo-600 font-medium">
                nhan de chon file
              </span>
            </p>
            <p className="text-xs text-gray-400 mt-3">
              Chi chap nhan file .xml xuat tu phan mem HTKK (Toi da 50MB)
            </p>
          </div>
        )}
      </div>

      {/* Error message */}
      {error && (
        <div className="mt-3 flex items-center gap-2 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-4 py-2.5">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
