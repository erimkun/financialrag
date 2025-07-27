import React, { useRef, useEffect } from 'react';
import { Send, Bot, User, Clock, TrendingUp, AlertCircle, Copy, ThumbsUp, ThumbsDown, Loader2 } from 'lucide-react';
import { useAppStore, useMessages, useSelectedDocument } from '../lib/store';
import type { Message } from '../lib/store';

interface ChatInterfaceProps {
  className?: string;
  suggestions?: string[];
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ 
  className = '', 
  suggestions = [
    "BIST-100 için teknik yorum nedir?",
    "Hangi hisse senetleri en yüksek getiri sağladı?",
    "Banka hisseleri nasıl performans gösterdi?",
    "VİOP kontratları hakkında ne söyleniyor?",
    "Ekonomik göstergeler nasıl?"
  ]
}) => {
  const messages = useMessages();
  const selectedDocument = useSelectedDocument();
  const sendMessage = useAppStore(state => state.sendMessage);
  const isLoadingResponse = useAppStore(state => state.isLoadingResponse);
  
  const [input, setInput] = React.useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (question?: string) => {
    const queryText = question || input.trim();
    if (!queryText || isLoadingResponse) return;

    setInput('');
    await sendMessage(queryText);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('tr-TR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatResponseTime = (ms?: number) => {
    if (!ms) return '';
    return ms < 1000 ? `${Math.round(ms)}ms` : `${(ms / 1000).toFixed(1)}s`;
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const getConfidenceColor = (confidence?: number) => {
    if (!confidence) return 'text-gray-500';
    if (confidence >= 0.8) return 'text-green-500';
    if (confidence >= 0.6) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getConfidenceLabel = (confidence?: number) => {
    if (!confidence) return 'Bilinmiyor';
    if (confidence >= 0.8) return 'Yüksek';
    if (confidence >= 0.6) return 'Orta';
    return 'Düşük';
  };

  return (
    <div className={`flex flex-col h-full bg-white dark:bg-gray-900 ${className}`}>
      {/* Header */}
      <div className="flex-shrink-0 p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Bot className="w-6 h-6 text-blue-500" />
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                Finansal Asistan
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {selectedDocument 
                  ? `Aktif: ${selectedDocument.filename}`
                  : 'Genel sorular için hazır'
                }
              </p>
            </div>
          </div>
          {isLoadingResponse && (
            <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-8">
            <Bot className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h4 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
              Merhaba! Size nasıl yardımcı olabilirim?
            </h4>
            <p className="text-gray-500 dark:text-gray-400 mb-6">
              Finansal raporlar hakkında sorular sorabilir veya aşağıdaki örnekleri deneyebilirsiniz:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto">
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSubmit(suggestion)}
                  disabled={isLoadingResponse}
                  className="p-3 text-left text-sm bg-gray-50 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-700 transition-colors duration-200 disabled:opacity-50 shadow-sm hover:shadow-md"
                >
                  <span className="text-gray-800 dark:text-gray-200">{suggestion}</span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex space-x-3 max-w-3xl ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                <div className="flex-shrink-0">
                  {message.type === 'user' ? (
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                      <User className="w-4 h-4 text-white" />
                    </div>
                  ) : (
                    <div className="w-8 h-8 bg-gray-500 rounded-full flex items-center justify-center">
                      <Bot className="w-4 h-4 text-white" />
                    </div>
                  )}
                </div>
                
                <div className={`flex-1 ${message.type === 'user' ? 'text-right' : ''}`}>
                  <div
                    className={`
                      p-3 rounded-lg
                      ${message.type === 'user' 
                        ? 'bg-blue-500 text-white' 
                        : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
                      }
                    `}
                  >
                    {message.isLoading ? (
                      <div className="flex items-center space-x-2">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Analiz ediliyor...</span>
                      </div>
                    ) : (
                      <div className="whitespace-pre-wrap">{message.content}</div>
                    )}
                  </div>
                  
                  <div className={`flex items-center space-x-4 mt-2 text-xs text-gray-500 dark:text-gray-400 ${message.type === 'user' ? 'justify-end' : ''}`}>
                    <span>{formatTime(message.timestamp)}</span>
                    
                    {message.type === 'assistant' && !message.isLoading && (
                      <>
                        {message.confidence && (
                          <span className={`flex items-center space-x-1 ${getConfidenceColor(message.confidence)}`}>
                            <TrendingUp className="w-3 h-3" />
                            <span>Güven: {getConfidenceLabel(message.confidence)} ({Math.round(message.confidence * 100)}%)</span>
                          </span>
                        )}
                        
                        {message.responseTime && (
                          <span className="flex items-center space-x-1">
                            <Clock className="w-3 h-3" />
                            <span>{formatResponseTime(message.responseTime)}</span>
                          </span>
                        )}
                        
                        <button
                          onClick={() => copyToClipboard(message.content)}
                          className="flex items-center space-x-1 hover:text-gray-700 dark:hover:text-gray-300"
                        >
                          <Copy className="w-3 h-3" />
                          <span>Kopyala</span>
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="flex-shrink-0 p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex space-x-3">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={
                selectedDocument
                  ? `${selectedDocument.filename} hakkında soru sorun...`
                  : "Finansal raporlar hakkında soru sorun..."
              }
              className="w-full p-3 pr-12 border border-gray-300 dark:border-gray-600 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-800 dark:text-gray-100"
              rows={3}
              disabled={isLoadingResponse}
            />
            <button
              onClick={() => handleSubmit()}
              disabled={!input.trim() || isLoadingResponse}
              className="absolute right-2 bottom-2 p-2 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 disabled:hover:bg-gray-300 text-white rounded-md transition-colors duration-200"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
        
        {!selectedDocument && (
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
            💡 İpucu: PDF yükleyerek belge-spesifik sorular sorabilirsiniz
          </p>
        )}

        {/* Quick Suggestions - Always visible */}
        <div className="mt-3">
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">💡 Hızlı sorular:</p>
          <div className="flex flex-wrap gap-2">
            {suggestions.slice(0, 3).map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSubmit(suggestion)}
                disabled={isLoadingResponse}
                className="px-3 py-1 text-xs bg-blue-50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-900/40 text-blue-700 dark:text-blue-300 rounded-full transition-colors duration-200 disabled:opacity-50 border border-blue-200 dark:border-blue-800"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
