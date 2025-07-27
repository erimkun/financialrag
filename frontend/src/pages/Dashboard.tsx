import React, { useState, useEffect } from 'react';
import PDFUploader from '../components/PDFUploader';
import ChatInterface from '../components/ChatInterface';
import DocumentViewer from '../components/DocumentViewer';
import { FileText, MessageSquare, Upload, BarChart3, Wifi, WifiOff } from 'lucide-react';
import { useAppStore, useDocuments, useSelectedDocument, useConnectionStatus } from '../lib/store';

type ActiveTab = 'chat' | 'upload' | 'documents' | 'analytics';

export const Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('chat');
  
  // Store hooks
  const documents = useDocuments();
  const selectedDocument = useSelectedDocument();
  const isConnected = useConnectionStatus();
  const setSelectedDocument = useAppStore(state => state.setSelectedDocument);
  const loadDocuments = useAppStore(state => state.loadDocuments);
  const checkConnection = useAppStore(state => state.checkConnection);

  // Load documents and check connection on mount
  useEffect(() => {
    loadDocuments();
    checkConnection();
  }, [loadDocuments, checkConnection]);

  const tabs = [
    { id: 'chat' as ActiveTab, label: 'Sohbet', icon: MessageSquare },
    { id: 'upload' as ActiveTab, label: 'Yükle', icon: Upload },
    { id: 'documents' as ActiveTab, label: 'Dokümanlar', icon: FileText },
    { id: 'analytics' as ActiveTab, label: 'Analitik', icon: BarChart3 }
  ];

  const handleUploadComplete = () => {
    setActiveTab('documents');
  };

  const handleDocumentSelect = (document: any) => {
    setSelectedDocument(document);
    if (activeTab !== 'chat') {
      setActiveTab('chat');
    }
  };

  const handleDocumentDelete = (documentId: string) => {
    if (selectedDocument?.id === documentId) {
      setSelectedDocument(null);
    }
  };

  return (
    <div 
      className="min-h-screen bg-slate-50 dark:bg-slate-900"
      style={{
        minHeight: '100vh',
        backgroundColor: '#f8fafc',
        fontFamily: 'system-ui, -apple-system, sans-serif'
      }}
    >
        {/* Header */}
        <header 
          className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 shadow-sm"
          style={{
            backgroundColor: 'white',
            borderBottom: '1px solid #e2e8f0',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
          }}
        >
          <div 
            className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8"
            style={{
              maxWidth: '80rem',
              margin: '0 auto',
              padding: '0 1rem'
            }}
          >
            <div 
              className="flex items-center justify-between h-16"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                height: '4rem'
              }}
            >
              <div 
                className="flex items-center space-x-4"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '1rem'
                }}
              >
                <div 
                  className="flex items-center justify-center w-10 h-10 bg-blue-600 rounded-lg shadow-lg"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    width: '2.5rem',
                    height: '2.5rem',
                    backgroundColor: '#2563eb',
                    borderRadius: '0.5rem',
                    boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
                  }}
                >
                  <FileText className="w-6 h-6 text-white" style={{ color: 'white' }} />
                </div>
                <div>
                  <h1 
                    className="text-xl font-bold text-slate-900 dark:text-white"
                    style={{
                      fontSize: '1.25rem',
                      fontWeight: 'bold',
                      color: '#0f172a',
                      margin: 0
                    }}
                  >
                    Turkish Financial AI Assistant
                  </h1>
                  <p 
                    className="text-sm text-slate-600 dark:text-slate-400"
                    style={{
                      fontSize: '0.875rem',
                      color: '#475569',
                      margin: 0
                    }}
                  >
                    AI destekli finansal doküman analizi
                  </p>
                </div>
              </div>

              <div 
                className="flex items-center space-x-4"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '1rem'
                }}
              >
                <div 
                  className="flex items-center space-x-2 px-3 py-1.5 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400 rounded-full text-sm font-medium"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    padding: '0.375rem 0.75rem',
                    backgroundColor: '#dcfce7',
                    color: '#166534',
                    borderRadius: '9999px',
                    fontSize: '0.875rem',
                    fontWeight: '500'
                  }}
                >
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" style={{
                    width: '0.5rem',
                    height: '0.5rem',
                    backgroundColor: '#22c55e',
                    borderRadius: '9999px'
                  }}></div>
                  <span>Sistem Aktif</span>
                </div>
                {selectedDocument && (
                  <div 
                    className="flex items-center space-x-2 px-3 py-1.5 bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg text-sm"
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      padding: '0.375rem 0.75rem',
                      backgroundColor: '#f1f5f9',
                      color: '#334155',
                      borderRadius: '0.5rem',
                      fontSize: '0.875rem'
                    }}
                  >
                    <FileText className="w-4 h-4" />
                    <span className="truncate max-w-32" style={{ maxWidth: '8rem' }}>
                      {selectedDocument.filename}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Main Layout */}
        <div 
          className="flex h-[calc(100vh-4rem)]"
          style={{
            display: 'flex',
            height: 'calc(100vh - 4rem)'
          }}
        >
          {/* Sidebar */}
          <aside 
            className="w-64 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700"
            style={{
              width: '16rem',
              backgroundColor: 'white',
              borderRight: '1px solid #e2e8f0'
            }}
          >
            <nav 
              className="p-4 space-y-2"
              style={{
                padding: '1rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.5rem'
              }}
            >
              {tabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`
                      w-full flex items-center space-x-3 px-4 py-3 text-left rounded-lg transition-all duration-200 font-medium
                      ${isActive 
                        ? 'bg-blue-600 text-white shadow-lg transform scale-[1.02]' 
                        : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 hover:text-slate-900 dark:hover:text-white'
                      }
                    `}
                    style={{
                      width: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.75rem',
                      padding: '0.75rem 1rem',
                      textAlign: 'left',
                      borderRadius: '0.5rem',
                      transition: 'all 0.2s',
                      fontWeight: '500',
                      backgroundColor: isActive ? '#2563eb' : 'transparent',
                      color: isActive ? 'white' : '#334155',
                      border: 'none',
                      cursor: 'pointer'
                    }}
                    onMouseEnter={(e) => {
                      if (!isActive) {
                        e.currentTarget.style.backgroundColor = '#f1f5f9';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (!isActive) {
                        e.currentTarget.style.backgroundColor = 'transparent';
                      }
                    }}
                  >
                    <Icon className="w-5 h-5" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </nav>
          </aside>

          {/* Main Content */}
          <main 
            className="flex-1 overflow-auto bg-slate-50 dark:bg-slate-900"
            style={{
              flex: 1,
              overflow: 'auto',
              backgroundColor: '#f8fafc'
            }}
          >
          {activeTab === 'chat' && (
            <div className="h-full p-6">
              <ChatInterface />
            </div>
          )}

          {activeTab === 'upload' && (
            <div className="p-6">
              <div className="max-w-4xl mx-auto">
                <div className="mb-8">
                  <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
                    Doküman Yükle
                  </h2>
                  <p className="text-slate-600 dark:text-slate-400">
                    PDF dosyalarınızı yükleyerek AI destekli analiz başlatın
                  </p>
                </div>
                <PDFUploader onUploadComplete={handleUploadComplete} />
              </div>
            </div>
          )}

          {activeTab === 'documents' && (
            <div className="p-6">
              <div className="max-w-6xl mx-auto">
                <div className="mb-8">
                  <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
                    Dokümanlar
                  </h2>
                  <p className="text-slate-600 dark:text-slate-400">
                    Yüklediğiniz dokümanları görüntüleyin ve yönetin
                  </p>
                </div>
                <DocumentViewer 
                  onDocumentSelect={handleDocumentSelect}
                  onDocumentDelete={handleDocumentDelete}
                />
              </div>
            </div>
          )}

          {activeTab === 'analytics' && (
            <div className="flex items-center justify-center h-full p-6">
              <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-8 text-center max-w-md border border-slate-200 dark:border-slate-700">
                <div className="w-16 h-16 bg-slate-100 dark:bg-slate-700 rounded-full flex items-center justify-center mx-auto mb-6">
                  <BarChart3 className="w-8 h-8 text-slate-600 dark:text-slate-400" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-3">
                  Analitik Panosu
                </h3>
                <p className="text-slate-600 dark:text-slate-400 mb-6">
                  Detaylı finansal analiz ve görselleştirme araçları yakında eklenecek.
                </p>
                <button className="px-6 py-2.5 bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded-lg font-medium hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors">
                  Yakında Gelecek
                </button>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default Dashboard;
