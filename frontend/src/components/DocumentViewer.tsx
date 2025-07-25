import React, { useState, useEffect } from 'react';
import { FileText, Download, Trash2, Calendar, FileIcon, BarChart3, Eye, EyeOff } from 'lucide-react';

interface Document {
  id: string;
  filename: string;
  size: number;
  pages: number;
  processed_at: string;
  status: string;
}

interface DocumentViewerProps {
  selectedDocument?: Document | null;
  onDocumentSelect?: (document: Document) => void;
  onDocumentDelete?: (documentId: string) => void;
  className?: string;
}

export const DocumentViewer: React.FC<DocumentViewerProps> = ({
  selectedDocument,
  onDocumentSelect,
  onDocumentDelete,
  className = ''
}) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [showPreview, setShowPreview] = useState(false);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/documents');
      if (response.ok) {
        const data = await response.json();
        setDocuments(data);
      }
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (documentId: string) => {
    if (!confirm('Bu dokümanı silmek istediğinizden emin misiniz?')) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/documents/${documentId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        setDocuments(prev => prev.filter(doc => doc.id !== documentId));
        onDocumentDelete?.(documentId);
        
        // If the deleted document was selected, clear selection
        if (selectedDocument?.id === documentId) {
          onDocumentSelect?.(null as any);
        }
      } else {
        throw new Error('Delete failed');
      }
    } catch (error) {
      console.error('Failed to delete document:', error);
      alert('Doküman silinirken bir hata oluştu.');
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('tr-TR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100 dark:bg-green-900/20';
      case 'processing': return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20';
      case 'failed': return 'text-red-600 bg-red-100 dark:bg-red-900/20';
      default: return 'text-gray-600 bg-gray-100 dark:bg-gray-900/20';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'completed': return 'Tamamlandı';
      case 'processing': return 'İşleniyor';
      case 'failed': return 'Başarısız';
      case 'uploaded': return 'Yüklendi';
      default: return status;
    }
  };

  if (loading) {
    return (
      <div className={`flex items-center justify-center h-64 ${className}`}>
        <div className="animate-spin w-8 h-8 border-2 border-red-500 border-t-transparent rounded-full"></div>
        <span className="ml-3 text-gray-600 dark:text-gray-400">Dokümanlar yükleniyor...</span>
      </div>
    );
  }

  return (
    <div className={`bg-white dark:bg-gray-900 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-2">
          <FileText className="w-5 h-5 text-red-500" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Dokümanlar ({documents.length})
          </h3>
        </div>
        
        <button
          onClick={() => setShowPreview(!showPreview)}
          className="flex items-center space-x-1 px-3 py-1 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
        >
          {showPreview ? <EyeOff size={16} /> : <Eye size={16} />}
          <span>{showPreview ? 'Önizlemeyi Gizle' : 'Önizleme'}</span>
        </button>
      </div>

      {/* Documents List */}
      <div className="p-4">
        {documents.length === 0 ? (
          <div className="text-center py-12">
            <FileIcon className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
            <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              Henüz doküman yok
            </h4>
            <p className="text-gray-600 dark:text-gray-400">
              PDF dosyalarınızı yükleyerek başlayın
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {documents.map((document) => (
              <div
                key={document.id}
                className={`border rounded-lg p-4 cursor-pointer transition-all duration-200 ${
                  selectedDocument?.id === document.id
                    ? 'border-red-500 bg-red-50 dark:bg-red-900/10'
                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                }`}
                onClick={() => onDocumentSelect?.(document)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    {/* Document Name & Status */}
                    <div className="flex items-center space-x-2 mb-2">
                      <FileText className="w-5 h-5 text-red-500 flex-shrink-0" />
                      <h4 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {document.filename}
                      </h4>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(document.status)}`}>
                        {getStatusLabel(document.status)}
                      </span>
                    </div>

                    {/* Document Details */}
                    <div className="flex flex-wrap items-center gap-4 text-xs text-gray-600 dark:text-gray-400">
                      <div className="flex items-center space-x-1">
                        <BarChart3 size={12} />
                        <span>{formatFileSize(document.size)}</span>
                      </div>
                      
                      {document.pages > 0 && (
                        <div className="flex items-center space-x-1">
                          <FileText size={12} />
                          <span>{document.pages} sayfa</span>
                        </div>
                      )}
                      
                      <div className="flex items-center space-x-1">
                        <Calendar size={12} />
                        <span>{formatDate(document.processed_at)}</span>
                      </div>
                    </div>

                    {/* Preview Panel */}
                    {showPreview && selectedDocument?.id === document.id && (
                      <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                        <h5 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                          Doküman Bilgileri
                        </h5>
                        <div className="space-y-1 text-xs text-gray-600 dark:text-gray-400">
                          <div><strong>ID:</strong> {document.id}</div>
                          <div><strong>Durum:</strong> {getStatusLabel(document.status)}</div>
                          <div><strong>İşlem Tarihi:</strong> {formatDate(document.processed_at)}</div>
                          {document.pages > 0 && (
                            <div><strong>Sayfa Sayısı:</strong> {document.pages}</div>
                          )}
                        </div>
                        
                        {/* Actions */}
                        <div className="flex space-x-2 mt-3">
                          <button
                            className="flex items-center space-x-1 px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 rounded hover:bg-blue-200 dark:hover:bg-blue-900/30 transition-colors"
                            onClick={(e) => {
                              e.stopPropagation();
                              // TODO: Implement download
                            }}
                          >
                            <Download size={12} />
                            <span>İndir</span>
                          </button>
                          
                          <button
                            className="flex items-center space-x-1 px-2 py-1 text-xs bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-300 rounded hover:bg-red-200 dark:hover:bg-red-900/30 transition-colors"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDelete(document.id);
                            }}
                          >
                            <Trash2 size={12} />
                            <span>Sil</span>
                          </button>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Quick Actions */}
                  <div className="flex items-center space-x-1 ml-2">
                    <button
                      className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(document.id);
                      }}
                      title="Dokümanı sil"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      {documents.length > 0 && (
        <div className="px-4 py-3 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
          <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
            <span>
              Toplam {documents.length} doküman
            </span>
            <span>
              {documents.filter(d => d.status === 'completed').length} tamamlandı
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentViewer;
