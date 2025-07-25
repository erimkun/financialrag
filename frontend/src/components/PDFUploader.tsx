import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X, CheckCircle, AlertCircle } from 'lucide-react';

interface UploadedDocument {
  id: string;
  filename: string;
  size: number;
  status: 'uploading' | 'completed' | 'error';
  message?: string;
}

interface PDFUploaderProps {
  onUploadComplete?: (document: UploadedDocument) => void;
  className?: string;
}

export const PDFUploader: React.FC<PDFUploaderProps> = ({ 
  onUploadComplete, 
  className = '' 
}) => {
  const [uploadedDocuments, setUploadedDocuments] = useState<UploadedDocument[]>([]);
  const [isUploading, setIsUploading] = useState(false);

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
    }
  }, []);

  const uploadFile = async (file: File) => {
    const tempDoc: UploadedDocument = {
      id: `temp-${Date.now()}`,
      filename: file.name,
      size: file.size,
      status: 'uploading'
    };

    setUploadedDocuments(prev => [...prev, tempDoc]);
    setIsUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/api/upload-pdf', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const result = await response.json();
      
      const uploadedDoc: UploadedDocument = {
        id: result.document_id,
        filename: result.filename,
        size: result.size,
        status: 'completed',
        message: result.message
      };

      setUploadedDocuments(prev => 
        prev.map(doc => 
          doc.id === tempDoc.id ? uploadedDoc : doc
        )
      );

      onUploadComplete?.(uploadedDoc);

    } catch (error) {
      console.error('Upload error:', error);
      
      setUploadedDocuments(prev =>
        prev.map(doc =>
          doc.id === tempDoc.id
            ? { ...doc, status: 'error', message: error instanceof Error ? error.message : 'Upload failed' }
            : doc
        )
      );
    } finally {
      setIsUploading(false);
    }
  };

  const removeDocument = (id: string) => {
    setUploadedDocuments(prev => prev.filter(doc => doc.id !== id));
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: true,
    disabled: isUploading
  });

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Upload Zone */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200
          ${isDragActive 
            ? 'border-red-500 bg-red-50 dark:bg-red-900/20' 
            : 'border-gray-300 dark:border-gray-600 hover:border-red-400 dark:hover:border-red-500'
          }
          ${isUploading ? 'cursor-not-allowed opacity-50' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center space-y-4">
          <Upload 
            size={48} 
            className={`${isDragActive ? 'text-red-500' : 'text-gray-400 dark:text-gray-500'}`} 
          />
          
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              {isDragActive ? 'PDF dosyasını buraya bırakın' : 'PDF Dosyası Yükleyin'}
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Dosyaları sürükleyip bırakın veya seçmek için tıklayın
            </p>
            <div className="flex flex-wrap justify-center gap-2 text-xs text-gray-500 dark:text-gray-400">
              <span className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                PDF formatı
              </span>
              <span className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                Maksimum 50MB
              </span>
              <span className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                Çoklu dosya desteği
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Uploaded Documents List */}
      {uploadedDocuments.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-900 dark:text-white">
            Yüklenen Dosyalar ({uploadedDocuments.length})
          </h4>
          
          <div className="space-y-2">
            {uploadedDocuments.map((doc) => (
              <div
                key={doc.id}
                className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
              >
                <div className="flex items-center space-x-3 flex-1 min-w-0">
                  <FileText size={20} className="text-red-500 flex-shrink-0" />
                  
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {doc.filename}
                    </p>
                    <div className="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
                      <span>{formatFileSize(doc.size)}</span>
                      {doc.message && (
                        <>
                          <span>•</span>
                          <span className="truncate">{doc.message}</span>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-2 flex-shrink-0">
                  {/* Status Icon */}
                  {doc.status === 'uploading' && (
                    <div className="animate-spin w-4 h-4 border-2 border-red-500 border-t-transparent rounded-full"></div>
                  )}
                  {doc.status === 'completed' && (
                    <CheckCircle size={16} className="text-green-500" />
                  )}
                  {doc.status === 'error' && (
                    <AlertCircle size={16} className="text-red-500" />
                  )}

                  {/* Remove Button */}
                  <button
                    onClick={() => removeDocument(doc.id)}
                    className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                    disabled={doc.status === 'uploading'}
                  >
                    <X size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upload Status */}
      {isUploading && (
        <div className="flex items-center justify-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
          <div className="animate-spin w-4 h-4 border-2 border-red-500 border-t-transparent rounded-full"></div>
          <span>Dosya yükleniyor...</span>
        </div>
      )}
    </div>
  );
};

export default PDFUploader;
