import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { useAppStore, useUploadStatus, useDocuments } from '../lib/store';

interface PDFUploaderProps {
  onUploadComplete?: (document: any) => void;
  className?: string;
}

export const PDFUploader: React.FC<PDFUploaderProps> = ({ 
  onUploadComplete, 
  className = '' 
}) => {
  const uploadFile = useAppStore(state => state.uploadFile);
  const uploadStatus = useUploadStatus();
  const documents = useDocuments();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const pdfFiles = acceptedFiles.filter(file => 
      file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
    );

    if (pdfFiles.length === 0) {
      alert('Lütfen sadece PDF dosyaları yükleyin.');
      return;
    }

    for (const file of pdfFiles) {
      await uploadFile(file);
      onUploadComplete?.(file);
    }
  }, [uploadFile, onUploadComplete]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: true,
    disabled: uploadStatus.isUploading
  });

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getRecentDocuments = () => {
    return documents.slice(-3).reverse(); // Son 3 dökümanı göster
  };

  return (
    <div className={`w-full max-w-4xl mx-auto ${className}`}>
      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed border-gray-300 dark:border-gray-600 
          rounded-lg p-8 text-center cursor-pointer transition-all duration-200
          hover:border-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20
          ${isDragActive ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/20' : ''}
          ${uploadStatus.isUploading ? 'cursor-not-allowed opacity-50' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center justify-center space-y-4">
          {uploadStatus.isUploading ? (
            <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
          ) : (
            <Upload className="w-12 h-12 text-gray-400" />
          )}
          
          <div>
            <p className="text-lg font-medium text-gray-900 dark:text-gray-100">
              {uploadStatus.isUploading 
                ? 'Yükleniyor...' 
                : isDragActive 
                  ? 'Dosyaları buraya bırakın'
                  : 'PDF dosyalarını sürükleyin veya seçin'
              }
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Desteklenen format: PDF • Maksimum boyut: 50MB
            </p>
          </div>
        </div>

        {/* Progress Bar */}
        {uploadStatus.isUploading && (
          <div className="mt-4">
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div 
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadStatus.progress}%` }}
              />
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
              %{uploadStatus.progress} tamamlandı
            </p>
          </div>
        )}

        {/* Error Message */}
        {uploadStatus.error && (
          <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-red-500" />
              <p className="text-sm text-red-700 dark:text-red-300">
                {uploadStatus.error}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Recent Documents */}
      {documents.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-3">
            Son Yüklenen Dosyalar ({documents.length})
          </h3>
          <div className="space-y-2">
            {getRecentDocuments().map((doc) => (
              <div
                key={doc.id}
                className="flex items-center justify-between p-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <FileText className="w-5 h-5 text-blue-500" />
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {doc.filename}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      {formatFileSize(doc.size)} • {doc.pages || 0} sayfa
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  {doc.status === 'completed' && (
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  )}
                  {doc.status === 'processing' && (
                    <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
                  )}
                  {doc.status === 'error' && (
                    <AlertCircle className="w-4 h-4 text-red-500" />
                  )}
                  <span className={`
                    text-xs px-2 py-1 rounded-full font-medium
                    ${doc.status === 'completed' ? 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-300' : ''}
                    ${doc.status === 'processing' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300' : ''}
                    ${doc.status === 'error' ? 'bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-300' : ''}
                  `}>
                    {doc.status === 'completed' ? 'Tamamlandı' : ''}
                    {doc.status === 'processing' ? 'İşleniyor' : ''}
                    {doc.status === 'error' ? 'Hata' : ''}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upload Tips */}
      <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
        <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-2">
          💡 İpuçları:
        </h4>
        <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
          <li>• Finansal raporlar, analiz belgeleri ve teknik dökümanlar desteklenir</li>
          <li>• Türkçe içerik daha iyi analiz edilir</li>
          <li>• Çok sayfalı dosyalar otomatik olarak parçalara ayrılır</li>
          <li>• Yüklenen dosyalar analiz edilip sohbet için hazır hale getirilir</li>
        </ul>
      </div>
    </div>
  );
};

export default PDFUploader;
