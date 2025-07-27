import { create } from 'zustand';
import { apiService, type Document, type AnalysisResult, type QueryResponse } from '../lib/api';

// Message type for chat
export interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: string;
  confidence?: number;
  responseTime?: number;
  isLoading?: boolean;
  sources?: Array<{
    content: string;
    page: number;
    type: string;
    similarity: number;
  }>;
}

// Upload status type
export interface UploadStatus {
  isUploading: boolean;
  progress: number;
  error?: string;
}

// App state interface
interface AppState {
  // Documents
  documents: Document[];
  selectedDocument: Document | null;
  
  // Chat
  messages: Message[];
  isLoadingResponse: boolean;
  
  // Upload
  uploadStatus: UploadStatus;
  
  // Connection
  isConnected: boolean;
  lastConnectionCheck: string | null;
  
  // Analysis
  currentAnalysis: AnalysisResult | null;
  
  // Actions
  setDocuments: (documents: Document[]) => void;
  setSelectedDocument: (document: Document | null) => void;
  addDocument: (document: Document) => void;
  removeDocument: (documentId: string) => void;
  updateDocument: (documentId: string, updates: Partial<Document>) => void;
  
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  updateMessage: (messageId: string, updates: Partial<Message>) => void;
  clearMessages: () => void;
  setLoadingResponse: (loading: boolean) => void;
  
  setUploadStatus: (status: Partial<UploadStatus>) => void;
  resetUploadStatus: () => void;
  
  setConnected: (connected: boolean) => void;
  setCurrentAnalysis: (analysis: AnalysisResult | null) => void;
  
  // Async actions
  uploadFile: (file: File) => Promise<void>;
  sendMessage: (content: string) => Promise<void>;
  loadDocuments: () => Promise<void>;
  checkConnection: () => Promise<boolean>;
  deleteDocument: (documentId: string) => Promise<void>;
}

export const useAppStore = create<AppState>((set, get) => ({
  // Initial state
  documents: [],
  selectedDocument: null,
  messages: [],
  isLoadingResponse: false,
  uploadStatus: { isUploading: false, progress: 0 },
  isConnected: false,
  lastConnectionCheck: null,
  currentAnalysis: null,

  // Document actions
  setDocuments: (documents) => set({ documents }),
  
  setSelectedDocument: (document) => set({ selectedDocument: document }),
  
  addDocument: (document) => set((state) => ({ 
    documents: [...state.documents, document] 
  })),
  
  removeDocument: (documentId) => set((state) => ({
    documents: state.documents.filter(doc => doc.id !== documentId),
    selectedDocument: state.selectedDocument?.id === documentId ? null : state.selectedDocument
  })),
  
  updateDocument: (documentId, updates) => set((state) => ({
    documents: state.documents.map(doc => 
      doc.id === documentId ? { ...doc, ...updates } : doc
    ),
    selectedDocument: state.selectedDocument?.id === documentId 
      ? { ...state.selectedDocument, ...updates } 
      : state.selectedDocument
  })),

  // Chat actions
  addMessage: (messageData) => {
    const message: Message = {
      ...messageData,
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString(),
    };
    set((state) => ({ messages: [...state.messages, message] }));
  },
  
  updateMessage: (messageId, updates) => set((state) => ({
    messages: state.messages.map(msg => 
      msg.id === messageId ? { ...msg, ...updates } : msg
    )
  })),
  
  clearMessages: () => set({ messages: [] }),
  
  setLoadingResponse: (loading) => set({ isLoadingResponse: loading }),

  // Upload actions
  setUploadStatus: (status) => set((state) => ({
    uploadStatus: { ...state.uploadStatus, ...status }
  })),
  
  resetUploadStatus: () => set({
    uploadStatus: { isUploading: false, progress: 0 }
  }),

  // Connection actions
  setConnected: (connected) => set({ 
    isConnected: connected,
    lastConnectionCheck: new Date().toISOString()
  }),
  
  setCurrentAnalysis: (analysis) => set({ currentAnalysis: analysis }),

  // Async actions
  uploadFile: async (file: File) => {
    const { setUploadStatus, addDocument, setCurrentAnalysis } = get();
    
    try {
      setUploadStatus({ isUploading: true, progress: 0, error: undefined });
      
      // Create temporary document
      const tempDoc: Document = {
        id: `temp_${Date.now()}`,
        filename: file.name,
        size: file.size,
        processed_at: new Date().toISOString(),
        status: 'uploading'
      };
      
      addDocument(tempDoc);
      setUploadStatus({ progress: 10 });
      
      // Upload file
      const result = await apiService.uploadPDF(file);
      setUploadStatus({ progress: 50 });
      
      // Update document with real data
      const updatedDoc: Document = {
        id: result.analysis_id,
        filename: file.name,
        size: file.size,
        processed_at: new Date().toISOString(),
        status: result.status === 'completed' ? 'completed' : 'processing'
      };
      
      set((state) => ({
        documents: state.documents.map(doc => 
          doc.id === tempDoc.id ? updatedDoc : doc
        )
      }));
      
      setCurrentAnalysis(result);
      setUploadStatus({ progress: 100, isUploading: false });
      
      // Auto-select the uploaded document
      get().setSelectedDocument(updatedDoc);
      
    } catch (error: any) {
      console.error('Upload failed:', error);
      setUploadStatus({ 
        isUploading: false, 
        progress: 0, 
        error: error.message || 'Upload failed' 
      });
      
      // Remove temp document on error
      set((state) => ({
        documents: state.documents.filter(doc => !doc.id.startsWith('temp_'))
      }));
    }
  },

  sendMessage: async (content: string) => {
    const { addMessage, setLoadingResponse, selectedDocument } = get();
    
    try {
      // Add user message
      addMessage({
        type: 'user',
        content
      });
      
      // Add loading assistant message
      const loadingMessageId = `msg_${Date.now()}_loading`;
      addMessage({
        type: 'assistant',
        content: '',
        isLoading: true
      });
      
      setLoadingResponse(true);
      
      const startTime = Date.now();
      
      // Send query to API
      const response = await apiService.queryRAG(
        content, 
        selectedDocument?.id
      );
      
      const responseTime = Date.now() - startTime;
      
      // Update loading message with actual response
      set((state) => ({
        messages: state.messages.map(msg => 
          msg.isLoading ? {
            ...msg,
            content: response.answer,
            confidence: response.confidence,
            responseTime: responseTime,
            isLoading: false
          } : msg
        )
      }));
      
    } catch (error: any) {
      console.error('Query failed:', error);
      
      // Update loading message with error
      set((state) => ({
        messages: state.messages.map(msg => 
          msg.isLoading ? {
            ...msg,
            content: `Üzgünüm, bir hata oluştu: ${error.message || 'Bilinmeyen hata'}`,
            isLoading: false
          } : msg
        )
      }));
    } finally {
      setLoadingResponse(false);
    }
  },

  loadDocuments: async () => {
    try {
      const documents = await apiService.getDocuments();
      set({ documents });
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  },

  checkConnection: async () => {
    const { setConnected } = get();
    try {
      const isConnected = await apiService.testConnection();
      setConnected(isConnected);
      return isConnected;
    } catch (error) {
      setConnected(false);
      return false;
    }
  },

  deleteDocument: async (documentId: string) => {
    const { removeDocument } = get();
    try {
      await apiService.deleteDocument(documentId);
      removeDocument(documentId);
    } catch (error) {
      console.error('Failed to delete document:', error);
      throw error;
    }
  }
}));

// Selector hooks for better performance
export const useDocuments = () => useAppStore(state => state.documents);
export const useSelectedDocument = () => useAppStore(state => state.selectedDocument);
export const useMessages = () => useAppStore(state => state.messages);
export const useUploadStatus = () => useAppStore(state => state.uploadStatus);
export const useConnectionStatus = () => useAppStore(state => state.isConnected);
export const useCurrentAnalysis = () => useAppStore(state => state.currentAnalysis);
