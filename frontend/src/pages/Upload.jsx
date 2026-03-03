import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import {
  Loader2,
  CheckCircle2,
  AlertCircle,
  FileText,
  Shield,
  BarChart3,
  BookOpen,
} from "lucide-react";
import FileUploader from "../components/FileUploader";

const API_BASE = import.meta.env.VITE_API_BASE || "";

export default function Upload({ onUploadSuccess, hasData }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setError("");
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setError("");
    setProgress("Dang tai file len...");

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      setProgress("Dang phan tich XML...");

      const response = await axios.post(`${API_BASE}/api/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 60000,
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percent = Math.round(
              (progressEvent.loaded / progressEvent.total) * 100
            );
            if (percent < 100) {
              setProgress(`Dang tai len... ${percent}%`);
            } else {
              setProgress("Dang phan tich bao cao tai chinh...");
            }
          }
        },
      });

      if (response.data && response.data.success) {
        setProgress("Hoan thanh! Dang chuyen den trang tong quan...");
        onUploadSuccess(response.data);
        setTimeout(() => navigate("/dashboard"), 500);
      } else {
        throw new Error(response.data?.detail || "Phan tich that bai.");
      }
    } catch (err) {
      let message = "Da xay ra loi khi phan tich file.";

      if (err.response) {
        if (err.response.status === 400) {
          message =
            err.response.data?.detail ||
            "File khong hop le. Vui long chon file XML tu HTKK.";
        } else if (err.response.status === 422) {
          message =
            "Cau truc file XML khong dung dinh dang. Hay dam bao file duoc xuat tu phan mem HTKK.";
        } else if (err.response.status === 500) {
          message =
            "Loi may chu. Vui long thu lai sau hoac kiem tra dinh dang file.";
        } else {
          message = err.response.data?.detail || message;
        }
      } else if (err.code === "ECONNABORTED") {
        message =
          "Het thoi gian xu ly. File co the qua lon hoac may chu khong phan hoi.";
      } else if (err.message === "Network Error") {
        message =
          "Khong the ket noi den may chu. Vui long dam bao Backend dang chay tai localhost:8000.";
      }

      setError(message);
    } finally {
      setUploading(false);
      setProgress("");
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      {/* Hero section */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-indigo-100 rounded-2xl mb-4">
          <FileText className="w-8 h-8 text-indigo-600" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900">
          Phan tich Bao cao Tai chinh
        </h1>
        <p className="text-gray-500 mt-2 text-sm max-w-md mx-auto">
          Tai len file XML xuat tu HTKK de tu dong doi chieu cheo, phat hien
          bat thuong va phan tich chi so tai chinh.
        </p>
      </div>

      {/* Upload card */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <FileUploader onFileSelect={handleFileSelect} disabled={uploading} />

        {/* Upload button */}
        <div className="mt-6 flex justify-center">
          <button
            onClick={handleUpload}
            disabled={!selectedFile || uploading}
            className="inline-flex items-center gap-2 px-8 py-3 bg-indigo-600 text-white rounded-xl
              text-sm font-semibold hover:bg-indigo-700 transition-all duration-200
              disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-indigo-600
              shadow-sm hover:shadow-md"
          >
            {uploading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                {progress || "Dang xu ly..."}
              </>
            ) : (
              <>
                <CheckCircle2 className="w-4 h-4" />
                Bat dau phan tich
              </>
            )}
          </button>
        </div>

        {/* Progress */}
        {uploading && (
          <div className="mt-4">
            <div className="flex items-center gap-2 justify-center text-sm text-indigo-600">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>{progress}</span>
            </div>
            <div className="mt-2 w-full bg-gray-200 rounded-full h-1.5">
              <div className="bg-indigo-600 h-1.5 rounded-full animate-pulse w-2/3" />
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mt-4 flex items-start gap-2 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
            <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-red-800">
                Khong the phan tich
              </p>
              <p className="text-sm text-red-600 mt-0.5">{error}</p>
            </div>
          </div>
        )}
      </div>

      {/* Go to dashboard if data exists */}
      {hasData && !uploading && (
        <div className="mt-6 text-center">
          <button
            onClick={() => navigate("/dashboard")}
            className="inline-flex items-center gap-2 text-sm text-indigo-600 hover:text-indigo-800 font-medium"
          >
            <CheckCircle2 className="w-4 h-4" />
            Xem ket qua phan tich truoc do
          </button>
        </div>
      )}

      {/* Features */}
      <div className="mt-10 grid grid-cols-1 sm:grid-cols-3 gap-4">
        <FeatureCard
          icon={Shield}
          title="Doi chieu cheo"
          desc="Tu dong doi chieu 4 bao cao: CDKT, KQHDKD, LCTT, CDTK."
        />
        <FeatureCard
          icon={BookOpen}
          title="Tai tao but toan"
          desc="Suy luan but toan goc tu bang can doi tai khoan."
        />
        <FeatureCard
          icon={BarChart3}
          title="Phan tich chi so"
          desc="Tinh toan chi so thanh khoan, sinh loi, don bay, hieu suat."
        />
      </div>
    </div>
  );
}

function FeatureCard({ icon: Icon, title, desc }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 text-center">
      <div className="inline-flex items-center justify-center w-10 h-10 bg-gray-100 rounded-lg mb-3">
        <Icon className="w-5 h-5 text-gray-600" />
      </div>
      <h3 className="text-sm font-semibold text-gray-800">{title}</h3>
      <p className="text-xs text-gray-500 mt-1">{desc}</p>
    </div>
  );
}
