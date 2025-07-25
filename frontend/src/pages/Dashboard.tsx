import React, { useState } from 'react';
import PDFUploader from '../components/PDFUploader';
import ChatInterface from '../components/ChatInterface';
import DocumentViewer from '../components/DocumentViewer';
import { FileText, MessageSquare, Upload, BarChart3 } from 'lucide-react';

interface Document {
  id: string;
  filename: string;
  size: number;
  pages: number;
  processed_at: string;
  status: string;
}

type ActiveTab = 'chat' | 'upload' | 'documents' | 'analytics';

export const Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('chat');
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);

  const tabs = [
    { id: 'chat' as ActiveTab, label: 'Sohbet', icon: MessageSquare },
    { id: 'upload' as ActiveTab, label: 'Yükle', icon: Upload },
    { id: 'documents' as ActiveTab, label: 'Dokümanlar', icon: FileText },
    { id: 'analytics' as ActiveTab, label: 'Analitik', icon: BarChart3 }
  ];

  const handleUploadComplete = (document: any) => {
    // Switch to documents tab after successful upload
    setActiveTab('documents');
    // Optionally select the newly uploaded document
    setSelectedDocument(document);
  };

  const handleDocumentSelect = (document: Document) => {
    setSelectedDocument(document);
    // Switch to chat tab when a document is selected
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
    <div className="h-screen flex flex-col bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 dark:from-gray-900 dark:via-purple-900/20 dark:to-blue-900/20 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-purple-400/30 to-pink-400/30 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-br from-blue-400/30 to-cyan-400/30 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-br from-indigo-400/20 to-purple-400/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '4s' }}></div>
      </div>

      {/* Header */}
      <header className="relative z-10 flex-shrink-0 bg-white/70 dark:bg-gray-900/70 backdrop-blur-xl shadow-2xl border-b border-white/20 dark:border-gray-700/20">
        <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-10">
          <div className="flex items-center justify-between h-20">
            <div className="flex items-center space-x-4">
              <div className="relative">
                <div className="w-12 h-12 bg-gradient-to-br from-purple-500 via-pink-500 to-blue-500 rounded-2xl flex items-center justify-center shadow-2xl shadow-purple-500/25 animate-pulse">
                  <FileText className="w-7 h-7 text-white" />
                </div>
                <div className="absolute -inset-1 bg-gradient-to-br from-purple-500 via-pink-500 to-blue-500 rounded-2xl blur opacity-30 animate-pulse"></div>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 bg-clip-text text-transparent">
                  Turkish Financial RAG
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-300 font-medium">
                  ✨ AI-powered financial document analysis
                </p>
              </div>
            </div>

            {/* Status Indicator */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3 px-4 py-2 bg-gradient-to-r from-green-400/20 to-emerald-400/20 backdrop-blur-sm rounded-2xl border border-green-300/30 dark:border-green-400/30 shadow-lg">
                <div className="relative">
                  <div className="w-3 h-3 bg-gradient-to-r from-green-400 to-emerald-400 rounded-full shadow-lg shadow-green-400/50"></div>
                  <div className="absolute inset-0 w-3 h-3 bg-gradient-to-r from-green-400 to-emerald-400 rounded-full animate-ping opacity-75"></div>
                </div>
                <span className="text-sm font-semibold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">Sistem Aktif</span>
              </div>
              {selectedDocument && (
                <div className="hidden sm:flex items-center space-x-3 px-4 py-2 bg-gradient-to-r from-purple-400/20 to-pink-400/20 backdrop-blur-sm rounded-2xl border border-purple-300/30 dark:border-purple-400/30 shadow-lg">
                  <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center shadow-lg">
                    <FileText className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-sm font-semibold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent truncate max-w-32">
                    {selectedDocument.filename}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="relative z-10 flex-1 flex overflow-hidden">
        {/* Sidebar Navigation */}
        <nav className="w-72 bg-white/60 dark:bg-gray-900/60 backdrop-blur-2xl shadow-2xl border-r border-white/20 dark:border-gray-700/20 flex-shrink-0">
          <div className="p-8">
            <div className="mb-8">
              <h3 className="text-lg font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 bg-clip-text text-transparent mb-2">
                🚀 Menü
              </h3>
              <div className="w-12 h-1 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"></div>
            </div>
            <div className="space-y-3">
              {tabs.map((tab, index) => {
                const Icon = tab.icon;
                const gradients = [
                  'from-blue-500 to-cyan-500',
                  'from-purple-500 to-pink-500', 
                  'from-green-500 to-emerald-500',
                  'from-orange-500 to-red-500'
                ];
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full group relative overflow-hidden px-6 py-4 rounded-2xl text-left transition-all duration-300 hover:scale-105 ${
                      activeTab === tab.id
                        ? `bg-gradient-to-r ${gradients[index]} text-white shadow-2xl shadow-${gradients[index].split('-')[1]}-500/30`
                        : 'text-gray-700 dark:text-gray-300 hover:bg-white/40 dark:hover:bg-gray-800/40 backdrop-blur-sm'
                    }`}
                  >
                    <div className="flex items-center space-x-4 relative z-10">
                      <div className={`p-2 rounded-xl ${
                        activeTab === tab.id 
                          ? 'bg-white/20 backdrop-blur-sm' 
                          : `bg-gradient-to-r ${gradients[index]} text-white`
                      }`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <span className="font-semibold text-lg">{tab.label}</span>
                    </div>
                    {activeTab === tab.id && (
                      <div className="absolute inset-0 bg-gradient-to-r from-white/10 to-transparent backdrop-blur-sm"></div>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Document Selector in Sidebar */}
          {selectedDocument && (
            <div className="border-t border-white/20 dark:border-gray-700/20 p-8">
              <div className="mb-4">
                <h4 className="text-lg font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
                  📄 Aktif Doküman
                </h4>
                <div className="w-12 h-1 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"></div>
              </div>
              <div className="relative overflow-hidden p-6 bg-gradient-to-br from-white/50 to-purple-50/50 dark:from-gray-800/50 dark:to-purple-900/20 rounded-2xl border border-white/30 dark:border-gray-600/30 shadow-xl backdrop-blur-sm">
                <div className="flex items-center space-x-4">
                  <div className="relative">
                    <div className="w-12 h-12 bg-gradient-to-br from-purple-500 via-pink-500 to-blue-500 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/25">
                      <FileText className="w-6 h-6 text-white" />
                    </div>
                    <div className="absolute -inset-1 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl blur opacity-20"></div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-bold text-gray-900 dark:text-white truncate mb-1">
                      {selectedDocument.filename}
                    </p>
                    <p className="text-xs text-gray-600 dark:text-gray-400 flex items-center">
                      <span className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></span>
                      {selectedDocument.pages > 0 ? `${selectedDocument.pages} sayfa` : 'İşlendi'}
                    </p>
                  </div>
                </div>
                <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-purple-400/20 to-pink-400/20 rounded-full blur-xl transform translate-x-6 -translate-y-6"></div>
              </div>
            </div>
          )}
        </nav>

        {/* Main Content Area */}
        <main className="flex-1 overflow-hidden bg-white/30 dark:bg-gray-900/30 backdrop-blur-sm relative">
          <div className="absolute inset-0 bg-gradient-to-br from-transparent via-white/5 to-purple-50/20 dark:via-gray-800/5 dark:to-purple-900/10"></div>
          
          {activeTab === 'chat' && (
            <div className="relative z-10 h-full">
              <ChatInterface className="h-full" />
            </div>
          )}
          
          {activeTab === 'upload' && (
            <div className="relative z-10 h-full overflow-y-auto">
              <div className="max-w-4xl mx-auto p-12">
                <div className="text-center mb-12">
                  <div className="relative mb-8">
                    <div className="w-24 h-24 bg-gradient-to-br from-purple-500 via-pink-500 to-blue-500 rounded-3xl flex items-center justify-center mx-auto shadow-2xl shadow-purple-500/30 animate-pulse">
                      <Upload className="w-12 h-12 text-white" />
                    </div>
                    <div className="absolute -inset-2 bg-gradient-to-br from-purple-500 to-pink-500 rounded-3xl blur-xl opacity-30 animate-pulse"></div>
                  </div>
                  <h2 className="text-4xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 bg-clip-text text-transparent mb-4">
                    📁 PDF Dosyası Yükle
                  </h2>
                  <p className="text-gray-600 dark:text-gray-300 text-xl font-medium">
                    ✨ Türkçe finansal dokümanlarınızı yükleyerek AI analizi başlatın
                  </p>
                </div>
                
                <PDFUploader 
                  onUploadComplete={handleUploadComplete}
                  className="mb-12"
                />

                {/* Upload Instructions */}
                <div className="relative overflow-hidden bg-gradient-to-br from-blue-50/80 via-purple-50/80 to-pink-50/80 dark:from-blue-900/20 dark:via-purple-900/20 dark:to-pink-900/20 rounded-3xl p-8 border border-blue-200/50 dark:border-blue-700/50 shadow-2xl backdrop-blur-sm">
                  <div className="flex items-center mb-6">
                    <div className="relative">
                      <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/25">
                        <FileText className="w-6 h-6 text-white" />
                      </div>
                      <div className="absolute -inset-1 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl blur opacity-20"></div>
                    </div>
                    <h3 className="ml-4 text-xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                      📊 Desteklenen Doküman Türleri
                    </h3>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {[
                      { text: 'BIST-100 günlük bültenler', emoji: '📈' },
                      { text: 'Ekonomik analiz raporları', emoji: '📊' },
                      { text: 'Şirket mali tabloları', emoji: '💼' },
                      { text: 'VİOP piyasa raporları', emoji: '📋' },
                      { text: 'Merkez Bankası yayınları', emoji: '🏦' },
                      { text: 'Finansal performans raporları', emoji: '📈' }
                    ].map((item, index) => (
                      <div key={index} className="flex items-center space-x-3 p-3 bg-white/50 dark:bg-gray-800/50 rounded-xl backdrop-blur-sm border border-white/30 dark:border-gray-600/30">
                        <span className="text-2xl">{item.emoji}</span>
                        <span className="text-sm font-medium text-blue-800 dark:text-blue-200">{item.text}</span>
                      </div>
                    ))}
                  </div>
                  <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-400/20 to-cyan-400/20 rounded-full blur-2xl"></div>
                </div>
              </div>
            </div>
          )}
          
          {activeTab === 'documents' && (
            <div className="relative z-10 h-full">
              <DocumentViewer
                className="h-full overflow-y-auto"
                selectedDocument={selectedDocument}
                onDocumentSelect={handleDocumentSelect}
                onDocumentDelete={handleDocumentDelete}
              />
            </div>
          )}
          
          {activeTab === 'analytics' && (
            <div className="relative z-10 h-full overflow-y-auto p-12">
              <div className="max-w-7xl mx-auto">
                <div className="text-center mb-12">
                  <div className="relative mb-8">
                    <div className="w-24 h-24 bg-gradient-to-br from-green-500 via-emerald-500 to-teal-500 rounded-3xl flex items-center justify-center mx-auto shadow-2xl shadow-green-500/30 animate-pulse">
                      <BarChart3 className="w-12 h-12 text-white" />
                    </div>
                    <div className="absolute -inset-2 bg-gradient-to-br from-green-500 to-emerald-500 rounded-3xl blur-xl opacity-30 animate-pulse"></div>
                  </div>
                  <h2 className="text-4xl font-bold bg-gradient-to-r from-green-600 via-emerald-600 to-teal-600 bg-clip-text text-transparent mb-4">
                    📊 Sistem Analitikleri
                  </h2>
                  <p className="text-gray-600 dark:text-gray-300 text-xl font-medium">
                    ⚡ AI sisteminin performans metrikleri ve detaylı istatistikleri
                  </p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
                  {/* Stats Cards */}
                  <div className="relative overflow-hidden bg-white/60 dark:bg-gray-900/60 backdrop-blur-2xl rounded-3xl shadow-2xl p-8 border border-white/20 dark:border-gray-700/20 hover:scale-105 transition-all duration-300 group">
                    <div className="flex items-center">
                      <div className="relative">
                        <div className="w-16 h-16 bg-gradient-to-br from-purple-500 via-pink-500 to-red-500 rounded-2xl flex items-center justify-center shadow-xl shadow-purple-500/25">
                          <FileText className="w-8 h-8 text-white" />
                        </div>
                        <div className="absolute -inset-1 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl blur opacity-30 group-hover:opacity-50 transition-opacity"></div>
                      </div>
                      <div className="ml-6">
                        <p className="text-sm font-bold text-gray-600 dark:text-gray-300 mb-2">
                          📁 Toplam Doküman
                        </p>
                        <p className="text-4xl font-bold bg-gradient-to-r from-purple-500 via-pink-500 to-red-500 bg-clip-text text-transparent">
                          12
                        </p>
                      </div>
                    </div>
                    <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-purple-400/20 to-pink-400/20 rounded-full blur-2xl"></div>
                  </div>

                  <div className="relative overflow-hidden bg-white/60 dark:bg-gray-900/60 backdrop-blur-2xl rounded-3xl shadow-2xl p-8 border border-white/20 dark:border-gray-700/20 hover:scale-105 transition-all duration-300 group">
                    <div className="flex items-center">
                      <div className="relative">
                        <div className="w-16 h-16 bg-gradient-to-br from-blue-500 via-cyan-500 to-teal-500 rounded-2xl flex items-center justify-center shadow-xl shadow-blue-500/25">
                          <MessageSquare className="w-8 h-8 text-white" />
                        </div>
                        <div className="absolute -inset-1 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl blur opacity-30 group-hover:opacity-50 transition-opacity"></div>
                      </div>
                      <div className="ml-6">
                        <p className="text-sm font-bold text-gray-600 dark:text-gray-300 mb-2">
                          💬 Toplam Soru
                        </p>
                        <p className="text-4xl font-bold bg-gradient-to-r from-blue-500 via-cyan-500 to-teal-500 bg-clip-text text-transparent">
                          45
                        </p>
                      </div>
                    </div>
                    <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-blue-400/20 to-cyan-400/20 rounded-full blur-2xl"></div>
                  </div>

                  <div className="relative overflow-hidden bg-white/60 dark:bg-gray-900/60 backdrop-blur-2xl rounded-3xl shadow-2xl p-8 border border-white/20 dark:border-gray-700/20 hover:scale-105 transition-all duration-300 group">
                    <div className="flex items-center">
                      <div className="relative">
                        <div className="w-16 h-16 bg-gradient-to-br from-green-500 via-emerald-500 to-lime-500 rounded-2xl flex items-center justify-center shadow-xl shadow-green-500/25">
                          <BarChart3 className="w-8 h-8 text-white" />
                        </div>
                        <div className="absolute -inset-1 bg-gradient-to-br from-green-500 to-emerald-500 rounded-2xl blur opacity-30 group-hover:opacity-50 transition-opacity"></div>
                      </div>
                      <div className="ml-6">
                        <p className="text-sm font-bold text-gray-600 dark:text-gray-300 mb-2">
                          🎯 Ortalama Güven
                        </p>
                        <p className="text-4xl font-bold bg-gradient-to-r from-green-500 via-emerald-500 to-lime-500 bg-clip-text text-transparent">
                          93.7%
                        </p>
                      </div>
                    </div>
                    <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-green-400/20 to-emerald-400/20 rounded-full blur-2xl"></div>
                  </div>
                </div>

                {/* Performance Metrics */}
                <div className="relative overflow-hidden bg-white/60 dark:bg-gray-900/60 backdrop-blur-2xl rounded-3xl shadow-2xl p-10 border border-white/20 dark:border-gray-700/20">
                  <div className="flex items-center mb-8">
                    <div className="relative">
                      <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 rounded-2xl flex items-center justify-center shadow-lg shadow-indigo-500/25">
                        <BarChart3 className="w-6 h-6 text-white" />
                      </div>
                      <div className="absolute -inset-1 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-2xl blur opacity-20"></div>
                    </div>
                    <h3 className="ml-4 text-2xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                      ⚡ Sistem Performansı
                    </h3>
                  </div>
                  <div className="space-y-8">
                    <div>
                      <div className="flex justify-between items-center mb-4">
                        <span className="text-lg font-bold text-gray-700 dark:text-gray-200">🚀 Ortalama Yanıt Süresi</span>
                        <span className="text-xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">1.28s</span>
                      </div>
                      <div className="relative w-full h-4 bg-gray-200 dark:bg-gray-700 rounded-full shadow-inner overflow-hidden">
                        <div className="absolute inset-0 bg-gradient-to-r from-green-400 via-emerald-400 to-green-500 h-full rounded-full shadow-lg animate-pulse" style={{ width: '85%' }}></div>
                        <div className="absolute inset-0 bg-gradient-to-r from-green-400/30 to-emerald-400/30 h-full rounded-full blur animate-pulse" style={{ width: '85%' }}></div>
                      </div>
                    </div>
                    
                    <div>
                      <div className="flex justify-between items-center mb-4">
                        <span className="text-lg font-bold text-gray-700 dark:text-gray-200">✅ Başarı Oranı</span>
                        <span className="text-xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">100%</span>
                      </div>
                      <div className="relative w-full h-4 bg-gray-200 dark:bg-gray-700 rounded-full shadow-inner overflow-hidden">
                        <div className="absolute inset-0 bg-gradient-to-r from-green-400 via-emerald-400 to-green-500 h-full rounded-full shadow-lg animate-pulse" style={{ width: '100%' }}></div>
                        <div className="absolute inset-0 bg-gradient-to-r from-green-400/30 to-emerald-400/30 h-full rounded-full blur animate-pulse" style={{ width: '100%' }}></div>
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between items-center mb-4">
                        <span className="text-lg font-bold text-gray-700 dark:text-gray-200">😊 Kullanıcı Memnuniyeti</span>
                        <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">97%</span>
                      </div>
                      <div className="relative w-full h-4 bg-gray-200 dark:bg-gray-700 rounded-full shadow-inner overflow-hidden">
                        <div className="absolute inset-0 bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-500 h-full rounded-full shadow-lg animate-pulse" style={{ width: '97%' }}></div>
                        <div className="absolute inset-0 bg-gradient-to-r from-blue-400/30 to-cyan-400/30 h-full rounded-full blur animate-pulse" style={{ width: '97%' }}></div>
                      </div>
                    </div>
                  </div>
                  <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-indigo-400/20 to-purple-400/20 rounded-full blur-2xl"></div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default Dashboard;
