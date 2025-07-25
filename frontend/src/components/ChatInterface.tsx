import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Clock, TrendingUp, AlertCircle, Copy, ThumbsUp, ThumbsDown } from 'lucide-react';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: string;
  confidence?: number;
  responseTime?: number;
  isLoading?: boolean;
}

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
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
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
    if (!queryText || isLoading) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: queryText,
      timestamp: new Date().toISOString()
    };

    const loadingMessage: Message = {
      id: `loading-${Date.now()}`,
      type: 'assistant',
      content: 'Analiz ediliyor...',
      timestamp: new Date().toISOString(),
      isLoading: true
    };

    setMessages(prev => [...prev, userMessage, loadingMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: queryText,
          language: 'tr'
        }),
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        type: 'assistant',
        content: data.answer,
        timestamp: data.timestamp,
        confidence: data.confidence,
        responseTime: data.response_time
      };

      setMessages(prev => 
        prev.map(msg => 
          msg.id === loadingMessage.id ? assistantMessage : msg
        )
      );

    } catch (error) {
      console.error('Query error:', error);
      
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        type: 'assistant',
        content: `Üzgünüm, bir hata oluştu: ${error instanceof Error ? error.message : 'Bilinmeyen hata'}`,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => 
        prev.map(msg => 
          msg.id === loadingMessage.id ? errorMessage : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // TODO: Add toast notification
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('tr-TR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getConfidenceColor = (confidence?: number) => {
    if (!confidence) return 'text-gray-500';
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceLabel = (confidence?: number) => {
    if (!confidence) return '';
    if (confidence >= 0.8) return 'Yüksek güven';
    if (confidence >= 0.6) return 'Orta güven';
    return 'Düşük güven';
  };

  return (
    <div className={`flex flex-col h-full bg-gradient-to-br from-white via-blue-50/30 to-purple-50/30 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 ${className}`}>
      {/* Header */}
      <div className="flex-shrink-0 px-6 py-4 bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border-b border-gray-200/50 dark:border-gray-700/50 shadow-sm">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1">
            <h2 className="text-lg font-bold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
              Turkish Financial AI Assistant
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              AI destekli finansal doküman analizi
            </p>
          </div>
          <div className="flex items-center space-x-2 px-3 py-1.5 bg-green-50 dark:bg-green-900/20 rounded-full border border-green-200 dark:border-green-800">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm font-medium text-green-700 dark:text-green-300">Aktif</span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 ? (
          <div className="text-center py-16 relative">
            {/* Floating Background Elements */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
              <div className="absolute top-10 left-10 w-32 h-32 bg-gradient-to-r from-blue-400/20 to-purple-400/20 rounded-full blur-xl animate-pulse"></div>
              <div className="absolute top-20 right-20 w-24 h-24 bg-gradient-to-r from-pink-400/20 to-red-400/20 rounded-full blur-xl animate-pulse" style={{ animationDelay: '1s' }}></div>
              <div className="absolute bottom-20 left-1/4 w-40 h-40 bg-gradient-to-r from-purple-400/20 to-blue-400/20 rounded-full blur-xl animate-pulse" style={{ animationDelay: '2s' }}></div>
            </div>
            
            {/* Main Content */}
            <div className="relative z-10">
              <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-2xl animate-bounce">
                <Bot className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-3xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-3 animate-pulse">
                Türkiye Finansal Analizine Hoş Geldiniz
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-8 max-w-md mx-auto text-lg">
                BIST-100, hisse senetleri, ekonomik göstergeler ve VİOP hakkında detaylı analizler için sorularınızı sorabilirsiniz.
              </p>
              
              {/* Modern Feature Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-4xl mx-auto mb-8">
                <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-xl border border-blue-200/50 dark:border-blue-700/50 backdrop-blur-sm">
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <TrendingUp className="w-5 h-5 text-white" />
                  </div>
                  <h4 className="font-semibold text-blue-700 dark:text-blue-300 mb-2">BIST-100 Analizi</h4>
                  <p className="text-sm text-blue-600 dark:text-blue-400">Gerçek zamanlı borsa verileri ve trend analizi</p>
                </div>
                
                <div className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-xl border border-purple-200/50 dark:border-purple-700/50 backdrop-blur-sm">
                  <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <h4 className="font-semibold text-purple-700 dark:text-purple-300 mb-2">AI Destekli Analiz</h4>
                  <p className="text-sm text-purple-600 dark:text-purple-400">Gelişmiş yapay zeka ile finansal öngörüler</p>
                </div>
                
                <div className="p-4 bg-gradient-to-br from-pink-50 to-pink-100 dark:from-pink-900/20 dark:to-pink-800/20 rounded-xl border border-pink-200/50 dark:border-pink-700/50 backdrop-blur-sm">
                  <div className="w-10 h-10 bg-gradient-to-r from-pink-500 to-pink-600 rounded-lg flex items-center justify-center mx-auto mb-3">
                    <Clock className="w-5 h-5 text-white" />
                  </div>
                  <h4 className="font-semibold text-pink-700 dark:text-pink-300 mb-2">Anlık Raporlama</h4>
                  <p className="text-sm text-pink-600 dark:text-pink-400">Güncel finansal raporlar ve bulletinler</p>
                </div>
              </div>
              
              {/* Enhanced Suggestions */}
              <div className="max-w-3xl mx-auto">
                <p className="text-xl font-semibold bg-gradient-to-r from-gray-700 to-gray-500 dark:from-gray-300 dark:to-gray-500 bg-clip-text text-transparent mb-6">
                  ✨ Başlamak için bir soru seçin
                </p>
                <div className="grid gap-4">
                  {suggestions.slice(0, 3).map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSubmit(suggestion)}
                      className="group text-left p-6 bg-white/90 dark:bg-gray-800/90 backdrop-blur-md rounded-2xl hover:bg-white dark:hover:bg-gray-700 transition-all duration-300 shadow-lg hover:shadow-2xl transform hover:scale-105 border border-gray-200/50 dark:border-gray-700/50 hover:border-purple-300 dark:hover:border-purple-600"
                      disabled={isLoading}
                    >
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform duration-300">
                          <span className="text-white text-sm font-bold">{index + 1}</span>
                        </div>
                        <div className="flex-1">
                          <span className="text-gray-700 dark:text-gray-300 font-medium leading-relaxed">"{suggestion}"</span>
                          <div className="mt-2 flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400">
                            <span className="px-2 py-1 bg-gradient-to-r from-blue-100 to-purple-100 dark:from-blue-900/30 dark:to-purple-900/30 rounded-full">Popüler</span>
                            <span>• 2-3 saniye yanıt</span>
                          </div>
                        </div>
                        <div className="text-purple-500 group-hover:translate-x-1 transition-transform duration-300">
                          <Send size={20} />
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} transition-all duration-200 hover:scale-[1.02]`}
            >
              <div className={`flex space-x-3 max-w-4xl ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                {/* Avatar */}
                <div className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center shadow-lg ${
                  message.type === 'user' 
                    ? 'bg-gradient-to-r from-red-500 to-pink-600 text-white' 
                    : 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
                }`}>
                  {message.type === 'user' ? <User size={20} /> : <Bot size={20} />}
                </div>

                {/* Message Content */}
                <div className={`flex-1 ${message.type === 'user' ? 'text-right' : ''}`}>
                  <div className={`inline-block p-4 rounded-2xl shadow-lg backdrop-blur-md border border-gray-200/50 dark:border-gray-700/50 ${
                    message.type === 'user'
                      ? 'bg-gradient-to-r from-red-500 to-pink-600 text-white'
                      : 'bg-white/90 dark:bg-gray-800/90 text-gray-900 dark:text-white'
                  }`}>
                    {message.isLoading ? (
                      <div className="flex items-center space-x-3">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                          <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                          <div className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                        </div>
                        <span className="font-medium">AI analiz ediyor...</span>
                      </div>
                    ) : (
                      <div className="whitespace-pre-wrap leading-relaxed">{message.content}</div>
                    )}
                  </div>

                  {/* Message Metadata */}
                  <div className={`mt-2 flex items-center space-x-3 text-xs text-gray-500 dark:text-gray-400 ${
                    message.type === 'user' ? 'justify-end' : 'justify-start'
                  }`}>
                    <span className="flex items-center space-x-1 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded-full">
                      <Clock size={12} />
                      <span>{formatTimestamp(message.timestamp)}</span>
                    </span>
                    
                    {message.confidence && (
                      <span className={`flex items-center space-x-1 px-2 py-1 rounded-full ${
                        message.confidence >= 0.8 ? 'bg-green-100 text-green-700 dark:bg-green-900/20 dark:text-green-400' :
                        message.confidence >= 0.6 ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/20 dark:text-yellow-400' :
                        'bg-red-100 text-red-700 dark:bg-red-900/20 dark:text-red-400'
                      }`}>
                        <TrendingUp size={12} />
                        <span>{getConfidenceLabel(message.confidence)} ({(message.confidence * 100).toFixed(0)}%)</span>
                      </span>
                    )}
                    
                    {message.responseTime && (
                      <span className="flex items-center space-x-1 px-2 py-1 bg-blue-100 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400 rounded-full">
                        <span>⚡</span>
                        <span>{message.responseTime.toFixed(2)}s</span>
                      </span>
                    )}

                    {/* Action Buttons */}
                    {message.type === 'assistant' && !message.isLoading && (
                      <div className="flex items-center space-x-1">
                        <button
                          onClick={() => copyToClipboard(message.content)}
                          className="p-2 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
                          title="Kopyala"
                        >
                          <Copy size={14} />
                        </button>
                        <button
                          className="p-2 hover:bg-green-100 dark:hover:bg-green-900/20 rounded-lg transition-colors"
                          title="Beğen"
                        >
                          <ThumbsUp size={14} />
                        </button>
                        <button
                          className="p-2 hover:bg-red-100 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                          title="Beğenme"
                        >
                          <ThumbsDown size={14} />
                        </button>
                      </div>
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
      <div className="flex-shrink-0 p-6 bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border-t border-gray-200/50 dark:border-gray-700/50">
        <div className="flex space-x-3">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Türkiye finansal piyasası hakkında soru sorun... (Enter ile gönder)"
              className="w-full px-6 py-4 pr-16 border-2 border-gray-200 dark:border-gray-600 rounded-2xl focus:ring-4 focus:ring-purple-500/20 focus:border-purple-500 dark:focus:border-purple-400 transition-all duration-200 resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 shadow-lg"
              rows={1}
              style={{ minHeight: '60px', maxHeight: '120px' }}
              disabled={isLoading}
            />
            
            <button
              onClick={() => handleSubmit()}
              disabled={!input.trim() || isLoading}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-3 bg-gradient-to-r from-purple-500 to-pink-600 text-white rounded-xl hover:from-purple-600 hover:to-pink-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl hover:scale-105 disabled:hover:scale-100"
            >
              <Send size={20} />
            </button>
          </div>
        </div>
        
        {/* Enhanced Quick Suggestions */}
        {messages.length === 0 && (
          <div className="mt-6 p-4 bg-gradient-to-r from-blue-50/50 to-purple-50/50 dark:from-blue-900/10 dark:to-purple-900/10 rounded-2xl border border-blue-200/30 dark:border-blue-700/30 backdrop-blur-sm">
            <div className="flex items-center space-x-2 mb-3">
              <div className="w-5 h-5 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white text-xs">⚡</span>
              </div>
              <span className="text-sm font-semibold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Hızlı Başlangıç
              </span>
            </div>
            <div className="flex flex-wrap gap-2">
              {suggestions.slice(3).map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSubmit(suggestion)}
                  className="group px-4 py-2 text-sm bg-white/80 dark:bg-gray-800/80 backdrop-blur-md text-gray-700 dark:text-gray-300 rounded-xl hover:bg-gradient-to-r hover:from-blue-500 hover:to-purple-600 hover:text-white transition-all duration-300 border border-gray-200/50 dark:border-gray-600/50 shadow-sm hover:shadow-lg hover:scale-105 transform"
                  disabled={isLoading}
                >
                  <span className="group-hover:font-medium transition-all duration-300">{suggestion}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatInterface;
