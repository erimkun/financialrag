import axios, { AxiosResponse } from 'axios';

// API base URL - can be configured via environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for large file uploads
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth tokens if needed
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for handling common errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token');
      // Redirect to login if needed
    }
    return Promise.reject(error);
  }
);

// Types
export interface AnalysisResult {
  analysis_id: string;
  status: 'processing' | 'completed' | 'error';
  summary?: {
    document_info: any;
    pdf_content: any;
    chart_analysis: any;
    performance_stats: any;
  };
  details?: any;
  message?: string;
  confidence?: number;
  response_time?: number;
}

export interface QueryResponse {
  answer: string;
  confidence: number;
  response_time: number;
  document_id?: string;
  timestamp: string;
}

export interface Document {
  id: string;
  filename: string;
  size: number;
  pages?: number;
  processed_at: string;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  analysis_id?: string;
}

// API Service Class
class ApiService {
  // Upload PDF file for analysis
  async uploadPDF(file: File): Promise<AnalysisResult> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response: AxiosResponse<AnalysisResult> = await apiClient.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          console.log(`Upload Progress: ${percentCompleted}%`);
        }
      },
    });
    
    return response.data;
  }

  // Get analysis status by ID
  async getAnalysisStatus(analysisId: string): Promise<AnalysisResult> {
    const response: AxiosResponse<AnalysisResult> = await apiClient.get(`/status/${analysisId}`);
    return response.data;
  }

  // Query the RAG system
  async queryRAG(question: string, document_id?: string): Promise<QueryResponse> {
    const payload = {
      question,
      document_id,
      language: 'tr'
    };
    
    const response: AxiosResponse<QueryResponse> = await apiClient.post('/api/query', payload);
    return response.data;
  }

  // Get list of processed documents
  async getDocuments(): Promise<Document[]> {
    const response: AxiosResponse<Document[]> = await apiClient.get('/api/documents');
    return response.data;
  }

  // Delete a document and its analysis
  async deleteDocument(documentId: string): Promise<void> {
    await apiClient.delete(`/documents/${documentId}`);
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await apiClient.get('/api/health');
    return response.data;
  }

  // Get system metrics
  async getMetrics(): Promise<any> {
    const response = await apiClient.get('/api/stats');
    return response.data;
  }

  // Test connection to backend
  async testConnection(): Promise<boolean> {
    try {
      await this.healthCheck();
      return true;
    } catch (error) {
      console.error('Backend connection failed:', error);
      return false;
    }
  }
}

// Export singleton instance
export const apiService = new ApiService();

// Export individual methods for convenience
export const {
  uploadPDF,
  getAnalysisStatus,
  queryRAG,
  getDocuments,
  deleteDocument,
  healthCheck,
  getMetrics,
  testConnection,
} = apiService;

export default apiService;
