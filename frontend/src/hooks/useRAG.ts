import { useState, useCallback } from 'react';
import { QueryRequest, QueryResponse, HealthStatus, SystemStats } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

export const useRAG = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const query = useCallback(async (request: QueryRequest): Promise<QueryResponse | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`Query failed: ${response.statusText}`);
      }

      const data: QueryResponse = await response.json();
      return data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const checkHealth = useCallback(async (): Promise<HealthStatus | null> => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (!response.ok) {
        throw new Error(`Health check failed: ${response.statusText}`);
      }
      return await response.json();
    } catch (err) {
      console.error('Health check failed:', err);
      return null;
    }
  }, []);

  const getStats = useCallback(async (): Promise<SystemStats | null> => {
    try {
      const response = await fetch(`${API_BASE_URL}/stats`);
      if (!response.ok) {
        throw new Error(`Stats fetch failed: ${response.statusText}`);
      }
      return await response.json();
    } catch (err) {
      console.error('Stats fetch failed:', err);
      return null;
    }
  }, []);

  return {
    query,
    checkHealth,
    getStats,
    loading,
    error,
  };
};

export default useRAG;
